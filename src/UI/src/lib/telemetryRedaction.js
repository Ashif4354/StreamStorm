const SECRET_KEY = /(?:password|passwd|pwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|client[\s_-]?secret|access[\s_-]?key|refresh[\s_-]?token|session[\s_-]?id|csrf|xsrf)/i;
const SECRET_ASSIGNMENT_QUOTED = /(["']?(?:password|passwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|client[\s_-]?secret|access[\s_-]?key|refresh[\s_-]?token)["']?\s*[:=]\s*["'])([^"']*)(["'])/gi;
const SECRET_ASSIGNMENT = /(["']?(?:password|passwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|client[\s_-]?secret|access[\s_-]?key|refresh[\s_-]?token)["']?\s*[:=]\s*)[^\s"'&,;}]+/gi;
const QUERY_SECRET = /([?#&](?:password|passwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|access[\s_-]?key|refresh[\s_-]?token)=)[^&#\s]*/gi;
const SECRET_HEADER = /((?:^|\r?\n)\s*(?:cookie|set-cookie|authorization|proxy-authorization|x-api-key|api-key)\s*:\s*)[^\r\n]*/gi;
const KNOWN_COOKIE_VALUE = /((?:__Secure-[A-Za-z0-9_-]+|__Host-[A-Za-z0-9_-]+|SID|HSID|SSID|APISID|SAPISID|LOGIN_INFO|PREF|YSC|VISITOR_INFO1_LIVE|VISITOR_PRIVACY_METADATA|CONSENT|NID)=)[^;,\s]*/gi;
const BEARER = /\b(Bearer|Basic)\s+[A-Za-z0-9._~+/-]+=*/gi;
const JWT = /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b/g;
const PROVIDER_KEYS = /\b(?:sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{30,}|gh[pousr]_[A-Za-z0-9_]{20,}|ya29\.[A-Za-z0-9_-]{20,})\b/g;
const REDACTED = '[REDACTED]';

export const isSensitiveTelemetryKey = (key = '') => SECRET_KEY.test(String(key));

export function sanitizeTelemetryString(value) {
    return String(value)
        .replace(BEARER, `$1 ${REDACTED}`)
        .replace(SECRET_HEADER, `$1${REDACTED}`)
        .replace(KNOWN_COOKIE_VALUE, `$1${REDACTED}`)
        .replace(SECRET_ASSIGNMENT_QUOTED, `$1${REDACTED}$3`)
        .replace(SECRET_ASSIGNMENT, `$1${REDACTED}`)
        .replace(QUERY_SECRET, `$1${REDACTED}`)
        .replace(JWT, REDACTED)
        .replace(PROVIDER_KEYS, REDACTED);
}

function sanitizeValue(value, key = '', seen = new WeakSet(), insideCookie = false) {
    if (isSensitiveTelemetryKey(key) || insideCookie) return REDACTED;
    if (value == null || typeof value === 'boolean' || typeof value === 'number') return value;
    if (typeof value === 'string') return sanitizeTelemetryString(value);
    if (typeof value === 'bigint') return String(value);
    if (typeof value === 'function' || typeof value === 'symbol') return '[OMITTED]';
    if (typeof Node !== 'undefined' && value instanceof Node) return '[DOM OMITTED]';
    if (typeof File !== 'undefined' && value instanceof File) return '[FILE OMITTED]';
    if (typeof Blob !== 'undefined' && value instanceof Blob) return '[BLOB OMITTED]';
    if (seen.has(value)) return '[CIRCULAR]';
    seen.add(value);

    if (typeof FormData !== 'undefined' && value instanceof FormData) {
        const result = {};
        for (const [entryKey, entryValue] of value.entries()) {
            const safeKey = sanitizeTelemetryString(entryKey);
            const safeValue = sanitizeValue(entryValue, entryKey, seen, isSensitiveTelemetryKey(entryKey));
            result[safeKey] = Object.hasOwn(result, safeKey) ? [...[].concat(result[safeKey]), safeValue] : safeValue;
        }
        return result;
    }
    if (Array.isArray(value)) return value.map((item) => sanitizeValue(item, key, seen, insideCookie));
    if (value instanceof Error) {
        const safeError = new Error(sanitizeTelemetryString(value.message));
        safeError.name = sanitizeTelemetryString(value.name);
        if (value.stack) safeError.stack = sanitizeTelemetryString(value.stack);
        if (value.cause !== undefined) safeError.cause = sanitizeValue(value.cause, 'cause', seen);
        return safeError;
    }

    const cookieObject = ('name' in value && 'value' in value && ('domain' in value || 'path' in value));
    const result = {};
    for (const [entryKey, entryValue] of Object.entries(value)) {
        const cookieField = insideCookie || (cookieObject && entryKey === 'value');
        result[sanitizeTelemetryString(entryKey)] = sanitizeValue(entryValue, entryKey, seen, cookieField);
    }
    return result;
}

export function sanitizeTelemetry(value) {
    return sanitizeValue(value);
}

export function sanitizeTelemetryUrl(rawUrl) {
    try {
        const base = typeof window !== 'undefined' ? window.location.href : 'https://streamstorm.invalid/';
        const url = new URL(String(rawUrl), base);
        if (url.username) url.username = REDACTED;
        if (url.password) url.password = REDACTED;
        for (const key of [...url.searchParams.keys()]) {
            if (isSensitiveTelemetryKey(key)) url.searchParams.set(key, REDACTED);
        }
        url.hash = sanitizeTelemetryString(url.hash);
        return `${url.origin === 'https://streamstorm.invalid' ? '' : url.origin}${url.pathname}${url.search}${url.hash}`;
    } catch {
        throw new Error('Unable to safely redact telemetry URL');
    }
}

export function isSensitiveInput(element) {
    if (!element) return true;
    if (element.type === 'password' || element.type === 'file' || element.isContentEditable) return true;
    const descriptors = [element.name, element.id, element.autocomplete, element.getAttribute?.('aria-label'), element.placeholder];
    return descriptors.some((item) => item && isSensitiveTelemetryKey(item));
}

export function markInputsPrivate(root = document) {
    if (root.matches?.('input, textarea, select, [contenteditable="true"]')) {
        root.setAttribute('data-atatus-privacy', 'mask');
        root.setAttribute('data-clarity-mask', 'true');
    }
    const fields = root.querySelectorAll?.('input, textarea, select, [contenteditable="true"]') || [];
    for (const field of fields) {
        // Atatus Replay and Microsoft Clarity both honor these attributes as DOM masking controls.
        field.setAttribute('data-atatus-privacy', 'mask');
        field.setAttribute('data-clarity-mask', 'true');
    }
}

let consoleRedactionInstalled = false;
export function installConsoleRedaction() {
    if (typeof console === 'undefined' || consoleRedactionInstalled) return;
    consoleRedactionInstalled = true;
    for (const level of ['log', 'debug', 'info', 'warn', 'error']) {
        const original = console[level]?.bind(console);
        if (!original) continue;
        console[level] = (...args) => {
            try {
                original(...args.map((arg) => sanitizeTelemetry(arg)));
            } catch {
                // Do not pass unsanitized console output to log-forwarding agents.
            }
        };
    }
}
