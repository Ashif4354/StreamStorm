/**
 * Atatus Browser RUM & Browser Logs Bridge for StreamStorm Site (Next.js App Router)
 * Connects to the documented `atatusRum` API or the existing GTM bridge globals:
 * - https://js-cdn.atatus.io/atatus-browser-agent/latest/atatus-rum.js
 * - https://js-cdn.atatus.io/atatus-browser-agent/latest/atatus-logs.js
 *
 * Features:
 * - SSR-safe for Next.js App Router
 * - Early-call queueing and auto-flush after agent initialization
 * - Full Views, Actions, Resources, Errors, Timings, Duration Vitals, Operations API
 * - Identity (User & Account), Global Context, Feature Flags
 * - Session Replay links and controls
 * - Named Scoped Loggers (site, downloads, visits, navigation, ui, api)
 * - Redacted fetch/input telemetry, private replay fields, and outbound/download link observer
 */

import {
    isSensitiveInput,
    installConsoleRedaction,
    markInputsPrivate,
    sanitizeTelemetry,
    sanitizeTelemetryString,
    sanitizeTelemetryUrl,
} from './telemetryRedaction';

const isBrowser = typeof window !== 'undefined';

// The documented SDK exports `atatusRum`; retain the uppercase bridge as a
// compatibility path for an existing GTM container during deployment migration.
const getRumAgent = () => isBrowser ? (window.atatusRum || window.ATATUS_RUM || null) : null;
const getLogsAgent = () => isBrowser ? (window.atatusLogs || window.ATATUS_LOGS || null) : null;

function isRumReady() {
    return Boolean(
        isBrowser &&
        getRumAgent() &&
        typeof getRumAgent().addAction === 'function'
    );
}

function isLogsReady() {
    return Boolean(
        isBrowser &&
        getLogsAgent() &&
        (getLogsAgent().logger || typeof getLogsAgent().createLogger === 'function')
    );
}

if (isBrowser) {
    window.__ATATUS_RUM_QUEUE__ = window.__ATATUS_RUM_QUEUE__ || [];
    window.__ATATUS_LOGS_QUEUE__ = window.__ATATUS_LOGS_QUEUE__ || [];

    window.__flushAtatusRumQueue = function () {
        if (!getRumAgent() || !window.__ATATUS_RUM_QUEUE__) return;
        while (window.__ATATUS_RUM_QUEUE__.length > 0) {
            const task = window.__ATATUS_RUM_QUEUE__.shift();
            try {
                task(getRumAgent());
            } catch (err) {
                console.error('[Atatus Site RUM Queue Error] A queued telemetry call failed.');
            }
        }
    };

    window.__flushAtatusLogsQueue = function () {
        if (!getLogsAgent() || !window.__ATATUS_LOGS_QUEUE__) return;
        while (window.__ATATUS_LOGS_QUEUE__.length > 0) {
            const task = window.__ATATUS_LOGS_QUEUE__.shift();
            try {
                task(getLogsAgent());
            } catch (err) {
                console.error('[Atatus Site Logs Queue Error] A queued telemetry call failed.');
            }
        }
    };

    // Periodic check to auto-flush once the Atatus agents are available.
    let checkCount = 0;
    const flushInterval = setInterval(() => {
        checkCount++;
        if (isRumReady() && window.__ATATUS_RUM_QUEUE__?.length) {
            window.__flushAtatusRumQueue();
        }
        if (isLogsReady() && window.__ATATUS_LOGS_QUEUE__?.length) {
            window.__flushAtatusLogsQueue();
        }
        if (
            checkCount > 60 ||
            (isRumReady() && isLogsReady() && !window.__ATATUS_RUM_QUEUE__?.length && !window.__ATATUS_LOGS_QUEUE__?.length)
        ) {
            clearInterval(flushInterval);
        }
    }, 250);
}

function withRum(callback) {
    if (!isBrowser) return;
    if (isRumReady()) {
        try {
            return callback(getRumAgent());
        } catch {
            console.error('[Atatus Site RUM Error] Telemetry was dropped after sanitization failed.');
        }
    } else {
        window.__ATATUS_RUM_QUEUE__.push(callback);
    }
}

function withLogs(callback) {
    if (!isBrowser) return;
    if (isLogsReady()) {
        try {
            return callback(getLogsAgent());
        } catch {
            console.error('[Atatus Site Logs Error] Telemetry was dropped after sanitization failed.');
        }
    } else {
        window.__ATATUS_LOGS_QUEUE__.push(callback);
    }
}

// ==========================================
// VIEWS API
// ==========================================
export const startView = (name) => withRum((rum) => rum.startView?.(sanitizeTelemetryString(name)));
export const setViewName = (name) => withRum((rum) => rum.setViewName?.(sanitizeTelemetryString(name)));
export const setViewContext = (context) => withRum((rum) => rum.setViewContext?.(sanitizeTelemetry(context)));
export const setViewContextProperty = (key, value) => withRum((rum) => rum.setViewContextProperty?.(sanitizeTelemetryString(key), sanitizeTelemetry(value)));
export const setViewLoadingTime = () => withRum((rum) => rum.setViewLoadingTime?.());

// ==========================================
// ACTIONS & RESOURCES API
// ==========================================
export const addAction = (name, context = {}) => withRum((rum) => rum.addAction?.(sanitizeTelemetryString(name), sanitizeTelemetry(context)));
export const startAction = (name, options) => withRum((rum) => rum.startAction?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));
export const stopAction = (name, options) => withRum((rum) => rum.stopAction?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));
export const startResource = (url, options) => withRum((rum) => rum.startResource?.(sanitizeTelemetryUrl(url), sanitizeTelemetry(options)));
export const stopResource = (url, options) => withRum((rum) => rum.stopResource?.(sanitizeTelemetryUrl(url), sanitizeTelemetry(options)));

// ==========================================
// ERRORS, TIMINGS & DURATION VITALS API
// ==========================================
export const addError = (error, context = {}) => {
    withRum((rum) => {
        const replayLink = rum.getSessionReplayLink?.();
        const internalContext = rum.getInternalContext?.();
        const enrichedContext = sanitizeTelemetry({
            ...context,
            ...(replayLink && { sessionReplayUrl: replayLink }),
            ...(internalContext && { internalContext }),
        });
        const errObj = error instanceof Error
            ? sanitizeTelemetry(error)
            : new Error(sanitizeTelemetryString(typeof error === 'string' ? error : JSON.stringify(sanitizeTelemetry(error))));
        rum.addError?.(errObj, enrichedContext);
    });
};

// Legacy alias to seamlessly replace `atatus.notify`
export const notify = (error, context = {}, tags = []) => {
    const customContext = { ...context };
    if (tags && tags.length > 0) {
        customContext.tags = tags;
    }
    addError(error, customContext);
};

export const addTiming = (name, time) => withRum((rum) => rum.addTiming?.(sanitizeTelemetryString(name), time));
export const addDurationVital = (name, options) => withRum((rum) => rum.addDurationVital?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));
export const startDurationVital = (name, options) => withRum((rum) => rum.startDurationVital?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));
export const stopDurationVital = (name, options) => withRum((rum) => rum.stopDurationVital?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));

// ==========================================
// OPERATIONS API
// ==========================================
export const startOperation = (name, options) => withRum((rum) => rum.startOperation?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));
export const succeedOperation = (name, options) => withRum((rum) => rum.succeedOperation?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));
export const failOperation = (name, reason, options) => withRum((rum) => rum.failOperation?.(sanitizeTelemetryString(name), sanitizeTelemetryString(reason), sanitizeTelemetry(options)));
export const startFeatureOperation = (name, options) => withRum((rum) => rum.startFeatureOperation?.(sanitizeTelemetryString(name), sanitizeTelemetry(options)));

// ==========================================
// IDENTITY (USER & ACCOUNT) API
// ==========================================
export const setUser = (user) => {
    try {
        const safeUser = sanitizeTelemetry(user);
        withRum((rum) => rum.setUser?.(safeUser));
        withLogs((logs) => logs.setUser?.(safeUser));
    } catch { /* Drop telemetry if sanitization fails; do not affect app behavior. */ }
};
export const getUser = () => (isBrowser && getRumAgent()?.getUser?.()) || null;
export const setUserProperty = (key, value) => withRum((rum) => rum.setUserProperty?.(sanitizeTelemetryString(key), sanitizeTelemetry(value)));
export const removeUserProperty = (key) => withRum((rum) => rum.removeUserProperty?.(key));
export const clearUser = () => {
    withRum((rum) => rum.clearUser?.());
    withLogs((logs) => logs.setUser?.({ id: 'anonymous' }));
};

export const setAccount = (account) => {
    try {
        const safeAccount = sanitizeTelemetry(account);
        withRum((rum) => rum.setAccount?.(safeAccount));
        withLogs((logs) => logs.setAccount?.(safeAccount));
    } catch { /* Drop telemetry if sanitization fails; do not affect app behavior. */ }
};
export const getAccount = () => (isBrowser && getRumAgent()?.getAccount?.()) || null;
export const setAccountProperty = (key, value) => withRum((rum) => rum.setAccountProperty?.(sanitizeTelemetryString(key), sanitizeTelemetry(value)));
export const removeAccountProperty = (key) => withRum((rum) => rum.removeAccountProperty?.(key));
export const clearAccount = () => withRum((rum) => rum.clearAccount?.());

// ==========================================
// GLOBAL CONTEXT & FEATURE FLAGS API
// ==========================================
export const setGlobalContext = (context) => {
    try {
        const safeContext = sanitizeTelemetry(context);
        withRum((rum) => rum.setGlobalContext?.(safeContext));
        withLogs((logs) => logs.setGlobalContext?.(safeContext));
    } catch { /* Drop telemetry if sanitization fails; do not affect app behavior. */ }
};
export const getGlobalContext = () => (isBrowser && getRumAgent()?.getGlobalContext?.()) || {};
export const setGlobalContextProperty = (key, value) => {
    try {
        const safeKey = sanitizeTelemetryString(key);
        const safeValue = sanitizeTelemetry(value);
        withRum((rum) => rum.setGlobalContextProperty?.(safeKey, safeValue));
        withLogs((logs) => logs.setGlobalContextProperty?.(safeKey, safeValue));
    } catch { /* Drop telemetry if sanitization fails; do not affect app behavior. */ }
};
export const removeGlobalContextProperty = (key) => withRum((rum) => rum.removeGlobalContextProperty?.(key));
export const clearGlobalContext = () => {
    withRum((rum) => rum.setGlobalContext?.({}));
    withLogs((logs) => logs.clearGlobalContext?.());
};
export const addFeatureFlagEvaluation = (key, value) => withRum((rum) => rum.addFeatureFlagEvaluation?.(sanitizeTelemetryString(key), sanitizeTelemetry(value)));

// ==========================================
// SESSION REPLAY & DIAGNOSTICS API
// ==========================================
export const startSessionReplayRecording = () => withRum((rum) => rum.startSessionReplayRecording?.());
export const stopSessionReplayRecording = () => withRum((rum) => rum.stopSessionReplayRecording?.());
export const getSessionReplayLink = () => (isBrowser && getRumAgent()?.getSessionReplayLink?.()) || null;
export const getReplayLink = getSessionReplayLink;
export const startReplay = startSessionReplayRecording;
export const stopReplay = stopSessionReplayRecording;
export const getInitConfiguration = () => (isBrowser && getRumAgent()?.getInitConfiguration?.()) || null;
export const getInternalContext = () => (isBrowser && getRumAgent()?.getInternalContext?.()) || null;
export const getLogsInitConfiguration = () => (isBrowser && getLogsAgent()?.getInitConfiguration?.()) || null;
export const getLogsInternalContext = () => (isBrowser && getLogsAgent()?.getInternalContext?.()) || null;
export const setTrackingConsent = (consent) => withRum((rum) => rum.setTrackingConsent?.(consent));

// ==========================================
// SCOPED LOGGERS (ATATUS BROWSER LOGS)
// ==========================================
const loggersCache = new Map();

export const createScopedLogger = (scope, level = 'debug') => {
    if (loggersCache.has(scope)) {
        return loggersCache.get(scope);
    }

    const levels = ['ok', 'debug', 'info', 'notice', 'warn', 'error', 'critical', 'alert', 'emerg'];
    const loggerObj = {};

    levels.forEach((lvl) => {
        loggerObj[lvl] = (message, context = {}, err = null) => {
            withLogs((logs) => {
                let scopedLogger = logs.getLogger ? logs.getLogger(scope) : null;
                if (!scopedLogger && logs.createLogger) {
                    scopedLogger = logs.createLogger(scope, { level });
                }
                const target = scopedLogger || logs.logger;
                if (target && typeof target[lvl] === 'function') {
                    if (err) {
                        target[lvl](`[${scope}] ${message}`, context, err);
                    } else {
                        target[lvl](`[${scope}] ${message}`, context);
                    }
                }
            });
        };
    });

    loggerObj.setLevel = (newLevel) => {
        withLogs((logs) => {
            const l = logs.getLogger ? logs.getLogger(scope) : logs.logger;
            l?.setLevel?.(newLevel);
        });
    };

    loggersCache.set(scope, loggerObj);
    return loggerObj;
};

export const siteLogger = createScopedLogger('site');
export const downloadLogger = createScopedLogger('downloads');
export const visitLogger = createScopedLogger('visits');
export const navLogger = createScopedLogger('navigation');
export const uiLogger = createScopedLogger('ui');
export const apiLogger = createScopedLogger('api');

export const logger = {
    ok: (msg, ctx, err) => withLogs((logs) => logs.logger?.ok?.(msg, ctx, err)),
    debug: (msg, ctx, err) => withLogs((logs) => logs.logger?.debug?.(msg, ctx, err)),
    info: (msg, ctx, err) => withLogs((logs) => logs.logger?.info?.(msg, ctx, err)),
    notice: (msg, ctx, err) => withLogs((logs) => logs.logger?.notice?.(msg, ctx, err)),
    warn: (msg, ctx, err) => withLogs((logs) => logs.logger?.warn?.(msg, ctx, err)),
    error: (msg, ctx, err) => withLogs((logs) => logs.logger?.error?.(msg, ctx, err)),
    critical: (msg, ctx, err) => withLogs((logs) => logs.logger?.critical?.(msg, ctx, err)),
    alert: (msg, ctx, err) => withLogs((logs) => logs.logger?.alert?.(msg, ctx, err)),
    emerg: (msg, ctx, err) => withLogs((logs) => logs.logger?.emerg?.(msg, ctx, err)),
    setLevel: (lvl) => withLogs((logs) => logs.logger?.setLevel?.(lvl)),
};

// ==========================================
// AUTOMATIC GLOBAL OBSERVERS
// ==========================================
let observersInstalled = false;

export const installGlobalObservers = () => {
    if (!isBrowser || observersInstalled) return;
    observersInstalled = true;
    installConsoleRedaction();

    setGlobalContextProperty('appName', 'StreamStormSite');
    setGlobalContextProperty('version', '4.2.0');

    // 1. Fetch observer: retain JSON diagnostics after credential redaction.
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        const startTime = Date.now();
        let url = null;
        try {
            url = sanitizeTelemetryUrl(typeof args[0] === 'string' ? args[0] : (args[0]?.url || 'unknown-url'));
        } catch { /* Do not emit telemetry for URLs that cannot be safely redacted. */ }
        const options = args[1] || {};
        const method = options.method || (args[0]?.method) || 'GET';
        let reqBody = options.body;
        try {
            if (typeof reqBody === 'string') {
                try { reqBody = JSON.parse(reqBody); } catch (_) { reqBody = sanitizeTelemetryString(reqBody); }
            }
            reqBody = sanitizeTelemetry(reqBody);
        } catch {
            reqBody = undefined;
        }

        try {
            const response = await originalFetch.apply(this, args);
            const duration = Date.now() - startTime;
            if (!url) return response;
            const clone = response.clone();

            clone.json().then((json) => {
                let safeResponse;
                try { safeResponse = sanitizeTelemetry(json); } catch { return; }
                apiLogger.debug(`${method} ${url} -> ${response.status} (${duration}ms)`, {
                    method,
                    url,
                    status: response.status,
                    duration,
                    ...(reqBody !== undefined && { request: reqBody }),
                    response: safeResponse,
                });
            }).catch(() => {
                if (url) apiLogger.debug(`${method} ${url} -> ${response.status} (${duration}ms)`, { method, url, status: response.status, duration });
            });

            return response;
        } catch (error) {
            const duration = Date.now() - startTime;
            if (url) {
                try {
                    apiLogger.error(`${method} ${url} FAILED (${duration}ms)`, {
                        method,
                        url,
                        duration,
                        ...(reqBody !== undefined && { request: reqBody }),
                    }, sanitizeTelemetry(error));
                } catch { /* Redaction failures fail closed; the original request still rejects. */ }
            }
            throw error;
        }
    };

    // Mask editable fields before replay snapshots, including controls added after mount.
    markInputsPrivate(document);
    const privateInputObserver = new MutationObserver((records) => {
        for (const record of records) for (const node of record.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) markInputsPrivate(node);
        }
    });
    privateInputObserver.observe(document.documentElement, { childList: true, subtree: true });

    // 2. Input observer: keep field metadata but never emit credential values.
    document.addEventListener('change', (e) => {
        try {
            const target = e.target;
            if (!target) return;
            const tag = target.tagName?.toLowerCase();
            if (tag === 'input' || tag === 'textarea' || tag === 'select') {
                const name = target.name || target.id || target.getAttribute('aria-label') || target.placeholder || 'unnamed-input';
                const type = target.type || tag;
                const value = isSensitiveInput(target)
                    ? '[REDACTED]'
                    : sanitizeTelemetry(target.type === 'checkbox' ? target.checked : target.value);
                addAction('input-changed', { field: name, type, value });
                uiLogger.debug(`Input changed: ${name}`, { field: name, type, value });
            }
        } catch (_) {}
    }, true);

    // 3. Outbound & Download Link Observer
    document.addEventListener('click', (e) => {
        try {
            const anchor = e.target?.closest?.('a');
            if (anchor && anchor.href) {
                const safeHref = sanitizeTelemetryUrl(anchor.href);
                const url = new URL(safeHref, window.location.href);
                const isOutbound = url.origin !== window.location.origin;
                const isDownload = anchor.hasAttribute('download') || /\.(exe|deb|rpm|dmg|tar\.gz|zip)$/i.test(url.pathname);

                if (isDownload) {
                    addAction('file-download-clicked', {
                        href: safeHref,
                        text: anchor.innerText?.trim() || '',
                        path: url.pathname,
                    });
                    downloadLogger.info(`Download clicked: ${url.pathname}`, { href: safeHref });
                } else if (isOutbound) {
                    addAction('outbound-link-clicked', {
                        href: safeHref,
                        host: url.host,
                        text: anchor.innerText?.trim() || '',
                    });
                    navLogger.info(`Outbound link clicked: ${url.host}`, { href: safeHref });
                }
            }
        } catch (_) {}
    }, { capture: true, passive: true });
};

export default {
    startView,
    setViewName,
    setViewContext,
    setViewContextProperty,
    setViewLoadingTime,
    addAction,
    startAction,
    stopAction,
    startResource,
    stopResource,
    addError,
    notify,
    addTiming,
    addDurationVital,
    startDurationVital,
    stopDurationVital,
    startOperation,
    succeedOperation,
    failOperation,
    startFeatureOperation,
    setUser,
    getUser,
    setUserProperty,
    removeUserProperty,
    clearUser,
    setAccount,
    getAccount,
    setAccountProperty,
    removeAccountProperty,
    clearAccount,
    setGlobalContext,
    getGlobalContext,
    setGlobalContextProperty,
    removeGlobalContextProperty,
    clearGlobalContext,
    addFeatureFlagEvaluation,
    startSessionReplayRecording,
    stopSessionReplayRecording,
    getSessionReplayLink,
    getReplayLink,
    startReplay,
    stopReplay,
    getInitConfiguration,
    getInternalContext,
    getLogsInitConfiguration,
    getLogsInternalContext,
    setTrackingConsent,
    createScopedLogger,
    siteLogger,
    downloadLogger,
    visitLogger,
    navLogger,
    uiLogger,
    apiLogger,
    logger,
    installGlobalObservers,
};
