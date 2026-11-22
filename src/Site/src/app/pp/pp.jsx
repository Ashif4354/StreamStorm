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
        <p className="last-updated">Last Updated: November 22, 2026</p>

        <section>
          <h2>1. Overview & Transparency Commitment</h2>
          <p>
            StreamStorm (&quot;we&quot;, &quot;our&quot;, or &quot;the software&quot;) believes in complete transparency regarding how data is collected, monitored, and utilized.
            This Privacy Policy explains what information is collected when you visit our website (<code>https://streamstorm.darkglance.in</code>) and use the StreamStorm Desktop Application &amp; UI, including detailed disclosures about telemetry, session replays, AI assistance prompts, and third-party observability tools.
          </p>
        </section>

        <section>
          <h2>2. Telemetry, Monitoring &amp; Diagnostics (Atatus, Firebase, Clarity &amp; Sentry)</h2>
          <p>
            StreamStorm sends product, performance, and diagnostic telemetry automatically while the website or desktop UI and backend engine are in use. Atatus Browser Real User Monitoring (RUM) is loaded via Google Tag Manager for session, performance, error, action, and diagnostic monitoring. Firebase Analytics records selected product events, Microsoft Clarity provides interaction analytics and heatmaps, and Sentry is utilized for backend application crash reporting and diagnostic error tracking (which may include exception stack traces, request metadata, and debugging contextual variables). Before an error report is sent, credential-like data (cookies, API keys, tokens, and authorization values) is masked, and your computer&apos;s hostname and user directory paths are removed. There is no telemetry opt-in prompt.
          </p>
          <div>
            <strong>Telemetry categories:</strong>
            <ul>
              <li><strong>Session Replay &amp; Full Masking:</strong> Session replays record user navigation, button clicks, and UI interactions to diagnose errors and usability issues. Session replay is configured with full masking (<code>defaultPrivacyLevel: &apos;mask&apos;</code>), which masks all text shown on screen and all text typed into input fields, textareas, and form controls, so content such as channel names, status labels, log lines, and anything you type is not visible in a session replay.</li>
              <li><strong>Performance &amp; Web Vitals:</strong> Page load times, resource timings, Core Web Vitals (LCP, FID, CLS, INP), and custom application timing metrics.</li>
              <li><strong>Errors &amp; Exceptions:</strong> Uncaught JavaScript exceptions, unhandled promise rejections, and application error boundary incidents to ensure software stability.</li>
              <li><strong>Product Actions &amp; Logs:</strong> High-level application events triggered within the user interface (e.g., starting or stopping a storm, opening modals, counts of channels or messages, prompt lengths, selected engine, login method, and AI provider and model names). Logged request details are limited to the HTTP method, URL path (without query string, fragment, or host), response status, and duration. Request and response bodies are not logged, and requests to Atatus, Firebase, and Google Tag Manager are excluded.</li>
              <li><strong>Form Interactions:</strong> Only the name and type of a form field that was changed is recorded, never the value you entered.</li>
              <li><strong>Content Not Logged:</strong> Video URLs, chat message text, channel names, AI prompt text, AI-generated content, cookie file names, file system paths, your configured engine host address, and engine log output are not included in Atatus action or log events.</li>
              <li><strong>Local Credential Separation:</strong> Authentication credentials—including YouTube session cookies, local browser profiles, and third-party AI API keys—are stored strictly on your local machine and are never transmitted in application telemetry.</li>
              <li><strong>Session Identifiers:</strong> Atatus, Firebase, and Microsoft Clarity use anonymous session identifiers and standard browser storage to correlate visits and sessions.</li>
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
          <h2>4. AI Features &amp; Prompt Disclosure (Kelu Ask AI &amp; In-App Generators)</h2>
          <p>
            StreamStorm incorporates artificial intelligence features, including <strong>Kelu Ask AI</strong> (<a href="https://kelu.dev" target="_blank" rel="noopener noreferrer">kelu.dev</a>) for interactive guidance and troubleshooting, as well as in-app AI prompt assistants for generating messages and channel names.
          </p>
          <div>
            <strong>Prompt &amp; Interaction Disclosure:</strong>
            <ul>
              <li><strong>Prompt Visibility (Kelu Ask AI):</strong> Prompts, queries, conversation histories, and messages submitted through the Kelu Ask AI assistant may be recorded and processed by that service and via application telemetry visible to the maintainer/administrator of StreamStorm.</li>
              <li><strong>In-App AI Generators:</strong> Prompts entered in the in-app message and channel name generators are sent directly from your machine to the AI provider you configured. Application telemetry records only the prompt length, number of results, and the provider and model names, not the prompt or the generated text.</li>
              <li><strong>Purpose of Collection:</strong> Prompts are reviewed to analyze user questions, provide technical support, debug application errors, monitor feature reliability, refine AI response quality, and improve software documentation.</li>
              <li><strong>Sensitive Information Warning:</strong> Please do not submit confidential credentials, sensitive passwords, private keys, or personal identifiers into any AI prompt interface within StreamStorm.</li>
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
            <li><strong>YouTube Authentication Data:</strong> Google/YouTube cookies or browser profiles generated during setup remain stored locally on your machine within your user profile directory. They are stored locally and are never transmitted in telemetry or sent to third-party advertisers.</li>
            <li><strong>Custom AI API Keys:</strong> API keys provided for custom LLM integrations (OpenAI, Anthropic, Google Gemini, Ollama) are stored in your local configuration and communicated directly from your machine to the respective AI provider.</li>
            <li><strong>Network Traffic:</strong> The engine connects to the internet to check for software releases, launch your locally installed Google Chrome (or the optional Obscura engine, which you install yourself) to interact with YouTube live chat streams as commanded by you, and transmit the monitoring telemetry detailed above.</li>
          </ul>
        </section>

        <section>
          <h2>7. Data Retention &amp; Security</h2>
          <p>
            Telemetry, logs, crash reports, and session recordings are processed and retained by Atatus, Sentry, Google Firebase, and Microsoft Clarity under their current service terms and retention controls. StreamStorm does not promise a fixed retention period. Telemetry is transmitted over HTTPS/TLS where supported by the provider.
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
