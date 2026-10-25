# Configure StreamStorm telemetry in Google Tag Manager

This guide describes what to add, where to add it, and how to check it for both StreamStorm front ends. GTM owns the Atatus and Clarity tags; this repository cannot publish those remote tags.

## Which containers to edit

Verify container IDs in the app's current deployment variables before changing anything:

| App | GTM container | Atatus RUM project name |
| --- | --- | --- |
| Website (`src/Site`) | `GTM-P6S7P2C8` | `StreamStorm Site` (use the exact existing Atatus project `appName`) |
| Desktop UI (`src/UI`) | `GTM-T6SGZ28P` | `StreamStorm UI` (use the exact existing Atatus project `appName`) |

Site loads GTM in `src/Site/src/app/layout.js`; the desktop UI loads it from `src/UI/index.html`. These containers are separate, so make the same tag changes in each one.

## Atatus Browser RUM tag

In **each** GTM container:

1. Open **Tags** and edit the existing Atatus Browser RUM Custom HTML tag. If there is no RUM tag, create one.
2. Set its trigger to **Initialization – All Pages** so replay masking is configured before the application hydrates.
3. The documented Browser RUM API uses `atatusRum.init()` with `licenseKey`, `appName`, and native privacy configuration.
4. Paste the code below into the Custom HTML tag. Replace `PASTE_RUM_LICENSE_KEY` with the Browser RUM license key from that Atatus project. Replace `APP_NAME` with that project's exact application name (`StreamStorm Site` in Site container, `StreamStorm UI` in UI container).
5. Save, preview, and publish.

Standard Atatus RUM tag (per official Atatus documentation):

```html
<script>
(function () {
  if (window.__STREAMSTORM_ATATUS_RUM_INIT__) return;

  function initialize() {
    var rum = window.ATATUS_RUM || window.atatusRum;
    if (!rum || typeof rum.init !== 'function' || window.__STREAMSTORM_ATATUS_RUM_INIT__) return;

    window.ATATUS_RUM = window.atatusRum = rum;
    rum.init({
      licenseKey: '{{ATATUS_RUM_API_KEY}}',
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
      enablePrivacyForActionName: true
    });

    window.__STREAMSTORM_ATATUS_RUM_INIT__ = true;
    if (typeof window.__flushAtatusRumQueue === 'function') window.__flushAtatusRumQueue();
  }

  var existing = window.ATATUS_RUM || window.atatusRum;
  if (existing && typeof existing.init === 'function') {
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

### Privacy & Masking:
* **Native Atatus Masking**: `defaultPrivacyLevel: 'mask-user-input'` instructs Atatus Session Replay to automatically mask all form inputs, text areas, and user typing across the application. No manual regex or DOM rewriting is needed.

## Atatus Browser Logs tag

Keep Browser Logs as a **separate tag** from RUM:

1. Open the existing Browser Logs tag.
2. Configure initialization according to Atatus Browser Logs documentation (`atatusLogs.init`).
3. Set trigger to **Initialization – All Pages**.
4. Note on Console Wrapping: If `forwardConsoleLogs` is enabled (e.g. `['error', 'warn']`), Atatus intercepts `console.error` and `console.warn` to forward them to the Atatus dashboard. In browser developer consoles, this makes the top call frame point to `atatus-rum.js` or `atatus-logs.js`.
   * To see the original source file and line numbers in Chrome / Edge DevTools, add `atatus` to Chrome's **Ignore List** (`DevTools Settings -> Ignore List -> Add pattern /atatus.*\.js/` or right-click the script in console -> **Add script to ignore list**).
   * Alternatively, omit or set `forwardConsoleLogs: []` if console log forwarding is not desired.

## Microsoft Clarity tag

If Clarity is used in a container, keep one existing Clarity tag and ensure its input masking behavior is enabled in the Clarity dashboard settings so user-entered content is masked in recordings.

## Do not add Firebase through GTM

Site and UI already initialize Firebase Analytics in application code. Do not add a duplicate Firebase Analytics tag in GTM.

## References

- [Atatus Browser Agent Configuration](https://docs.atatus.com/docs/rum-monitoring/browser/configuration.html)
- [Atatus Session Replay Privacy Levels](https://docs.atatus.com/docs/rum-monitoring/browser/session-replay.html)
- [Atatus Browser Logs Documentation](https://docs.atatus.com/docs/browser-log-collection.html)
