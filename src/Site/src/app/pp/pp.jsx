"use client"
import { useEffect } from 'react';
import { logEvent } from 'firebase/analytics';
import { analytics } from '@/config/firebase';

const PrivacyPolicy = () => {

  useEffect(() => {
    logEvent(analytics, 'pp_viewed', {
      page_location: window.location.href,
      page_path: window.location.pathname,
      page_title: document.title
    });
  }, []);

  return (
    <div className="pp-page">
      <article className="pp-container">
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last Updated: August 23, 2025</p>

        <section>
          <h2>1. No Personal Data Collection</h2>
          <p>
            StreamStorm does not collect, store, or share any personal or identifiable user data. We do not collect your name, email address, IP address, or any other personal information.
          </p>
        </section>

        <section>
          <h2>2. Anonymous Analytics & Telemetry</h2>
          <p>
            We use analytics services (Atatus and Firebase Analytics) to understand how users interact with the app and to monitor application performance. 
            This includes page visits (like this privacy policy), actions such as downloading the application or viewing the GitHub repository, 
            and telemetry data such as application performance metrics, error tracking, and usage statistics.
          </p>
          <p>
            However, all collected data is completely anonymous and does not contain any personal information. We do not know who you are and cannot identify you in any way. 
            The information we collect is general and helps us improve the application experience and performance.
          </p>
        </section>

        <section>
          <h2>3. Internet Usage</h2>
          <span>
            The app uses the internet only for:
            <ul>
              <li>Checking for software updates</li>
              <li>Downloading required browser webdrivers (chromedriver)</li>
              <li>Sending anonymous telemetry and performance data to Atatus</li>
              <li>Sending anonymous analytics data to Firebase Analytics</li>
            </ul>
            These operations are technical and do not involve any personal data.
          </span>
        </section>

        <section>
          <h2>4. Anonymous Data Collection</h2>
          <p>
            StreamStorm collects anonymous telemetry and analytics data to improve application performance and user experience. 
            This includes application usage patterns, performance metrics, and error tracking. However, we do not use cookies or any 
            technologies that can personally identify you. All data collected is aggregated and anonymous.
          </p>
        </section>

        <section>
          <h2>5. Offline-Friendly</h2>
          <p>
            Except for update checks, webdriver downloads, and anonymous analytics/telemetry data transmission, 
            all core features of the app work entirely offline.
          </p>
        </section>

        <section>
          <h2>6. Third-Party Services</h2>
          <span>
            StreamStorm uses the following third-party services for analytics and performance monitoring:
            <ul>
              <li><strong>Atatus:</strong> For anonymous application performance monitoring and error tracking</li>
              <li><strong>Firebase Analytics:</strong> For anonymous usage analytics and user interaction tracking</li>
            </ul>
            These services only receive anonymous, non-personal data. The core functionality of StreamStorm remains fully self-contained.
          </span>
        </section>

        <section>
          <h2>7. Children's Privacy</h2>
          <p>
            We do not collect any data from users, including those under the age of 13. The app is safe to use for all ages.
          </p>
        </section>

        <section>
          <h2>8. Contact</h2>
          <p>
            For any questions or concerns, feel free to contact:<br />
            📧 <a href="mailto:darkglance.developer@gmail.com">darkglance.developer@gmail.com</a>
          </p>
        </section>
      </article>
    </div>
  );
};

export default PrivacyPolicy;
