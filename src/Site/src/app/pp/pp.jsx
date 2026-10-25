"use client";
import { useEffect } from 'react';
import { logEvent } from 'firebase/analytics';
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
            StreamStorm integrates <strong>Atatus Browser Real User Monitoring (RUM)</strong> and <strong>Atatus Browser Logs</strong> (loaded via official CDN <code>https://js-cdn.atatus.io/atatus-browser-agent/latest/</code> through Google Tag Manager) across both our web portal and desktop user interface to achieve 100% full observability, diagnose software bugs, monitor performance vitals, and ensure software stability.
          </p>
          <div>
            <strong>Data Collected via Atatus (Configured with 100% Sampling &amp; Unmasked Privacy Level):</strong>
            <ul>
              <li><strong>100% Unmasked Session Replays (<code>defaultPrivacyLevel: &apos;allow&apos;</code>):</strong> To deliver complete visibility into application workflows and diagnose edge-case issues, visual session replay recording is enabled with unmasked privacy settings. This captures all screen interactions, cursor movements, clicks, form inputs, video URLs, chat messages, channel names, API configuration inputs, page transitions, and DOM state changes in full unmasked plaintext for comprehensive debugging fidelity.</li>
              <li><strong>Browser Logs &amp; Diagnostics:</strong> All client console logs (<code>log</code>, <code>debug</code>, <code>info</code>, <code>warn</code>, <code>error</code>), runtime exceptions, and browser Reporting API diagnostics (CSP violations, deprecations, interventions) are collected and forwarded to Atatus for error diagnosis.</li>
              <li><strong>Performance, Network Payloads &amp; Web Vitals:</strong> Page load times, resource timings, HTTP/WebSocket request and response payloads, Core Web Vitals (LCP, FID, CLS, INP), and custom application vitals (such as storm setup duration, socket sync, profile operations).</li>
              <li><strong>Custom Operations, Feature Flags &amp; User Actions:</strong> All actions triggered within the app (e.g., launching a storm, stopping a storm, opening modals, configuring API keys, validating channels), feature flag evaluations, and their success or failure status.</li>
              <li><strong>Session Persistence &amp; Cross-Subdomain Tracking:</strong> Anonymous user identifiers, session contexts, cookies, and <code>localStorage</code> state are persisted across pages and subdomains to correlate user journeys end-to-end.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2>3. Behavioral Analytics &amp; Heatmaps (Microsoft Clarity via GTM)</h2>
          <p>
            We use <strong>Microsoft Clarity</strong> (deployed via Google Tag Manager) to capture how users interact with our website and user interface through behavioral metrics, heatmaps, scroll depth tracking, click tracking, and session replays.
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
            <li><strong>YouTube Authentication Data:</strong> Google/YouTube cookies or browser profiles generated during setup remain stored locally on your machine within your user profile directory. They are never sold or sent to third-party advertisers.</li>
            <li><strong>Custom AI API Keys:</strong> API keys provided for custom LLM integrations (OpenAI, Anthropic, Google Gemini, Ollama) are stored in your local configuration and communicated directly from your machine to the respective AI provider.</li>
            <li><strong>Network Traffic:</strong> The engine connects to the internet to check for software releases, download compatible browser drivers (chromedriver), interact with YouTube live chat streams as commanded by you, and transmit the monitoring telemetry detailed above.</li>
          </ul>
        </section>

        <section>
          <h2>7. Data Retention &amp; Security</h2>
          <p>
            Telemetry, error logs, and session recordings captured by Atatus and Microsoft Clarity are retained in accordance with their respective data retention policies (typically 30 to 90 days for diagnostic data). We implement standard technical safeguards to protect data transmission over encrypted HTTPS/TLS channels.
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
