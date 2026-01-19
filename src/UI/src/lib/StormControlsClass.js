import { logEvent } from "firebase/analytics";
import ValidateStormData from "./ValidateStormData";
import { analytics } from "../config/firebase";

import * as atatus from "atatus-spa"

class StormControlsClass {
    constructor(hostAddress) {
        this.hostAddress = hostAddress;
        this.notifications = null;
        this.setPausing = null;
        this.setStopping = null;
        this.setResuming = null;
        this.setControlsDisabled = null;
        this.setDontWaitLoading = null;
        this.setChangeMessagesLoading = null;
        this.setChangeSlowModeLoading = null;
        this.setMoreChannelsLoading = null;
    }

    log_analytics(stormData) {
        if (stormData.subscribe) { logEvent(analytics, "subscribe") }
        if (stormData.subscribe_and_wait) { logEvent(analytics, "subscribe_and_wait") }
        if (stormData.subscribe_and_wait_time) { logEvent(analytics, "subscribe_and_wait_time", { time: stormData.subscribe_and_wait_time }) }
        if (stormData.slow_mode != 5) { logEvent(analytics, "slow_mode_change", { time: stormData.slow_mode }) }
        if (stormData.background) { logEvent(analytics, "background_load") }
        logEvent(analytics, "channel_count", { count: stormData.channels.length });
        logEvent(analytics, "channel_selection_mode", { mode: stormData.channelSelection });
    }

    startStorm(formControls, systemInfoControls, appState) {
        // appState.setStormInProgress(true); // Comment this line in production
        // return; // Comment this line in production

        const dataValid = ValidateStormData(formControls, systemInfoControls);

        if (!dataValid) {
            return;
        }

        const stormData = formControls.getStormData();
        this.log_analytics(stormData);

        formControls.setLoading(true);
        // this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(stormData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('Storm started successfully!', {
                        severity: 'success',
                    });
                    appState.setAllChannels(data.channels);
                    // this.setControlsDisabled(false);
                    appState.setStormInProgress(true);
                    appState.setStormStatus("in Progress");
                    logEvent(analytics, "storm_started");
                } else {
                    formControls.setErrorText(data.message || 'Request failed');
                    this.notifications.show("Failed to start storm", {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to start storm:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['storm_start_failed']);
                    }
                    logEvent(analytics, "storm_start_failed");
                }
            })
            .catch(error => {
                this.notifications.show(error.message || 'An error occurred while starting the storm', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_start_error']);
                logEvent(analytics, "storm_start_error");
            })
            .finally(() => {
                formControls.setLoading(false);
                // this.setControlsDisabled(false);
            });
    }

    stopStorm(setStormInProgress) {
        this.setStopping(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    setStormInProgress(false);
                    this.notifications.show('Storm stopped successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "storm_stopped");
                } else {
                    this.notifications.show(data.message || 'Failed to stop the storm', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to stop storm:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['storm_stop_failed']);
                    }
                    logEvent(analytics, "storm_stop_failed");
                }

            })
            .catch(error => {
                this.notifications.show('An error occurred while stopping the storm', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_stop_error']);
                logEvent(analytics, "storm_stop_error");
            })
            .finally(() => {
                this.setStopping(false);
                this.setControlsDisabled(false);
            });

    }

    stopStorm2(setStopping) {
        setStopping(true);

        fetch(`${this.hostAddress}/storm/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    logEvent(analytics, "storm_stopped_2");
                } else {
                    if (data.error) {
                        console.error('Failed to stop storm (2):', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['storm_stop_2_failed']);
                    }
                    logEvent(analytics, "storm_stop_2_failed");
                }

            })
            .catch(error => {
                atatus.notify(error, {}, ['storm_stop_2_error']);
                logEvent(analytics, "storm_stop_2_error");
            })
            .finally(() => {
                setStopping(false);
            });

    }

    pauseStorm() {
        this.setPausing(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/pause`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('Storm paused successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "storm_paused");
                } else {
                    this.notifications.show(data.message || 'Failed to pause the storm', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to pause storm:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['storm_pause_failed']);
                    }
                    logEvent(analytics, "storm_pause_failed");
                }
            })
            .catch(error => {
                this.notifications.show('An error occurred while pausing the storm', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_pause_error']);
                logEvent(analytics, "storm_pause_error");
            })
            .finally(() => {
                this.setPausing(false);
                this.setControlsDisabled(false);
            });
    }


    resumeStorm() {
        this.setResuming(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/resume`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('Storm resumed successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "storm_resumed");
                } else {
                    this.notifications.show(data.message || 'Failed to resume the storm', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to resume storm:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['storm_resume_failed']);
                    }
                    logEvent(analytics, "storm_resume_failed");
                }
            })
            .catch(error => {
                this.notifications.show('An error occurred while resuming the storm', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_resume_error']);
                logEvent(analytics, "storm_resume_error");
            })
            .finally(() => {
                this.setResuming(false);
                this.setControlsDisabled(false);
            });
    }

    dontWait() {
        this.setDontWaitLoading(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/start_storm_dont_wait`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('Each channel will start storming without waiting for others!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "dont_wait");
                } else {
                    this.notifications.show(data.message || 'Failed to set dont-wait', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to set dont-wait:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['dont_wait_failed']);
                    }
                    logEvent(analytics, "dont_wait_failed");
                }
            })
            .catch(error => {
                this.notifications.show('An error occurred while setting dont-wait', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_dont_wait_error']);
                logEvent(analytics, "dont_wait_error");
            })
            .finally(() => {
                this.setDontWaitLoading(false);
                this.setControlsDisabled(false);
            });
    }

    changeMessages(messages, setMessages, setMessagesString) {

        this.setChangeMessagesLoading(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/change_messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ messages }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('Messages changed successfully!', {
                        severity: 'success',
                    });
                    setMessages(messages);
                    setMessagesString(messages.join('\n'));
                    logEvent(analytics, "change_messages");
                } else {
                    this.notifications.show(data.message || 'Failed to change messages', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to change messages:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['change_messages_failed']);
                    }
                    logEvent(analytics, "change_messages_failed");
                }
            })
            .catch(error => {
                this.notifications.show('An error occurred while changing messages', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_change_messages_error']);
                logEvent(analytics, "change_messages_error");
            })
            .finally(() => {
                this.setChangeMessagesLoading(false);
                this.setControlsDisabled(false);
            });
    }

    changeSlowMode(slowModeValue, setSlowMode) {
        this.setChangeSlowModeLoading(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/change_slow_mode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ slow_mode: slowModeValue }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('Slow mode changed successfully!', {
                        severity: 'success',
                    });
                    setSlowMode(slowModeValue);
                    logEvent(analytics, "change_slow_mode");
                } else {
                    this.notifications.show(data.message || 'Failed to change slow mode', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to change slow mode:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['change_slow_mode_failed']);
                    }
                    logEvent(analytics, "change_slow_mode_failed");
                }
            })
            .catch(error => {
                this.notifications.show('An error occurred while changing slow mode', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_change_slow_mode_error']);
                logEvent(analytics, "change_slow_mode_error");
            })
            .finally(() => {
                this.setChangeSlowModeLoading(false);
                this.setControlsDisabled(false);
            });
    }

    startMoreChannels(channels) {
        this.setMoreChannelsLoading(true);
        this.setControlsDisabled(true);

        fetch(`${this.hostAddress}/storm/start_more_channels`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ channels }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications.show('More channels started successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "start_more_channels");
                } else {
                    this.notifications.show(data.message || 'Failed to start more channels', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to start more channels:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['start_more_channels_failed']);
                    }
                    logEvent(analytics, "start_more_channels_failed");
                }
            })
            .catch(error => {
                this.notifications.show('An error occurred while starting more channels', {
                    severity: 'error',
                });
                atatus.notify(error, {}, ['storm_start_more_channels_error']);
                logEvent(analytics, "start_more_channels_error");
            })
            .finally(() => {
                this.setMoreChannelsLoading(false);
                this.setControlsDisabled(false);
            });
    }

}

export default StormControlsClass;