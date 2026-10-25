"use client";
import { useEffect } from 'react';
import { safeLogEvent as logEvent } from '../../config/safeAnalytics.js';
import { analytics } from '@/config/firebase';
import * as atatus from '@/config/atatus';

const PrivacyPolicy = () => {

  useEffect(() => {
    logEvent(analytics, 'pp_viewed', {
      page_location: window.location.href,
      page_path: window.location.pathname,
      page_title: document.title
    });
    atatus.siteLogger.info('Privacy policy page viewed');
  }, []);

  return (
    <div className="pp-page">
      <article className="pp-container">
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last Updated: October 25, 2026</p>

        <section>
          <h2>1. Overview & Transparency Commitment</h2>
          <p>
            StreamStorm (&quot;we&quot;, &quot;our&quot;, or &quot;the software&quot;) believes in complete transparency regarding how data is collected, monitored, and utilized.
            This Privacy Policy explains what information is collected when you visit our website (<code>https://streamstorm.darkglance.in</code>) and use the StreamStorm Desktop Application &amp; UI, including detailed disclosures about telemetry, session replays, AI assistance prompts, and third-party observability tools.
          </p>
        </section>

        <section>
          <h2>2. Telemetry, Monitoring &amp; Session Replays (Atatus RUM)</h2>
          <p>
            StreamStorm sends product and diagnostic telemetry automatically while the website or desktop UI is in use. Atatus Browser RUM and Browser Logs are loaded through Google Tag Manager for session, performance, error, action, and log diagnostics. Firebase Analytics records selected product events, and Microsoft Clarity provides interaction analytics on pages where its Google Tag Manager tag is configured. There is no telemetry opt-in prompt.
          </p>
          <div>
            <strong>Telemetry categories:</strong>
            <ul>
              <li><strong>Usage and interaction:</strong> page paths, navigation, feature use, settings choices, workflow outcomes, and selected non-secret input values used to improve product behavior.</li>
              <li><strong>Session replay:</strong> replay records page interaction and DOM changes. Form controls and editable content are masked in replay. Custom product events can separately include non-secret values such as AI prompts when those values are relevant to the feature being diagnosed.</li>
              <li><strong>Performance and errors:</strong> page/resource timings, web vitals, application errors, operation durations, and selected browser console and runtime diagnostics.</li>
              <li><strong>Network diagnostics:</strong> sanitized JSON request/response data and request status/duration may be logged for troubleshooting. Credential-like fields and sensitive query parameters are redacted; request headers are not included in custom payload logs.</li>
              <li><strong>Credential exclusion:</strong> passwords, API keys, YouTube cookies, authorization values, access/refresh tokens, and file contents are excluded or redacted by application telemetry filters. Cookie file names and upload counts may be collected, but the file contents are not.</li>
              <li><strong>Session identifiers:</strong> Atatus, Firebase, and Clarity may use their own identifiers or storage to associate telemetry with sessions. These identifiers and associated diagnostics are handled by the respective providers.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2>3. Behavioral Analytics &amp; Heatmaps (Microsoft Clarity via GTM)</h2>
          <p>
            We use <strong>Microsoft Clarity</strong> (deployed via Google Tag Manager) for behavioral metrics, heatmaps, scroll depth, click activity, and session recordings on configured website and desktop UI pages. Input controls are masked, and StreamStorm marks editable fields for masking.
          </p>
          <p>
            Clarity data helps us understand user behavior, optimize navigation paths, identify UX friction points, and improve product usability. For further details on Microsoft Clarity&apos;s data practices, please review the <a href="https://privacy.microsoft.com/en-us/privacystatement" target="_blank" rel="noopener noreferrer">Microsoft Privacy Statement</a>.
          </p>
        </section>

        <section>
          <h2>4. AI Assistance &amp; Prompt Visibility (Kelu Ask AI)</h2>
          <p>
            StreamStorm incorporates <strong>Kelu Ask AI</strong> (<a href="https://kelu.dev" target="_blank" rel="noopener noreferrer">kelu.dev</a>) to provide interactive artificial intelligence assistance, troubleshooting, setup guidance, and user support directly within the application and website.
          </p>
          <div>
            <strong>Prompt &amp; Interaction Disclosure:</strong>
            <ul>
              <li><strong>Prompt Visibility:</strong> All prompts, queries, text inputs, conversation histories, and messages submitted through the Kelu Ask AI assistant are recorded and visible to the maintainer/administrator of StreamStorm.</li>
              <li><strong>Purpose of Collection:</strong> Prompts are reviewed to analyze user questions, provide timely technical support, debug application errors reported via chat, refine AI response quality, and improve software documentation.</li>
              <li><strong>Sensitive Information Warning:</strong> Please do not submit confidential credentials, sensitive passwords, private keys, or personal identifiers into the Kelu Ask AI prompt interface.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2>5. Firebase Analytics &amp; Cloud Functions</h2>
          <p>
            We utilize <strong>Google Firebase Analytics</strong> and <strong>Firebase Cloud Functions</strong> for aggregated usage statistics and event counts, such as:
          </p>
          <ul>
            <li>Total software downloads count (Windows installer, Linux packages)</li>
            <li>Aggregated page visit counts and navigation journeys</li>
            <li>Anonymous high-level application lifecycle events</li>
          </ul>
        </section>

        <section>
          <h2>6. Desktop Engine &amp; Local Data Storage</h2>
          <p>
            StreamStorm&apos;s desktop engine runs locally on your computer:
          </p>
          <ul>
            <li><strong>YouTube Authentication Data:</strong> Google/YouTube cookies or browser profiles generated during setup remain stored locally on your machine within your user profile directory. Authentication cookie values are excluded from application telemetry.</li>
            <li><strong>Custom AI API Keys:</strong> API keys provided for custom LLM integrations (OpenAI, Anthropic, Google Gemini, Ollama) are stored in your local configuration and communicated directly from your machine to the respective AI provider.</li>
            <li><strong>Network Traffic:</strong> The engine connects to the internet to check for software releases, download compatible browser drivers (chromedriver), interact with YouTube live chat streams as commanded by you, and transmit the monitoring telemetry detailed above.</li>
          </ul>
        </section>

        <section>
          <h2>7. Data Retention &amp; Security</h2>
          <p>
            Telemetry, logs, and session recordings are processed and retained by Atatus, Google Firebase, and Microsoft Clarity under their current service terms and retention controls. StreamStorm does not promise a fixed retention period. Telemetry is transmitted over HTTPS/TLS where supported by the provider.
          </p>
        </section>

        <section>
          <h2>8. Children&apos;s Privacy</h2>
          <p>
            StreamStorm is not directed at children under the age of 13, and we do not knowingly collect personal information from children under 13.
          </p>
        </section>

        <section>
          <h2>9. Changes to This Privacy Policy</h2>
          <p>
            We may update this Privacy Policy from time to time to reflect modifications in our software architecture, observability instrumentation, or legal requirements. Updated versions will be posted on this page with an updated &quot;Last Updated&quot; date.
          </p>
        </section>

        <section>
          <h2>10. Contact Information</h2>
          <p>
            If you have questions, feedback, or inquiries regarding this Privacy Policy or our observability practices, please reach out to:
            <br />
            📧 <a href="mailto:darkglance.developer@gmail.com">darkglance.developer@gmail.com</a>
            <br />
            🐙 <a href="https://github.com/Ashif4354/StreamStorm" target="_blank" rel="noopener noreferrer">GitHub Repository</a>
          </p>
        </section>
      </article>
    </div>
  );
};

export default PrivacyPolicy;
