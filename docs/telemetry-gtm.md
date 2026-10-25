# Configure StreamStorm telemetry in Google Tag Manager

This guide describes what to add, where to add it, and how to check it for both StreamStorm front ends. GTM owns the Atatus and Clarity tags; this repository cannot publish those remote tags.

## Which containers to edit

The Antigravity walkthrough lists these IDs. Verify them in the app's current deployment variables before changing anything:

| App | GTM container listed in the walkthrough | Atatus RUM project name |
| --- | --- | --- |
| Website (`src/Site`) | `GTM-P6S7P2C8` | `StreamStorm Site` (use the exact existing Atatus project `appName`) |
| Desktop UI (`src/UI`) | `GTM-T6SGZ28P` | `StreamStorm UI` (use the exact existing Atatus project `appName`) |

Site loads GTM in `src/Site/src/app/layout.js`; the desktop UI loads it from `src/UI/index.html`. These containers are separate, so make the same tag changes in each one.

## Atatus Browser RUM tag

In **each** GTM container:

1. Open **Tags** and edit the existing Atatus Browser RUM Custom HTML tag. If there is no RUM tag, create one. Do not leave the unsafe old tag enabled or add a second tag that initializes another RUM agent.
2. Set its trigger to **Initialization – All Pages** so replay masking and URL filtering are configured before the application hydrates.
3. Replace the old initialization block. The documented Browser RUM API uses `atatusRum.init()` with `licenseKey` and `appName`; the Antigravity snippet's `applicationId` and `clientToken` fields are not the documented RUM initialization fields.
4. Paste the code below into the Custom HTML tag. Replace `PASTE_RUM_LICENSE_KEY` with the Browser RUM license key from that Atatus project. Replace `APP_NAME` with that project's existing exact application name. Use `StreamStorm Site` in the Site container and `StreamStorm UI` in the UI container if those are the names in Atatus.
5. Save, use GTM **Preview**, and complete the checks below before publishing.

Use this tag body in both containers; only `APP_NAME` and `PASTE_RUM_LICENSE_KEY` differ:

```html
<script>
(function () {
  if (window.__STREAMSTORM_ATATUS_RUM_INIT__) return;

  var SECRET_NAME = /password|passwd|pwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|client[\s_-]?secret|access[\s_-]?key|refresh[\s_-]?token|session[\s_-]?id|csrf|xsrf/i;
  var SECRET_ASSIGNMENT = /(["']?(?:password|passwd|pwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|client[\s_-]?secret|access[\s_-]?key|refresh[\s_-]?token)["']?\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;&}]+)/gi;
  var BEARER = /\b(Bearer|Basic)\s+[^\s,;]+/gi;
  var JWT = /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b/g;
  var PROVIDER_KEY = /\b(?:sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{30,}|gh[pousr]_[A-Za-z0-9_]{20,}|ya29\.[A-Za-z0-9_-]{20,})\b/g;
  var KNOWN_COOKIE = /((?:__Secure-[A-Za-z0-9_-]+|__Host-[A-Za-z0-9_-]+|SID|HSID|SSID|APISID|SAPISID|LOGIN_INFO|PREF|YSC|VISITOR_INFO1_LIVE|VISITOR_PRIVACY_METADATA|CONSENT|NID)=)[^;,\s]*/gi;
  var SECRET_HEADER = /((?:^|\r?\n)\s*(?:cookie|set-cookie|authorization|proxy-authorization|x-api-key|api-key)\s*:\s*)[^\r\n]*/gi;

  function scrubUrl(raw) {
    var url = new URL(raw, location.href);
    url.username = '';
    url.password = '';
    Array.from(url.searchParams.keys()).forEach(function (key) {
      if (SECRET_NAME.test(key)) url.searchParams.set(key, '[REDACTED]');
    });
    url.hash = url.hash.replace(/([?#&](?:password|passwd|secret|token|authorization|cookie|credential|api[\s_-]?key|private[\s_-]?key|access[\s_-]?key|refresh[\s_-]?token)=)[^&#]*/gi, '$1[REDACTED]');
    return url.href;
  }

  function scrubValue(value, key, seen) {
    if (SECRET_NAME.test(key) || /^(headers|cookies)$/i.test(key)) return '[REDACTED]';

    if (typeof value === 'string') {
      var safe = value
        .replace(SECRET_HEADER, '$1[REDACTED]')
        .replace(KNOWN_COOKIE, '$1[REDACTED]')
        .replace(SECRET_ASSIGNMENT, '$1[REDACTED]')
        .replace(BEARER, '$1 [REDACTED]')
        .replace(JWT, '[REDACTED]')
        .replace(PROVIDER_KEY, '[REDACTED]');
      return safe.replace(/https?:\/\/[^\s"'<>]+/gi, function (rawUrl) {
        return scrubUrl(rawUrl);
      });
    }

    if (!value || typeof value !== 'object') return value;
    if (seen.has(value)) throw new Error('Cyclic telemetry event');
    seen.add(value);

    if (Array.isArray(value)) {
      return value.map(function (item) { return scrubValue(item, key, seen); });
    }

    Object.keys(value).forEach(function (property) {
      value[property] = /url/i.test(property) && typeof value[property] === 'string'
        ? scrubUrl(value[property])
        : scrubValue(value[property], property, seen);
    });
    return value;
  }

  function beforeSend(event) {
    try {
      scrubValue(event, '', new WeakSet());
      return true;
    } catch (_) {
      return false; // Fail closed if an event cannot be scrubbed.
    }
  }

  function initialize() {
    var rum = window.atatusRum;
    if (!rum || typeof rum.init !== 'function' || window.__STREAMSTORM_ATATUS_RUM_INIT__) return;

    rum.init({
      licenseKey: 'PASTE_RUM_LICENSE_KEY',
      appName: 'APP_NAME',
      env: 'production',
      version: '4.2.0',
      sessionSampleRate: 100,
      sessionReplaySampleRate: 100,
      trackUserInteractions: true,
      trackResources: true,
      trackResourceHeaders: false,
      trackLongTasks: true,
      trackAnonymousUser: true,
      defaultPrivacyLevel: 'mask-user-input',
      enablePrivacyForActionName: true,
      beforeSend: beforeSend
    });

    window.__STREAMSTORM_ATATUS_RUM_INIT__ = true;
    if (typeof window.__flushAtatusRumQueue === 'function') window.__flushAtatusRumQueue();
  }

  if (window.atatusRum && typeof window.atatusRum.init === 'function') {
    initialize();
  } else {
    var script = document.createElement('script');
    script.src = 'https://js-cdn.atatus.io/atatus-browser-agent/latest/atatus-rum.js';
    script.crossOrigin = 'anonymous';
    script.onload = initialize;
    document.head.appendChild(script);
  }
})();
</script>
```

The sample intentionally omits `trackingConsent`: Atatus documents it as `granted` by default. This matches the requested no-prompt behavior. It also leaves `trackResourceHeaders` off and starts replay with typed inputs masked. Sampling is set to 100% for sessions and replay; retain lower values only if you choose to sample less.

The code bridge accepts both documented lowercase `window.atatusRum` and the old uppercase global for compatibility. The GTM initializer above uses the documented lowercase global.

## Atatus Browser Logs tag

Keep Browser Logs as a **separate tag** from RUM. The app's `atatus` wrappers sanitize application logger calls before sending them to the Logs agent. In each container:

1. Open the existing Browser Logs tag. Keep the `atatus-logs.js` loader only if it is the script supplied for your Atatus Browser Logs project.
2. Check the initialization block against that project's current **Install** snippet. Browser Logs uses its own project credentials and options; do not put the RUM license key into the Logs tag.
3. Use **Initialization – All Pages** and ensure Logs is initialized once. After initialization, call `window.__flushAtatusLogsQueue()` if it exists.
4. Do not enable raw console, error, or browser-report forwarding until you have verified that those forwarded events pass through the same redaction. The app's explicit `atatus` logger calls continue to send sanitized logs.

The Antigravity walkthrough's `ATATUS_LOGS.init()` options are not established by the Browser RUM documentation. Verify that block using the Logs project's own current installation instructions before relying on it.

## Microsoft Clarity tag

If Clarity is used in a container, keep one existing Clarity tag and ensure its input masking behavior is enabled. The app marks editable controls with `data-clarity-mask="true"`; keep Clarity's masking setting enabled so user-entered content is masked in recordings. Apply this in both containers where Clarity is intended to run. Do not add a second Clarity tag.

## Do not add Firebase through GTM

Site and UI already initialize Firebase Analytics in application code. Their `logEvent` calls now pass through a redacting wrapper. Do not add a duplicate Firebase Analytics tag in GTM.

## Preview, verify, then publish

In **each container**, use GTM Preview before publishing:

1. Confirm exactly one RUM agent initializes and the RUM tag fires on app startup.
2. Confirm page views, user interactions, resource timings, app actions, and sanitized app logs still arrive.
3. Use fake canary values in a password/API-key field, cookie-shaped text, an authorization header, a URL query parameter, and a thrown error. Verify none of the canaries appear in RUM events, logs, or replay.
4. Verify form inputs are masked in replay and the resource payloads have no request headers.
5. Confirm a normal non-secret prompt or product action is still captured where the app sends it.
6. Publish each container only after these checks pass.

Atatus references:

- [Browser Agent Configuration](https://docs.atatus.com/docs/rum-monitoring/browser/configuration.html)
- [Browser Session Replay and Privacy](https://docs.atatus.com/docs/rum-monitoring/browser/session-replay.html)

The app-side sanitizer tests are in `src/UI/tests/telemetryRedaction.test.js`. This file documents the remote configuration; changes here do not publish GTM containers.
