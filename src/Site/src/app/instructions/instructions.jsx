"use client"
import { useEffect } from 'react';
import { logEvent } from 'firebase/analytics';
import { analytics } from '@/config/firebase';

const Instructions = () => {

  useEffect(() => {
    window.document.title = 'Instructions | StreamStorm';
    logEvent(analytics, 'instructions_viewed', {
      page_location: window.location.href,
      page_path: window.location.pathname,
      page_title: document.title
    });
  }, []);

  return (
    <div className="instructions-page">
      <div className="instructions-page-body">
        <article className="instructions-container">
          <h1 className="instructions-main-heading">Instructions</h1>

          <nav className="instructions-index" aria-label="Table of Contents">
            <h2 className="instructions-index-heading">Table of Contents</h2>
            <ul className="instructions-index-list">
              <li><a href="#requirements" className="instructions-index-link">Requirements</a></li>
              <li>
                <a href="#using-the-app" className="instructions-index-link">Using The Application</a>
                <ul className="instructions-index-list">
                  <li><a href="#step1" className="instructions-index-link">Step 1. Create Temp Profiles</a></li>
                  <li><a href="#step2" className="instructions-index-link">Step 2. Starting The Storm</a></li>
                  <li><a href="#storm-controls" className="instructions-index-link">Storm Controls</a></li>
                </ul>
              </li>
              <li><a href="#creating-channels" className="instructions-index-link">Creating Channels</a></li>
              <li>
                <a href="#host-config" className="instructions-index-link">Host Configuration</a>
                <ul className="instructions-index-list">
                  <li><a href="#access-from-device" className="instructions-index-link">Accessing From Another Device</a></li>
                </ul>
              </li>
              <li><a href="#precautions" className="instructions-index-link">Precautions</a></li>
            </ul>
          </nav>

          <ul className="instructions-list">
            <li className="instructions-list-item">
              Download the application from the official website or repository.
              <ul className="instructions-list">
                <li className="instructions-list-item">
                  <a href="https://streamstorm.darkglance.in" target="_blank" rel="noopener noreferrer" className="instructions-link">StreamStorm Download Page</a>
                </li>
                <li className="instructions-list-item">
                  <a href="https://github.com/Ashif4344/StreamStorm" target="_blank" rel="noopener noreferrer" className="instructions-link">GitHub Repository</a>
                </li>
              </ul>
            </li>
            <li className="instructions-list-item">
              Install the application by following the setup wizard.
              <ul className="instructions-list">
                <li className="instructions-list-item">Double-click the downloaded installer file and follow the on-screen instructions.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              Always run the application as administrator for proper functionality.
              <ul className="instructions-list">
                <li className="instructions-list-item">Right-click on the application icon and select "Run as administrator".</li>
                <li className="instructions-list-item">Admin privileges are required to free up RAM.</li>
              </ul>
            </li>
          </ul>

          <div className="instructions-warning">
            <p className="instructions-warning-text">
              <strong>Disclaimer:</strong> You may get your channels <strong>Deleted</strong>  or <strong>Banned</strong>, and you may not be able to use Youtube with the account you used for StreamStorm, because we are violating Youtube Terms and Conditions. So <strong>use a temp/fake gmail account</strong> for creating channels for the spam. <strong>Never use your Real/Personal Account.</strong>
            </p>
          </div>

          <h2 id="requirements" className="instructions-section-heading">Requirements</h2>
          <ul className="instructions-list">
            <li className="instructions-list-item">You need to have a YouTube account (Google account) to use the application.</li>
            <li className="instructions-list-item">In your YouTube account, you need to have at least one channel created. More channels are recommended for better results.</li>
            <li className="instructions-list-item">If you don't have many channels, we have a feature that can create channels for you. <a href="#creating-channels" className="instructions-index-link"><i>click to proceed</i></a></li>
            <li className="instructions-list-item">You need to have Chrome browser installed on your system.</li>
            <li className="instructions-list-item">Stable internet connection to function properly.</li>
            <li className="instructions-list-item">To use one channel you need to have at least 300MB of free RAM available on your system. The more channels you use, the more RAM is required.</li>
          </ul>

          <h2 id="using-the-app" className="instructions-section-heading">Using The Application</h2>

          <h3 id="step1" className="instructions-step-heading">Step 1. Create Temp Profiles</h3>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              Creating temp profiles is the first step to use the application.
              <ul className="instructions-list">
                <li className="instructions-list-item">In the application UI, click on the <code className="instructions-inline-code">Manage Environment</code> button.</li>
                <li className="instructions-list-item">In create profile section, enter number of profiles you want to create.</li>
                <li className="instructions-list-item">Click on the <code className="instructions-inline-code">Create Profiles</code> button.</li>
                <div className='instructions-warning'>
                  <li><strong>Caution:</strong> Do not Minimize or Move away from the browser window while creating profiles.</li>
                </div>
              </ul>
            </li>
            <li className="instructions-list-item">The application will open a browser window and it will prompt you to log in to your YouTube account</li>
            <li className="instructions-list-item">Login to your YouTube account in the browser window that opens.</li>
            <li className="instructions-list-item">After logging in, the application will fetch all the channels available in your YouTube account.</li>
            <li className="instructions-list-item">After fetching the channels, the application will first close itself, and start creating the profiles.</li>
            <li className="instructions-list-item">Each temp profile will take up to <code className="instructions-inline-code">150MB</code> of storage space.</li>
          </ul>
          <p className="instructions-paragraph">The reason for creating all these profiles is that, each channel will require a separate profile to avoid any conflicts or issues with opening the browser window, since one browser window locks its own profile from being accessed by another instance of the same browser.</p>
          <p className="instructions-note"><code className="instructions-inline-code">There is also provision to delete all temp profiles created by the application, in case you want to start fresh.</code></p>

          <h3 id="step2" className="instructions-step-heading">Step 2. Starting The Storm</h3>
          <p className="instructions-paragraph">First Open the application and make sure you have created the temp profiles as mentioned in <code className="instructions-inline-code">Step 1.</code></p>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              You need to provide all the required information to start the storm.
              <ol className="instructions-list">
                <li className="instructions-list-item">
                  <strong>Video URL</strong>: Enter the URL of the YouTube video you want to storm.
                  <ul className="instructions-list">
                    <li className="instructions-list-item">This should be a valid youtube url copied from the url bar of your browser.</li>
                    <li className="instructions-list-item">It should not be a playlist or channel URL.</li>
                    <li className="instructions-list-item">Example: <code className="instructions-inline-code">https://www.youtube.com/watch?v=VIDEO_ID</code></li>
                  </ul>
                </li>
                <li className="instructions-list-item">
                  <strong>Messages</strong>: Enter the messages you want to send in the chat.
                  <ul className="instructions-list">
                    <li className="instructions-list-item">You can enter multiple messages separated by a new line.</li>
                    <li className="instructions-list-item">Example:
                      <div className="instructions-code-block">
                        Hello everyone! <br />
                        Let's support this video!
                      </div>
                    </li>
                    <li className="instructions-list-item">You can also use emojis in the messages.</li>
                    <li className="instructions-list-item">You can enter as many messages as you like.</li>
                  </ul>
                </li>
                <li className="instructions-list-item">
                  <strong>Subscribe switch</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">Some channels require you to subscribe to them before you can comment on their videos.</li>
                    <li className="instructions-list-item">If the channel you are trying to storm requires you to subscribe, then you need to enable this switch.</li>
                  </ul>
                </li>
                <li className="instructions-list-item">
                  <strong>Subscribe and Wait Switch</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">Some channels require you to subscribe to them and wait for a fixed time before you can comment on their videos.</li>
                    <li className="instructions-list-item">If the channel you are trying to storm requires you to subscribe and wait, then you need to enable this switch.</li>
                  </ul>
                </li>
                <li className="instructions-list-item">
                  <strong>Subscribe and Wait Time</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">If you have enabled the <code className="instructions-inline-code">Subscribe and Wait</code> switch, then you need to enter the time in seconds you want to wait after subscribing to the channel.</li>
                    <li className="instructions-list-item">This is the time you want to wait before starting the storm.</li>
                    <li className="instructions-list-item">Example: <code className="instructions-inline-code">10</code> (for 10 seconds)</li>
                  </ul>
                </li>
                <li className="instructions-list-item">
                  <strong>Slow mode</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">Some channels have slow mode enabled, which means you can only send a limited number of messages in a fixed time.</li>
                    <li className="instructions-list-item">If the channel you are trying to storm has slow mode enabled, then you need to enter the time in seconds you want to wait before sending each message.</li>
                    <li className="instructions-list-item">Example: <code className="instructions-inline-code">5</code> (for 5 seconds)</li>
                  </ul>
                </li>
                <li className="instructions-list-item">
                  <strong>Channel selection</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">
                      Basic
                      <ul className="instructions-list">
                        <li className="instructions-list-item">In basic mode you just enter the number of channels you want to use for the storm.</li>
                        <li className="instructions-list-item">The application will automatically select the channels for you, starting from the first channel in the list, to the nth channel you provided.</li>
                      </ul>
                    </li>
                    <li className="instructions-list-item">
                      Intermediate
                      <ul className="instructions-list">
                        <li className="instructions-list-item">In intermediate mode you can select a range of channels you want to use for the storm.</li>
                        <li className="instructions-list-item">for example if you have 10 channels and you want to use channels from 3 to 7, then you can give start index as 3 and end index as 7.</li>
                        <li className="instructions-list-item">The application will select the channels from the start index to the end index you provided.</li>
                      </ul>
                    </li>
                    <li className="instructions-list-item">
                      Advanced
                      <ul className="instructions-list">
                        <li className="instructions-list-item">In advanced mode you can manually select the channels you want to use for the storm.</li>
                      </ul>
                    </li>
                  </ul>
                </li>

                <li className="instructions-list-item">
                  <strong>Load in Background</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">If you don't want the browser ui to be visible while the storm is running, you can enable this switch.</li>
                    <li className="instructions-list-item">This will load the browser in the background and the storm will run in the background.</li>
                  </ul>
                  <div className="instructions-warning">
                    <p className="instructions-warning-text"><strong>Note: ⚠ This feature is currently experimental and may not work as expected. We're actively working on fixing the bugs.</strong></p>
                  </div>
                </li>
                <li className="instructions-list-item">
                  <strong>Start Storm</strong>
                  <ul className="instructions-list">
                    <li className="instructions-list-item">After providing all the required information, you can click on the <code className="instructions-inline-code">Start Storm</code> button to start the storm.</li>
                    <li className="instructions-list-item">The application will open the browser and start sending the messages in the chat.</li>
                    <li className="instructions-list-item">You can see the progress of the storm in the application UI.</li>
                    <li className="instructions-list-item">You can stop the storm at any time by clicking on the <code className="instructions-inline-code">Stop Storm</code> button.</li>
                  </ul>
                </li>
              </ol>
            </li>
          </ul>

          <h3 id="storm-controls" className="instructions-step-heading">Storm Controls</h3>
          <p className="instructions-paragraph">You can control the storm while it is running by using the following controls:</p>
          <ol className="instructions-list">
            <li className="instructions-list-item">
              <strong>Pause</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">This will pause the storm and the application will stop sending messages in the chat.</li>
                <li className="instructions-list-item">The application will keep the browser open and wait for you to resume the storm.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Resume</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">This will resume the storm and the application will start sending messages in the chat again.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Change Messages</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Sometime when the storm is running, you might want to change the messages you are sending in the chat.</li>
                <li className="instructions-list-item">You can click on the <code className="instructions-inline-code">Change Messages</code> button to change the messages.</li>
                <li className="instructions-list-item">This will open a dialog where you can enter the new messages you want to send in the chat.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Change Slow Mode</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">If you want to change the slow mode time while the storm is running, you can click on the <code className="instructions-inline-code">Change Slow Mode</code> button.</li>
                <li className="instructions-list-item">This will open a dialog where you can enter the new slow mode time you want to use.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Don't wait</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Some time what happens is that when most of the channels are ready to storm and is still waiting for the remaining channels to be ready, you can click on the <code className="instructions-inline-code">Don't wait</code> button.</li>
                <li className="instructions-list-item">This will make the application to not wait for the remaining channels and start sending messages in the chat immediately.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Add Channels</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Sometimes when the storm is running, you notice that there is more free RAM available on your system and you want to start storming with more channels, you can click on the <code className="instructions-inline-code">Add Channels</code> button.</li>
                <li className="instructions-list-item">This will open a dialog where you can select channels you want to add to the storm.</li>
                <li className="instructions-list-item"><strong>Note: You need to have enough temp profiles, and enough channels on your YouTube account to add more channels to the storm.</strong></li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Stop Storm</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">If you want to stop the storm, you can click on the <code className="instructions-inline-code">Stop Storm</code> button.</li>
                <li className="instructions-list-item">This will stop the storm and the application will close all the browser instances opened by the application.</li>
              </ul>
            </li>
          </ol>

          <h3 id="creating-channels" className="instructions-step-heading">Creating Channels</h3>
          <p className="instructions-paragraph">First Click on <code className="instructions-inline-code">Manage Environment</code> button</p>

          <h4>Without Logo</h4>
          <ul className="instructions-list">
            <li className="instructions-list-item">Do not toggle the logo required switch</li>
            <li className="instructions-list-item">Enter names of channels separated by a new line</li>
            <li className="instructions-list-item">Click on the <code className="instructions-inline-code">Create Channels</code> button.</li>
            <li className="instructions-list-item">This will start creating channels with the names provided without any logo.</li>
          </ul>

          <h4>With Logo</h4>
          <p>You can also create channels with logo, either random logo or custom logo provided by you</p>
          <ul className="instructions-list">
            <li className="instructions-list-item">Toggle the logo required switch</li>

            <h4>Random Logo</h4>
            <ul className="instructions-list">
              <li className="instructions-list-item">Click on Random Logo radio button.</li>
              <li className="instructions-list-item">Enter names of channels separated by a new line.</li>
              <li className="instructions-list-item">Click on the <code className="instructions-inline-code">Create Channels</code> button.</li>
              <li className="instructions-list-item">This will start creating channels with the names provided with random logo from google's logo collection.</li>
            </ul>

            <h4>Custom Logo</h4>
            <ul className="instructions-list">
              <li className="instructions-list-item">Click on <code className="instructions-inline-code">Custom Logo radio button</code>.</li>
              <li className="instructions-list-item">In this you need not provide channel names in the textbox.</li>
              <li className="instructions-list-item">You need to have a directory in your local PC with image files with channel name as its name.</li>
              <li className="instructions-list-item">If you want to create 10 channels with logo, you need to have 10 files in the directory, one for each channel, with the channel name as the file name and the logo as the image.</li>
              <li className="instructions-list-item">For example, if you have an image file named <code className="instructions-inline-code">Pro Gamer.png</code> in the directory, then a channel named <code className="instructions-inline-code">Pro Gamer</code> with the logo <code className="instructions-inline-code">Pro Gamer.png</code> will be created.</li>
              <li className="instructions-list-item">Note: only image files with <code className="instructions-inline-code">.png</code> <code className="instructions-inline-code">.jpg</code> <code className="instructions-inline-code">.jpeg</code> extension are supported.</li>
              <li className="instructions-list-item">Enter the directory path in the textbox provided and click <code className="instructions-inline-code">Validate</code> .</li>
              <li className="instructions-list-item">After validating, click on the <code className="instructions-inline-code">Create Channels</code> button.</li>
              <li className="instructions-list-item">This will start creating channels with the names and logo provided.</li>
              <p className="instructions-warning-text"><strong>Note: ⚠ Custom logo is currently experimental and may not work as expected. We're actively working on fixing the bugs.</strong></p>
            </ul>
          </ul>

          <h2 id="host-config" className="instructions-section-heading">Host Configuration</h2>
          <ul className="instructions-list">
            <li className="instructions-list-item">The backend server of the application is hosted on your local machine.</li>
            <li className="instructions-list-item">The Server is configured to run on port <code className="instructions-inline-code">1919</code>.</li>
          </ul>


          <h3 id="access-from-device" className="instructions-step-heading">Accessing The application from another device</h3>
          <p className="instructions-paragraph">We have Provisions to access the application from another device on the same network or a different network. The another device can be a mobile phone, tablet, or another computer. First you need to make sure that the application is running on your machine, The UI will boot up, but don't close the UI, otherwise the local server will shut down.</p>

          <div className="instructions-highlight">
            First you need to open <a href="https://streamstorm-ui.darkglance.in" target="_blank" rel="noopener noreferrer" className="instructions-link">https://streamstorm-ui.darkglance.in</a> in your web browser.
          </div>

          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Same Network</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">If you want to access the application from another device on the same network, you need to provide the IP address of your machine running the application.</li>
                <li className="instructions-list-item">You can find your IP address by running the command <code className="instructions-inline-code">ipconfig</code> in the command prompt or powershell. Look for the <code className="instructions-inline-code">IPv4 Address</code> under your active network connection. eg. <code className="instructions-inline-code">192.168.1.100</code></li>
                <li className="instructions-list-item">Once you have your IP address, you can access the application from another device by entering the URL <code className="instructions-inline-code">http://&lt;your-ip-address&gt;:1919</code> in the browser.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Different Network</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">If you want to access the application from another device on a different network, you need to configure port forwarding on your router.</li>
                <li className="instructions-list-item">You need to forward the port <code className="instructions-inline-code">1919</code> to the IP address of your machine running the application.</li>
                <li className="instructions-list-item">Once you have configured port forwarding, you can access the application from another device by entering the URL <code className="instructions-inline-code">http://&lt;your-public-ip-address&gt;:1919</code> in the browser.</li>
                <li className="instructions-list-item">You can find your public IP address by searching for "What is my IP" in Google. eg. <code className="instructions-inline-code">203.0.113.0</code></li>
                <li className="instructions-list-item">If you didn't understand how to configure port forwarding, you can search in Google for "How to configure port forwarding" for your router model. There will be many tutorials available online.</li>
              </ul>
            </li>
          </ul>
          <h2 id="precautions" className="instructions-section-heading">Precautions</h2>
          <ul className="instructions-list">
            <li className="instructions-list-item">The less free RAM you have after clicking <code className="instructions-inline-code">Start Storm</code>, the more likely the storming process will be slower, and the more likely it is to fail. So choose the number of accounts responsibly. For example, if you have 10 GB of free RAM, use only 6-7 GB for storm and keep the rest free, for a smooth flow.</li>
          </ul>
        </article>
      </div>
    </div>
  );
};



export default Instructions;