# 📘 **Introduction / Overview**

StreamStorm is a lightweight desktop application built specifically to automate mass messaging (aka spamming) in YouTube live stream chats. With support for multiple browser instances and persistent Google login, StreamStorm can blast messages into live chats across multiple streams — on repeat, on schedule, or at full throttle.

There’s no coding, no fancy setup — just plug in your message, set your intervals, and let the chaos unfold. Whether you're trying to flood, disrupt, or annoy, StreamStorm gives you the power to do it all with a click.

#### 🔒 No terms respected. No ethics included. Use it if you dare.

#### 🧨 Designed for abuse. Not for the faint-hearted.

# 🛠️ Core Functionality & Features

StreamStorm's core functionality revolves around its ability to automate the sending of messages in YouTube live chats. Key features include:

* **Multi-Account Management**: Seamlessly operate multiple YouTube channels using separate, isolated browser profiles.
* **Custom Channel Creation**: Effortlessly create multiple YouTube accounts directly from the app.
* **Custom Message Scheduling**: Control message timing with flexible intervals, supporting both rapid-fire and delayed delivery.
* **One-Click Profile System**:
  * Automatically generate and configure browser profiles per channel.
  * Prevents data collisions and detection by isolating each session.
  * Easily clean up all temporary profiles post-storm.
* **Browser Automation Engine**: Simulates real human interaction with YouTube’s live chat UI via robust browser automation.
* **Customizable Storm Parameters**:
  * Target specific YouTube video URLs.
  * Define a list of messages to send.
  * Set "slow mode" delays between messages.
  * Enable/disable account subscriptions and background loading without UI.
* **Flexible Channel Selection**:
  * **Basic**: Run a fixed number of channels.
  * **Intermediate**: Choose a channel range (e.g., 5–15).
  * **Advanced**: Manually pick specific channels to storm.
* **In-App System Monitoring**:
  * Real-time RAM tracking to ensure system stability.
  * Dynamically calculates how many channels can be run based on available resources.
* **Streamlined Control Panel**: A centralized dashboard to configure storm settings and monitor performance.
* **Modern Desktop UI**: Built with React and Material-UI, featuring both light and dark themes for optimal comfort.
* **Advanced Tuning Options**: Fine-tune performance parameters to match your use case or system limits — no coding required.

# Instructions to use The Application
###### [INSTRUCTIONS](https://streamstorm.darkglance.in/instructions)


# 👨‍💻 **Development Setup**

* If you wish to run the project from the source code, follow these steps.

**Prerequisites:**
* Node.js v20.17.0 or higher, [install from here](https://nodejs.org/en/download)
* UV (Python dependency manager), [install from here](https://docs.astral.sh/uv/getting-started/installation/) 

**First clone the repository:**

```bash
git clone https://github.com/Ashif4354/StreamStorm.git
```

**Booting the Engine (Backend)**

The backend is a FastAPI server that handles all the browser automation logic.

```bash
cd src/Engine
uv sync
uv run main.py
```

* No need to install Python or a virtual environment, uv will handle everything for you.
* The backend will run on `http://localhost:1919` by default. You can change this in the `main.py` file if needed.

**Booting the UI (Frontend)**

The frontend is a React application built with Vite.

```bash
cd src/UI
npm install
vite --host
```

* The frontend will run on `http://localhost:5173` by default. You can now open this URL in your browser and interact with the application.
* By default, the Engine will load the UI from `https://streamstorm-ui.darkglance.in/` in a separate window, but you can change this in the `main.py` file if needed. 
Just replace `https://streamstorm-ui.darkglance.in/` with `http://localhost:5173/` to load the local UI instead.

# 🧠 **Troubleshooting & FAQ**

*   **Error: "Engine is Busy"**
    *   This means the backend is already performing a resource-intensive task (like creating profiles or running a storm). Wait for the current task to complete.

*   **Error: "No storm is running. Start a storm first."**
    *   You are trying to use a storm control feature (like Pause, Resume, etc.) when no storm is active. Click "Start Storm" first.

*   **Issue: Browser window closes immediately after starting.**
    *   This might happen if the ChromeDriver is out of sync with your Chrome browser. The application attempts to manage this automatically, but a manual Chrome browser update might be needed.

# 📜 License

StreamStorm is licensed under the Personal Use License. See the [LICENSE](./LICENSE) file for more information.

# 🏆 Credits
###### [Credits](./CREDITS.md)



<!-- 
### ⚠️ **Dos and Don’ts**

*   **✅ DO** create profiles from within the app before starting a storm for the first time. The app needs to know about your YouTube accounts.
*   **✅ DO** monitor your RAM usage, especially when running a large number of channels.
*   **❌ DO NOT** close the browser windows manually while a storm is in progress. Use the "Stop" button in the UI.
*   **❌ DO NOT** interrupt the profile creation process. It can lead to corrupted profiles. If it fails, use the "Delete All Profiles" feature and try again.
*   **⚠️ Acknowledgment**: Automating user interactions on platforms like YouTube can be against their Terms of Service. Use this tool responsibly. The developers are not responsible for any account suspension or action taken against you. -->
