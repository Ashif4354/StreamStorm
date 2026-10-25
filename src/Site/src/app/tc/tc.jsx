"use client";
import { useEffect } from 'react';
import { logEvent } from 'firebase/analytics';
import { analytics } from '@/config/firebase';
import * as atatus from '@/config/atatus';

const TermsAndConditions = () => {

  useEffect(() => {
    logEvent(analytics, 'tc_viewed', {
      page_location: window.location.href,
      page_path: window.location.pathname,
      page_title: document.title
    });
    atatus.siteLogger.info('Terms and conditions page viewed');
  }, []);

  return (
    <div className="tc-page">
      <article className="tc-container">
        <h1>Terms &amp; Conditions</h1>
        <p className="last-updated">Last Updated: October 25, 2026</p>

        <section>
          <h2>1. Acceptance of Terms</h2>
          <p>
            By downloading, installing, accessing, or using StreamStorm (including the desktop application, user interface, and website at <code>https://streamstorm.darkglance.in</code>), you explicitly agree to be bound by these Terms &amp; Conditions and our <a href="/pp">Privacy Policy</a>. If you do not agree with any part of these terms, you must immediately discontinue use of the software.
          </p>
        </section>

        <section>
          <h2>2. License &amp; Usage Rights</h2>
          <ul>
            <li>This software is licensed strictly for personal, non-commercial, and educational evaluation purposes.</li>
            <li>Redistribution, republishing, mirroring, or commercial sublicensing of binary packages is prohibited without prior written consent from the author.</li>
            <li>
              The official source code must always be obtained solely from the official GitHub repository at:{' '}
              <a href="https://github.com/Ashif4354/StreamStorm" target="_blank" rel="noopener noreferrer">
                github.com/Ashif4354/StreamStorm
              </a>.
            </li>
            <li>You may modify the source code for your own private, personal use; however, modified versions must not be redistributed or publicly hosted without permission.</li>
          </ul>
        </section>

        <section>
          <h2>3. Telemetry, Session Replays &amp; Observability Consent</h2>
          <p>
            To provide continuous software reliability, error detection, and performance optimization, StreamStorm employs 100% unmasked observability tools across its web application and desktop user interface:
          </p>
          <ul>
            <li><strong>Atatus Browser RUM &amp; 100% Unmasked Session Replays:</strong> By using the application, you explicitly acknowledge and consent that 100% of your session is visually recorded and analyzed via Atatus Real User Monitoring (<code>js-cdn.atatus.io</code>) configured with <code>defaultPrivacyLevel: &apos;allow&apos;</code> (unmasked). This includes all mouse movements, clicks, navigation paths, form submissions, typed inputs (including video URLs, chat messages, channel names, and settings), network request/response payloads, DOM mutations, error traces, and console logs.</li>
            <li><strong>Microsoft Clarity (via Google Tag Manager):</strong> You acknowledge and consent to behavioral analytics, clickmaps, scroll heatmaps, and full session recordings facilitated through Microsoft Clarity injected via Google Tag Manager.</li>
            <li><strong>Application Logs &amp; Metrics:</strong> All browser console logs, Reporting API events, custom vital metrics, and API/WebSocket interaction payloads are automatically forwarded to remote monitoring dashboards.</li>
          </ul>
        </section>

        <section>
          <h2>4. AI Assistance &amp; Prompt Disclosure (Kelu Ask AI)</h2>
          <p>
            When utilizing the integrated AI assistant powered by <strong>Kelu Ask AI</strong> (<a href="https://kelu.dev" target="_blank" rel="noopener noreferrer">kelu.dev</a>):
          </p>
          <ul>
            <li>You acknowledge and agree that all prompts, questions, conversation history, and inputs submitted to the AI assistant are stored and visible to the maintainer/administrator of StreamStorm.</li>
            <li>Prompt data is inspected for customer support, system diagnostics, and conversational AI model fine-tuning.</li>
            <li>You agree not to transmit sensitive credentials, passwords, or confidential personal data into the AI prompt box.</li>
          </ul>
        </section>

        <section>
          <h2>5. Responsible Use &amp; Platform Compliance</h2>
          <p>
            StreamStorm is a technical automation demonstration tool. You assume full and exclusive legal responsibility for how you utilize the software. You agree not to use StreamStorm in violation of applicable laws, regulations, or third-party Terms of Service (including YouTube and Google Community Guidelines).
          </p>
        </section>

        <section>
          <h2>6. Intellectual Property</h2>
          <p>
            All rights, title, copyright, and intellectual property in and to StreamStorm (including source code, architecture, designs, and branding) remain the exclusive property of Ashif (DarkGlance). Attribution to the original author must be preserved in all instances.
          </p>
        </section>

        <section>
          <h2>7. Disclaimer of Warranties &amp; Limitation of Liability</h2>
          <p>
            StreamStorm is provided on an &quot;AS-IS&quot; and &quot;AS-AVAILABLE&quot; basis, without warranties or conditions of any kind, either express or implied, including but not limited to merchantability, fitness for a particular purpose, or non-infringement. Under no circumstances shall the author or contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including loss of accounts, data, or operational interruption) arising out of the use or inability to use this software.
          </p>
        </section>

        <section>
          <h2>8. Termination &amp; Legal Remedies</h2>
          <p>
            Any violation of these terms immediately terminates your license to use the software. The author reserves the right to enforce intellectual property rights and seek legal remedies, including DMCA takedowns and injunctive relief.
          </p>
        </section>

        <section>
          <h2>9. Contact</h2>
          <p>
            For questions, legal notices, or permissions concerning these Terms &amp; Conditions, please contact:
            <br />
            📧 <a href="mailto:darkglance.developer@gmail.com">darkglance.developer@gmail.com</a>
          </p>
        </section>
      </article>
    </div>
  );
};

export default TermsAndConditions;
