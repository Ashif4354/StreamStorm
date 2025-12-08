"use client"
import { useEffect } from 'react';
import { logEvent } from 'firebase/analytics';
import { analytics } from '@/config/firebase';

const TermsAndConditions = () => {

  useEffect(() => {
    logEvent(analytics, 'tc_viewed', {
      page_location: window.location.href,
      page_path: window.location.pathname,
      page_title: document.title
    });
  }, []);

  return (
    <div className="tc-page">
      <article className="tc-container">
        <h1>Terms & Conditions</h1>
        <p className="last-updated">Last Updated: July 5, 2025</p>

        <section>
          <h2>1. Acceptance of Terms</h2>
          <p>
            By downloading, installing, or using StreamStorm, you agree to these Terms & Conditions and the Personal Use License.
          </p>
        </section>

        <section>
          <h2>2. License & Usage</h2>
          <ul>
            <li>This software is licensed for personal and non-commercial use only.</li>
            <li>Redistribution, reuploading, or republishing of this software is strictly prohibited.</li>
            <li>
              The source must always be accessed only from the official repository at:{' '}
              
              <a href="https://github.com/Ashif4354/StreamStorm" target="_blank" rel="noopener noreferrer">
                Official repo
              </a>
            </li>
            <li>Personal modifications are allowed only for private use and should not be shared or published.</li>
          </ul>
        </section>

        <section>
          <h2>3. Intellectual Property</h2>
          <p>
            All rights and ownership of the StreamStorm project, including its code, branding, and related materials,
            belong solely to Ashif (aka DarkGlance).
          </p>
          <p>You must retain all references to the original author in the source and documentation.</p>
        </section>

        <section>
          <h2>4. Commercial Use</h2>
          <p>
            Commercial use, resale, sublicensing, or bundling of StreamStorm with other services or products is not allowed
            without explicit written permission from the author.
          </p>
        </section>

        <section>
          <h2>5. No Warranty</h2>
          <p>
            StreamStorm is provided "as-is" without any warranties, express or implied. The author is not responsible for
            any damages or losses resulting from use or misuse of the software.
          </p>
        </section>

        <section>
          <h2>6. Legal Consequences</h2>
          <p>
            Any violation of these terms will be considered a breach of license and may result in legal actions, including takedowns.
          </p>
        </section>

        <section>
          <h2>7. Contact</h2>
          <p>
            For collaborations, extended licenses, or clarifications, contact:<br />
            📧 <a href="mailto:darkglance.developer@gmail.com">darkglance.developer@gmail.com</a>
          </p>
        </section>
      </article>
    </div>
  );
};

export default TermsAndConditions;
