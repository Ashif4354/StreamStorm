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
            <p className="instructions-paragraph">For any queries, mail <a href="mailto:darkglance.developer@gmail.com" className="instructions-link">darkglance.developer@gmail.com</a></p>
            <ul className="instructions-index-list">
              <li><a href="#requirements" className="instructions-index-link">Requirements</a></li>
              <li>
                <a href="#using-the-app" className="instructions-index-link">Using The Application</a>
                <ul className="instructions-index-list">
                  <li><a href="#step1" className="instructions-index-link">Step 1. Manage Environment (Login)</a></li>
                  <li><a href="#step2" className="instructions-index-link">Step 2. Starting The Storm</a></li>
                </ul>
              </li>
              <li><a href="#creating-channels" className="instructions-index-link">Creating Channels</a></li>
              <li>
                <a href="#realtime-dashboard" className="instructions-index-link">Realtime Dashboard</a>
                <ul className="instructions-index-list">
                  <li><a href="#dashboard-metrics" className="instructions-index-link">Dashboard Metrics</a></li>
                  <li><a href="#storm-controls" className="instructions-index-link">Storm Controls</a></li>
                  <li><a href="#channel-status-menu" className="instructions-index-link">Channel Status Menu</a></li>
                  <li><a href="#view-configurations-menu" className="instructions-index-link">View Configurations Menu</a></li>
                </ul>
              </li>
              <li>
                <a href="#settings-menu" className="instructions-index-link">Settings Menu</a>
                <ul className="instructions-index-list">
                  <li><a href="#settings-general" className="instructions-index-link">General</a></li>
                  <li>
                    <a href="#settings-host" className="instructions-index-link">Host Configuration</a>
                    <ul className="instructions-index-list">
                      <li><a href="#access-from-device" className="instructions-index-link">Accessing From Another Device</a></li>
                    </ul>
                  </li>
                  <li><a href="#settings-appearance" className="instructions-index-link">Appearance</a></li>
                  <li><a href="#settings-api-keys" className="instructions-index-link">API Keys</a></li>
                </ul>
              </li>
              <li><a href="#precautions" className="instructions-index-link">Precautions</a></li>
              <li>
                <a href="#mcp-server" className="instructions-index-link">Using the StreamStorm MCP Server</a>
                <ul className="instructions-index-list">
                  <li><a href="#mcp-gemini" className="instructions-index-link">Gemini CLI</a></li>
                  <li><a href="#mcp-claude" className="instructions-index-link">Claude Desktop</a></li>
                  <li><a href="#mcp-chatgpt" className="instructions-index-link">ChatGPT</a></li>
                  <li><a href="#mcp-sample-prompts" className="instructions-index-link">Sample Prompts</a></li>
                  <li><a href="#mcp-available-tools" className="instructions-index-link">Available Tools</a></li>
                </ul>
              </li>
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

          <h3 id="step1" className="instructions-step-heading">Step 1. Manage Environment (Login)</h3>
          <p className="instructions-paragraph">Before starting a storm, you need to log in to your YouTube account. StreamStorm now uses <strong>cookie-based login</strong> as the default method, which is more reliable and efficient.</p>

          <ul className="instructions-list">
            <li className="instructions-list-item">
              In the application UI, click on the <code className="instructions-inline-code">Manage Environment</code> button.
            </li>
            <li className="instructions-list-item">
              A modal will open with two tabs: <strong>Login with Google</strong> and <strong>Login with Cookie Files</strong>.
            </li>
          </ul>

          <h4>Login with Google (Recommended)</h4>
          <ul className="instructions-list">
            <li className="instructions-list-item">Click the <code className="instructions-inline-code">Login with Google</code> button.</li>
            <li className="instructions-list-item">A browser window will open with a Google login page.</li>
            <li className="instructions-list-item">Log in with your Google account.</li>
            <li className="instructions-list-item">The application will automatically save the cookies after successful login.</li>
            <li className="instructions-list-item">These cookies will be used to authenticate when starting the storm.</li>
          </ul>
          <div className="instructions-warning">
            <p className="instructions-warning-text">
              <strong>Note:</strong> If your Google login is not reflected, it means the cookies have expired or corrupted and you need to try again.
            </p>
          </div>

          <h4>Login with Cookie Files</h4>
          <ul className="instructions-list">
            <li className="instructions-list-item">Click <code className="instructions-inline-code">Select Cookie Files</code> to open a file explorer.</li>
            <li className="instructions-list-item">Select your cookie files (JSON or Netscape format). You can select multiple files.</li>
            <li className="instructions-list-item">Only cookies for <code className="instructions-inline-code">youtube.com</code> will be parsed and saved.</li>
            <li className="instructions-list-item">Click <code className="instructions-inline-code">Submit Cookies</code> to upload and validate the cookies.</li>
            <li className="instructions-list-item">A browser window will open to fetch the available channels from your account.</li>
          </ul>

          <div className="instructions-warning">
            <p className="instructions-warning-text">
              <strong>Note:</strong> If the provided cookies are invalid or expired, the application will reject them. If your Google login is not reflected, it means the cookies have expired or invalid and you need to log in again.
            </p>
          </div>

          <h4>Alternative: Browser Profiles Login (Legacy)</h4>
          <p className="instructions-paragraph">The temp profiles-based login is still available for users who prefer it. You can switch the login method in the <a href="#settings-general" className="instructions-index-link">Settings → General</a> section.</p>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              To use browser profiles login:
              <ul className="instructions-list">
                <li className="instructions-list-item">In the application UI, click on the <code className="instructions-inline-code">Manage Environment</code> button.</li>
                <li className="instructions-list-item">In the create profile section, enter the number of profiles you want to create.</li>
                <li className="instructions-list-item">Click on the <code className="instructions-inline-code">Create Profiles</code> button.</li>
                <div className='instructions-warning'>
                  <li><strong>Caution:</strong> Do not minimize or move away from the browser window while creating profiles.</li>
                </div>
              </ul>
            </li>
            <li className="instructions-list-item">The application will open a browser window and prompt you to log in to your YouTube account.</li>
            <li className="instructions-list-item">Login to your YouTube account in the browser window that opens.</li>
            <li className="instructions-list-item">After logging in, the application will fetch all the channels available in your YouTube account.</li>
            <li className="instructions-list-item">After fetching the channels, the application will close itself and start creating the profiles.</li>
            <li className="instructions-list-item">Each temp profile will take up to <code className="instructions-inline-code">150MB</code> of storage space.</li>
          </ul>
          <p className="instructions-paragraph">The reason for creating all these profiles is that each channel requires a separate profile to avoid any conflicts or issues with opening the browser window, since one browser window locks its own profile from being accessed by another instance of the same browser.</p>
          <p className="instructions-note"><code className="instructions-inline-code">There is also provision to delete all temp profiles created by the application, in case you want to start fresh.</code></p>

          <h3 id="step2" className="instructions-step-heading">Step 2. Starting The Storm</h3>
          <p className="instructions-paragraph">First open the application and make sure you have logged in as mentioned in <code className="instructions-inline-code">Step 1.</code></p>
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

          <h3 id="creating-channels" className="instructions-step-heading">Creating Channels</h3>
          <p className="instructions-paragraph">Make sure you have logged in first (see <a href="#step1" className="instructions-index-link">Step 1</a>), then click on the <code className="instructions-inline-code">Manage Environment</code> button.</p>

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

          <h2 id="realtime-dashboard" className="instructions-section-heading">Realtime Dashboard</h2>
          <p className="instructions-paragraph">Once you start a storm, the Realtime Dashboard provides comprehensive monitoring and control capabilities. It displays live statistics about your storm and allows you to manage individual instances in real-time.</p>

          <h3 id="dashboard-metrics" className="instructions-step-heading">Dashboard Metrics</h3>
          <p className="instructions-paragraph">The dashboard displays the following real-time metrics:</p>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Storm Status</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Shows the current state of the storm: <code className="instructions-inline-code">Running</code>, <code className="instructions-inline-code">Paused</code>, or <code className="instructions-inline-code">Stopped</code>.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Active Storming Instances</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Displays the number of accounts currently active and sending messages in the chat.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Dead Instances</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Shows the number of accounts that have stopped storming due to errors, disconnections, or other issues.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Total Messages Sent</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">The cumulative count of all messages sent by all active accounts since the storm started.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Message Rate</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Shows the current rate of messages being sent per minute across all active instances.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Storm Duration</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Displays the total elapsed time since you pressed the Start button.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Live Log Feed</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">A real-time log stream showing all storm activities, including message sends, errors, and status changes.</li>
              </ul>
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

          <h3 id="channel-status-menu" className="instructions-step-heading">Channel Status Menu</h3>
          <p className="instructions-paragraph">The Channel Status Menu provides detailed visibility into all your accounts and their current states.</p>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Opening the Menu</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Click the <code className="instructions-inline-code">Channel Status</code> button located below the Stop button in the dashboard.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Information Displayed</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Lists all accounts/channels associated with your logged-in StreamStorm account.</li>
                <li className="instructions-list-item">Shows the current status of each channel: <code className="instructions-inline-code">Idle</code>, <code className="instructions-inline-code">Dead</code>, <code className="instructions-inline-code">Getting Ready</code>, <code className="instructions-inline-code">Ready</code>, or <code className="instructions-inline-code">Storming</code>.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Kill Individual Instance</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Each channel entry has a <code className="instructions-inline-code">Kill</code> button next to it.</li>
                <li className="instructions-list-item">Clicking this button will immediately stop that specific instance from storming without affecting other active instances.</li>
                <li className="instructions-list-item">Useful for removing problematic accounts or freeing up resources during a storm.</li>
              </ul>
            </li>
          </ul>

          <h3 id="view-configurations-menu" className="instructions-step-heading">View Configurations Menu</h3>
          <p className="instructions-paragraph">The View Configurations Menu displays all the parameters configured for the current running storm.</p>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Opening the Menu</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Click the <code className="instructions-inline-code">View Configurations</code> button located below the Channel Status button in the dashboard.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Information Displayed</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Video URL being stormed.</li>
                <li className="instructions-list-item">Number of channels selected for storming.</li>
                <li className="instructions-list-item">Current slow mode setting.</li>
                <li className="instructions-list-item">Subscribe setting status.</li>
                <li className="instructions-list-item">Subscribe and Wait configuration (if enabled).</li>
                <li className="instructions-list-item">Load in Background setting status.</li>
                <li className="instructions-list-item">All configured messages being used for the storm.</li>
              </ul>
            </li>
          </ul>



          <h2 id="settings-menu" className="instructions-section-heading">Settings Menu</h2>
          <p className="instructions-paragraph">Access the Settings menu by clicking the settings icon in the application. The Settings menu contains the following sections:</p>

          <h3 id="settings-general" className="instructions-step-heading">General</h3>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Login Method</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item"><code className="instructions-inline-code">Cookies Based Login</code> (Default) - Uses saved cookies for authentication. More efficient and reliable.</li>
                <li className="instructions-list-item"><code className="instructions-inline-code">Browser Profiles</code> - Uses separate browser profiles for each channel. Legacy method that requires more storage.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Clear Login Data</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Remove all saved cookies, browser profiles, and channel data.</li>
                <li className="instructions-list-item">You will need to log in again after clearing the data.</li>
              </ul>
            </li>
          </ul>

          <h3 id="settings-host" className="instructions-step-heading">Host Configuration</h3>
          <ul className="instructions-list">
            <li className="instructions-list-item">Set the base URL of the StreamStorm backend server.</li>
            <li className="instructions-list-item">The backend server runs on your local machine on port <code className="instructions-inline-code">1919</code> by default.</li>
            <li className="instructions-list-item">Default URL: <code className="instructions-inline-code">http://localhost:1919</code></li>
            <li className="instructions-list-item">Change this if you're accessing the application from another device or using a custom server setup.</li>
          </ul>

          <h4 id="access-from-device">Accessing The Application From Another Device</h4>
          <p className="instructions-paragraph">You can access the application from another device on the same network or a different network. The device can be a mobile phone, tablet, or another computer. Make sure the application is running on your machine - don't close the UI, otherwise the local server will shut down.</p>

          <div className="instructions-highlight">
            First you need to open <a href="https://streamstorm-ui.darkglance.in" target="_blank" rel="noopener noreferrer" className="instructions-link">https://streamstorm-ui.darkglance.in</a> in your web browser.
          </div>

          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Same Network</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Find your IP address by running <code className="instructions-inline-code">ipconfig</code> in the command prompt. Look for the <code className="instructions-inline-code">IPv4 Address</code> (e.g., <code className="instructions-inline-code">192.168.1.100</code>).</li>
                <li className="instructions-list-item">Access the application by entering <code className="instructions-inline-code">http://&lt;your-ip-address&gt;:1919</code> in the browser.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Different Network</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Configure port forwarding on your router to forward port <code className="instructions-inline-code">1919</code> to your machine's IP address.</li>
                <li className="instructions-list-item">Find your public IP by searching "What is my IP" on Google (e.g., <code className="instructions-inline-code">203.0.113.0</code>).</li>
                <li className="instructions-list-item">Access the application by entering <code className="instructions-inline-code">http://&lt;your-public-ip-address&gt;:1919</code> in the browser.</li>
              </ul>
            </li>
          </ul>

          <h3 id="settings-appearance" className="instructions-step-heading">Appearance</h3>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>Theme</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item"><code className="instructions-inline-code">Light</code> - Light color scheme for the application.</li>
                <li className="instructions-list-item"><code className="instructions-inline-code">Dark</code> - Dark color scheme for the application.</li>
              </ul>
            </li>
          </ul>

          <h3 id="settings-api-keys" className="instructions-step-heading">API Keys</h3>
          <p className="instructions-paragraph">Configure API keys for AI-powered features like message generation and channel name suggestions. All API keys are stored locally on your PC.</p>
          <ul className="instructions-list">
            <li className="instructions-list-item">
              <strong>OpenAI</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">API Key</li>
                <li className="instructions-list-item">Base URL (optional, for custom endpoints)</li>
                <li className="instructions-list-item">Model name</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Anthropic (Claude)</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">API Key</li>
                <li className="instructions-list-item">Model name</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Google (Gemini)</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">API Key</li>
                <li className="instructions-list-item">Model name</li>
              </ul>
            </li>
          </ul>
          <div className="instructions-note">
            <p className="instructions-paragraph"><strong>Tip:</strong> You can use the OpenAI provider section for other LLM providers that are compatible with the OpenAI API standard (e.g., Ollama, Mistral, Groq, OpenRouter, DeepSeek, LocalAI, etc.). Just manually set the Base URL, API Key, and Model.</p>
          </div>
          <h2 id="precautions" className="instructions-section-heading">Precautions</h2>
          <ul className="instructions-list">
            <li className="instructions-list-item">The less free RAM you have after clicking <code className="instructions-inline-code">Start Storm</code>, the more likely the storming process will be slower, and the more likely it is to fail. So choose the number of accounts responsibly. For example, if you have 10 GB of free RAM, use only 6-7 GB for storm and keep the rest free, for a smooth flow.</li>
          </ul>

          <h2 id="mcp-server" className="instructions-section-heading">Using the StreamStorm MCP Server</h2>
          <p className="instructions-paragraph">StreamStorm exposes an MCP (Model Context Protocol) server that allows AI assistants to control the storm programmatically. The MCP server is accessible at <code className="instructions-inline-code">http://localhost:1919/mcp</code> when the application is running.</p>
          <p className="instructions-paragraph"><strong>You can perform all the actions available in the UI through the MCP server, plus additional tools</strong>, and more advanced storm management capabilities.</p>

          <h3 id="mcp-gemini" className="instructions-step-heading">Gemini CLI</h3>
          <p className="instructions-paragraph">You can add the StreamStorm MCP server to Gemini CLI using either the configuration file or the command line.</p>
          <p className="instructions-paragraph"><strong>Option 1: Configuration File</strong></p>
          <p className="instructions-paragraph">Add the following to your Gemini CLI configuration:</p>
          <pre className="instructions-code-block">
            {`{
  "mcpServers": {
    "StreamStorm": {
      "httpUrl": "http://localhost:1919/mcp"
    }
  }
}`}
          </pre>
          <p className="instructions-paragraph"><strong>Option 2: Command Line</strong></p>
          <pre className="instructions-code-block">
            {`gemini mcp add StreamStorm http://localhost:1919/mcp --transport http --scope user`}
          </pre>

          <h3 id="mcp-claude" className="instructions-step-heading">Claude Desktop</h3>
          <p className="instructions-paragraph">Add the following to your Claude Desktop configuration file:</p>
          <pre className="instructions-code-block">
            {`{
  "mcpServers": {
    "StreamStorm": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:1919/mcp"
      ]
    }
  }
}`}
          </pre>

          <h3 id="mcp-chatgpt" className="instructions-step-heading">ChatGPT</h3>
          <p className="instructions-paragraph">To use StreamStorm with ChatGPT, you need to expose the local server to the internet and configure the ChatGPT app.</p>
          <ol className="instructions-list">
            <li className="instructions-list-item">
              <strong>Expose the server to the internet</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">You need to expose <code className="instructions-inline-code">http://localhost:1919</code> to the internet using a tunneling service like Cloudflare Tunnel or ngrok.</li>
                <li className="instructions-list-item">For ngrok, run: <code className="instructions-inline-code">ngrok http 1919</code></li>
                <li className="instructions-list-item">Note down the public URL provided by the tunnel service.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Enable Developer Mode</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">In ChatGPT, enable developer mode in your settings.</li>
              </ul>
            </li>
            <li className="instructions-list-item">
              <strong>Create the App</strong>
              <ul className="instructions-list">
                <li className="instructions-list-item">Go to Settings → Apps → Create App.</li>
                <li className="instructions-list-item">Enter name: <code className="instructions-inline-code">StreamStorm</code></li>
                <li className="instructions-list-item">Add a description for the app.</li>
                <li className="instructions-list-item">In the URL field, enter: <code className="instructions-inline-code">&lt;your-tunnel-url&gt;/mcp</code></li>
                <li className="instructions-list-item">Select "No authentication".</li>
                <li className="instructions-list-item">Check the confirmation checkbox and click Create.</li>
              </ul>
            </li>
          </ol>
          <div className="instructions-warning">
            <p className="instructions-warning-text">
              <strong>Note:</strong> Developer mode must always be enabled, and the StreamStorm app must be selected in the ChatGPT chat field before prompting.
            </p>
          </div>

          <h3 id="mcp-sample-prompts" className="instructions-step-heading">Sample Prompts</h3>
          <p className="instructions-paragraph">Here are some example prompts you can use with AI assistants to control StreamStorm:</p>
          <ul className="instructions-list">
            <li className="instructions-list-item"><code className="instructions-inline-code">Start storming on https://www.youtube.com/watch?v=dQw4w9WgXcQ with 5 channels with slow mode 3 seconds</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Start storming on https://www.youtube.com/watch?v=dQw4w9WgXcQ with 5 channels with slow mode 3 seconds and also subscribe and wait for 30 seconds</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Start storming on https://www.youtube.com/watch?v=dQw4w9WgXcQ with 3 channels with crazy messages</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Pause the storm</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Resume the storm</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Stop the storm</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Change slow mode to 2 sec</code></li>
            <li className="instructions-list-item"><code className="instructions-inline-code">Add 2 more channels to the storm</code></li>
          </ul>
          <p className="instructions-paragraph">...and many more! The AI assistant can understand natural language commands and translate them into appropriate tool calls.</p>

          <h3 id="mcp-available-tools" className="instructions-step-heading">Available Tools</h3>
          <p className="instructions-paragraph">The following tools are available through the MCP server as of 27-12-2025:</p>
          <div className="instructions-code-block">
            <ul className="instructions-list" style={{ columnCount: 2, columnGap: '2rem' }}>
              <li className="instructions-list-item"><code className="instructions-inline-code">add_channels_to_storm</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">ai_generate_channel_names</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">ai_generate_messages</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">change_slow_mode</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">change_storm_messages</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">create_chromium_profiles</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">create_youtube_channels</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">delete_chromium_profiles</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_active_channels</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_ai_provider_keys</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_assigned_profiles</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_available_channels</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_available_profiles</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_channel_info</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_channel_status</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_logs</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_message_stats</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_storm_channels</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_storm_context</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_storm_history</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_storm_messages</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_storm_status</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_system_metrics</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_system_ram_info</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_system_settings</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">greet_streamstorm</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">health_check</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">kill_instance</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">pause_storm</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">resume_storm</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">save_ai_provider_key</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">set_default_ai_provider</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">get_settings</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">start_storm</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">start_storm_dont_wait</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">stop_storm</code></li>
              <li className="instructions-list-item"><code className="instructions-inline-code">verify_channels_directory</code></li>
            </ul>

          </div>
        </article>
      </div>
    </div>
  );
};



export default Instructions;