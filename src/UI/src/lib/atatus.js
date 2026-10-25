/**
 * Atatus Browser RUM & Browser Logs Bridge for StreamStorm UI
 * Connects directly to window.ATATUS_RUM and window.ATATUS_LOGS loaded from:
 * - https://js-cdn.atatus.io/atatus-browser-agent/latest/atatus-rum.js
 * - https://js-cdn.atatus.io/atatus-browser-agent/latest/atatus-logs.js
 *
 * Features:
 * - 100% full unmasked visibility with early-call queueing & auto-flush after init()
 * - Full Views, Actions, Resources, Errors, Timings, Duration Vitals, Operations API
 * - Identity (User & Account), Global Context, Feature Flags
 * - Session Replay links and controls
 * - Named Scoped Loggers (storm, environment, settings, ai, socket, server, system, validation, api, ui)
 * - Automatic fetch payload logging & unmasked DOM input change observers
 */

const isBrowser = typeof window !== 'undefined';

const getRumAgent = () => isBrowser ? (window.atatusRum || window.ATATUS_RUM || null) : null;
const getLogsAgent = () => isBrowser ? (window.atatusLogs || window.ATATUS_LOGS || null) : null;

function isRumReady() {
    const rum = getRumAgent();
    return Boolean(
        isBrowser &&
        rum &&
        typeof rum.addAction === 'function'
    );
}

function isLogsReady() {
    const logs = getLogsAgent();
    return Boolean(
        isBrowser &&
        logs &&
        (logs.logger || typeof logs.createLogger === 'function')
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
                console.error('[Atatus RUM Queue Error]', err);
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
                console.error('[Atatus Logs Queue Error]', err);
            }
        }
    };

    // Periodic check to auto-flush once GTM initializes ATATUS_RUM and ATATUS_LOGS
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
        } catch (err) {
            console.error('[Atatus RUM Error]', err);
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
        } catch (err) {
            console.error('[Atatus Logs Error]', err);
        }
    } else {
        window.__ATATUS_LOGS_QUEUE__.push(callback);
    }
}

// ==========================================
// VIEWS API
// ==========================================
export const startView = (name) => withRum((rum) => rum.startView?.(name));
export const setViewName = (name) => withRum((rum) => rum.setViewName?.(name));
export const setViewContext = (context) => withRum((rum) => rum.setViewContext?.(context));
export const setViewContextProperty = (key, value) => withRum((rum) => rum.setViewContextProperty?.(key, value));
export const setViewLoadingTime = () => withRum((rum) => rum.setViewLoadingTime?.());

// ==========================================
// ACTIONS & RESOURCES API
// ==========================================
export const addAction = (name, context = {}) => withRum((rum) => rum.addAction?.(name, context));
export const startAction = (name, options) => withRum((rum) => rum.startAction?.(name, options));
export const stopAction = (name, options) => withRum((rum) => rum.stopAction?.(name, options));
export const startResource = (url, options) => withRum((rum) => rum.startResource?.(url, options));
export const stopResource = (url, options) => withRum((rum) => rum.stopResource?.(url, options));

// ==========================================
// ERRORS, TIMINGS & DURATION VITALS API
// ==========================================
export const addError = (error, context = {}) => {
    withRum((rum) => {
        const replayLink = rum.getSessionReplayLink?.();
        const internalContext = rum.getInternalContext?.();
        const enrichedContext = {
            ...context,
            ...(replayLink && { sessionReplayUrl: replayLink }),
            ...(internalContext && { internalContext }),
        };
        const errObj = error instanceof Error ? error : new Error(typeof error === 'string' ? error : JSON.stringify(error));
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

export const addTiming = (name, time) => withRum((rum) => rum.addTiming?.(name, time));
export const addDurationVital = (name, options) => withRum((rum) => rum.addDurationVital?.(name, options));
export const startDurationVital = (name, options) => withRum((rum) => rum.startDurationVital?.(name, options));
export const stopDurationVital = (name, options) => withRum((rum) => rum.stopDurationVital?.(name, options));

// ==========================================
// OPERATIONS API
// ==========================================
export const startOperation = (name, options) => withRum((rum) => rum.startOperation?.(name, options));
export const succeedOperation = (name, options) => withRum((rum) => rum.succeedOperation?.(name, options));
export const failOperation = (name, reason, options) => withRum((rum) => rum.failOperation?.(name, reason, options));
export const startFeatureOperation = (name, options) => withRum((rum) => rum.startFeatureOperation?.(name, options));

// ==========================================
// IDENTITY (USER & ACCOUNT) API
// ==========================================
export const setUser = (user) => {
    withRum((rum) => rum.setUser?.(user));
    withLogs((logs) => logs.setUser?.(user));
};
export const getUser = () => (isBrowser && getRumAgent()?.getUser?.()) || null;
export const setUserProperty = (key, value) => withRum((rum) => rum.setUserProperty?.(key, value));
export const removeUserProperty = (key) => withRum((rum) => rum.removeUserProperty?.(key));
export const clearUser = () => {
    withRum((rum) => rum.clearUser?.());
    withLogs((logs) => logs.setUser?.({ id: 'anonymous' }));
};

export const setAccount = (account) => {
    withRum((rum) => rum.setAccount?.(account));
    withLogs((logs) => logs.setAccount?.(account));
};
export const getAccount = () => (isBrowser && getRumAgent()?.getAccount?.()) || null;
export const setAccountProperty = (key, value) => withRum((rum) => rum.setAccountProperty?.(key, value));
export const removeAccountProperty = (key) => withRum((rum) => rum.removeAccountProperty?.(key));
export const clearAccount = () => withRum((rum) => rum.clearAccount?.());

// ==========================================
// GLOBAL CONTEXT & FEATURE FLAGS API
// ==========================================
export const setGlobalContext = (context) => {
    withRum((rum) => rum.setGlobalContext?.(context));
    withLogs((logs) => logs.setGlobalContext?.(context));
};
export const getGlobalContext = () => (isBrowser && getRumAgent()?.getGlobalContext?.()) || {};
export const setGlobalContextProperty = (key, value) => {
    withRum((rum) => rum.setGlobalContextProperty?.(key, value));
    withLogs((logs) => logs.setGlobalContextProperty?.(key, value));
};
export const removeGlobalContextProperty = (key) => withRum((rum) => rum.removeGlobalContextProperty?.(key));
export const clearGlobalContext = () => {
    withRum((rum) => rum.setGlobalContext?.({}));
    withLogs((logs) => logs.clearGlobalContext?.());
};
export const addFeatureFlagEvaluation = (key, value) => withRum((rum) => rum.addFeatureFlagEvaluation?.(key, value));

// ==========================================
// SESSION REPLAY & DIAGNOSTICS API
// ==========================================
export const startSessionReplayRecording = () => withRum((rum) => rum.startSessionReplayRecording?.());
export const stopSessionReplayRecording = () => withRum((rum) => rum.stopSessionReplayRecording?.());
export const getSessionReplayLink = () => (isBrowser && getRumAgent()?.getSessionReplayLink?.()) || null;
export const getReplayLink = getSessionReplayLink;
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

// Pre-defined scoped loggers for each major UI area
export const stormLogger = createScopedLogger('storm');
export const envLogger = createScopedLogger('environment');
export const settingsLogger = createScopedLogger('settings');
export const aiLogger = createScopedLogger('ai');
export const socketLogger = createScopedLogger('socket');
export const serverLogger = createScopedLogger('server');
export const systemLogger = createScopedLogger('system');
export const validationLogger = createScopedLogger('validation');
export const apiLogger = createScopedLogger('api');
export const uiLogger = createScopedLogger('ui');

// Default general logger
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

    // 1. Transparent Fetch Observer: Logs full API request/response payloads to apiLogger
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        const startTime = Date.now();
        const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || 'unknown-url');
        const options = args[1] || {};
        const method = options.method || (args[0]?.method) || 'GET';
        let reqBody = options.body;
        if (typeof reqBody === 'string') {
            try { reqBody = JSON.parse(reqBody); } catch (_) {}
        }

        try {
            const response = await originalFetch.apply(this, args);
            const duration = Date.now() - startTime;
            const clone = response.clone();

            // Clone JSON response for observability logging without consuming stream
            clone.json().then((json) => {
                apiLogger.debug(`${method} ${url} -> ${response.status} (${duration}ms)`, {
                    method,
                    url,
                    status: response.status,
                    duration,
                    request: reqBody,
                    response: json,
                });
            }).catch(() => {
                apiLogger.debug(`${method} ${url} -> ${response.status} (${duration}ms)`, {
                    method,
                    url,
                    status: response.status,
                    duration,
                });
            });

            return response;
        } catch (error) {
            const duration = Date.now() - startTime;
            apiLogger.error(`${method} ${url} FAILED (${duration}ms)`, {
                method,
                url,
                duration,
                request: reqBody,
            }, error);
            throw error;
        }
    };

    // 2. Global Unmasked Input Change Observer: Logs all user inputs across textfields, checkboxes, switches, selects
    document.addEventListener('change', (e) => {
        try {
            const target = e.target;
            if (!target) return;
            const tag = target.tagName?.toLowerCase();
            if (tag === 'input' || tag === 'textarea' || tag === 'select') {
                const name = target.name || target.id || target.getAttribute('aria-label') || target.placeholder || 'unnamed-input';
                const type = target.type || tag;
                const value = type === 'checkbox' ? target.checked : target.value;
                addAction('input-changed', { field: name, type, value });
                uiLogger.debug(`Input changed: ${name}`, { field: name, type, value });
            }
        } catch (_) {}
    }, true);
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
    getInitConfiguration,
    getInternalContext,
    getLogsInitConfiguration,
    getLogsInternalContext,
    setTrackingConsent,
    createScopedLogger,
    stormLogger,
    envLogger,
    settingsLogger,
    aiLogger,
    socketLogger,
    serverLogger,
    systemLogger,
    validationLogger,
    apiLogger,
    uiLogger,
    logger,
    installGlobalObservers,
};
