import { safeLogEvent as logEvent } from '../config/safeAnalytics.js';
import ValidateStormData from "./ValidateStormData";
import { analytics } from "../config/firebase";
import * as atatus from "./atatus";

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
        if (stormData.subscribe) { logEvent(analytics, "subscribe"); }
        if (stormData.subscribe_and_wait) { logEvent(analytics, "subscribe_and_wait"); }
        if (stormData.subscribe_and_wait_time) { logEvent(analytics, "subscribe_and_wait_time", { time: stormData.subscribe_and_wait_time }); }
        if (stormData.slow_mode != 5) { logEvent(analytics, "slow_mode_change", { time: stormData.slow_mode }); }
        if (stormData.background) { logEvent(analytics, "background_load"); }
        logEvent(analytics, "channel_count", { count: stormData.channels.length });
        logEvent(analytics, "channel_selection_mode", { mode: stormData.channelSelection });
    }

    startStorm(formControls, systemInfoControls, appState) {
        const dataValid = ValidateStormData(formControls, systemInfoControls);

        if (!dataValid) {
            atatus.stormLogger.warn("Storm start aborted: validation failed");
            return;
        }

        const stormData = formControls.getStormData();
        this.log_analytics(stormData);

        atatus.startOperation('start-storm', { channelsCount: stormData.channels.length });
        atatus.startDurationVital('start-storm');
        atatus.addAction('storm-start-requested', {
            videoUrl: stormData.videoUrl,
            channelsCount: stormData.channels.length,
            slowMode: stormData.slowMode,
            subscribe: stormData.subscribe,
            background: stormData.background,
        });

        formControls.setLoading(true);

        fetch(`${this.hostAddress}/storm/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(stormData),
        })
            .then(response => response.json())
            .then(data => {
                atatus.stopDurationVital('start-storm');
                if (data.success) {
                    atatus.succeedOperation('start-storm');
                    atatus.stormLogger.info('Storm started successfully', {
                        channelsCount: data.channels?.length || stormData.channels.length,
                    });
                    this.notifications.show('Storm started successfully!', {
                        severity: 'success',
                    });
                    appState.setAllChannels(data.channels);
                    appState.setStormInProgress(true);
                    appState.setStormStatus("in Progress");
                    logEvent(analytics, "storm_started");
                } else {
                    atatus.failOperation('start-storm', data.error || data.message || 'Request failed');
                    formControls.setErrorText(data.message || 'Request failed');
                    this.notifications.show("Failed to start storm", {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to start storm:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['storm_start_failed'] });
                        atatus.stormLogger.error('Failed to start storm', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "storm_start_failed");
                }
            })
            .catch(error => {
                atatus.stopDurationVital('start-storm');
                atatus.failOperation('start-storm', error.message);
                this.notifications.show(error.message || 'An error occurred while starting the storm', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_start_error'] });
                atatus.stormLogger.error('Error starting storm', {}, error);
                logEvent(analytics, "storm_start_error");
            })
            .finally(() => {
                formControls.setLoading(false);
            });
    }

    stopStorm(setStormInProgress) {
        this.setStopping(true);
        this.setControlsDisabled(true);

        atatus.startOperation('stop-storm');
        atatus.startDurationVital('stop-storm');
        atatus.addAction('storm-stop-requested');

        fetch(`${this.hostAddress}/storm/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                atatus.stopDurationVital('stop-storm');
                if (data.success) {
                    atatus.succeedOperation('stop-storm');
                    atatus.stormLogger.info('Storm stopped successfully');
                    setStormInProgress(false);
                    this.notifications.show('Storm stopped successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "storm_stopped");
                } else {
                    atatus.failOperation('stop-storm', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to stop the storm', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to stop storm:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['storm_stop_failed'] });
                        atatus.stormLogger.error('Failed to stop storm', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "storm_stop_failed");
                }

            })
            .catch(error => {
                atatus.stopDurationVital('stop-storm');
                atatus.failOperation('stop-storm', error.message);
                this.notifications.show('An error occurred while stopping the storm', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_stop_error'] });
                atatus.stormLogger.error('Error stopping storm', {}, error);
                logEvent(analytics, "storm_stop_error");
            })
            .finally(() => {
                this.setStopping(false);
                this.setControlsDisabled(false);
            });
    }

    stopStorm2(setStopping) {
        setStopping(true);

        atatus.startOperation('stop-storm-auxiliary');
        atatus.addAction('storm-aux-stop-requested');

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
                    atatus.succeedOperation('stop-storm-auxiliary');
                    atatus.stormLogger.info('Auxiliary storm stopped successfully');
                    logEvent(analytics, "storm_stopped_2");
                } else {
                    atatus.failOperation('stop-storm-auxiliary', data.error || data.message);
                    if (data.error) {
                        console.error('Failed to stop storm (2):', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['storm_stop_2_failed'] });
                        atatus.stormLogger.error('Failed to stop storm (2)', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "storm_stop_2_failed");
                }

            })
            .catch(error => {
                atatus.failOperation('stop-storm-auxiliary', error.message);
                atatus.addError(error, { tags: ['storm_stop_2_error'] });
                atatus.stormLogger.error('Error in auxiliary storm stop', {}, error);
                logEvent(analytics, "storm_stop_2_error");
            })
            .finally(() => {
                setStopping(false);
            });
    }

    pauseStorm() {
        this.setPausing(true);
        this.setControlsDisabled(true);

        atatus.startOperation('pause-storm');
        atatus.addAction('storm-pause-requested');

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
                    atatus.succeedOperation('pause-storm');
                    atatus.stormLogger.info('Storm paused successfully');
                    this.notifications.show('Storm paused successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "storm_paused");
                } else {
                    atatus.failOperation('pause-storm', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to pause the storm', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to pause storm:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['storm_pause_failed'] });
                        atatus.stormLogger.error('Failed to pause storm', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "storm_pause_failed");
                }
            })
            .catch(error => {
                atatus.failOperation('pause-storm', error.message);
                this.notifications.show('An error occurred while pausing the storm', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_pause_error'] });
                atatus.stormLogger.error('Error pausing storm', {}, error);
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

        atatus.startOperation('resume-storm');
        atatus.addAction('storm-resume-requested');

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
                    atatus.succeedOperation('resume-storm');
                    atatus.stormLogger.info('Storm resumed successfully');
                    this.notifications.show('Storm resumed successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "storm_resumed");
                } else {
                    atatus.failOperation('resume-storm', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to resume the storm', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to resume storm:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['storm_resume_failed'] });
                        atatus.stormLogger.error('Failed to resume storm', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "storm_resume_failed");
                }
            })
            .catch(error => {
                atatus.failOperation('resume-storm', error.message);
                this.notifications.show('An error occurred while resuming the storm', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_resume_error'] });
                atatus.stormLogger.error('Error resuming storm', {}, error);
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

        atatus.startOperation('dont-wait');
        atatus.addAction('storm-dont-wait-requested');

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
                    atatus.succeedOperation('dont-wait');
                    atatus.stormLogger.info('Dont-wait mode activated');
                    this.notifications.show('Each channel will start storming without waiting for others!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "dont_wait");
                } else {
                    atatus.failOperation('dont-wait', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to set dont-wait', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to set dont-wait:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['dont_wait_failed'] });
                        atatus.stormLogger.error('Failed to set dont-wait', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "dont_wait_failed");
                }
            })
            .catch(error => {
                atatus.failOperation('dont-wait', error.message);
                this.notifications.show('An error occurred while setting dont-wait', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_dont_wait_error'] });
                atatus.stormLogger.error('Error setting dont-wait', {}, error);
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

        atatus.startOperation('change-messages', { count: messages.length });
        atatus.addAction('storm-change-messages-requested', { count: messages.length, messages });

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
                    atatus.succeedOperation('change-messages');
                    atatus.stormLogger.info('Messages changed successfully in ongoing storm', { count: messages.length });
                    this.notifications.show('Messages changed successfully!', {
                        severity: 'success',
                    });
                    setMessages(messages);
                    setMessagesString(messages.join('\n'));
                    logEvent(analytics, "change_messages");
                } else {
                    atatus.failOperation('change-messages', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to change messages', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to change messages:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['change_messages_failed'] });
                        atatus.stormLogger.error('Failed to change messages', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "change_messages_failed");
                }
            })
            .catch(error => {
                atatus.failOperation('change-messages', error.message);
                this.notifications.show('An error occurred while changing messages', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_change_messages_error'] });
                atatus.stormLogger.error('Error changing messages', {}, error);
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

        atatus.startOperation('change-slow-mode', { slowMode: slowModeValue });
        atatus.addAction('storm-change-slow-mode-requested', { slowMode: slowModeValue });

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
                    atatus.succeedOperation('change-slow-mode');
                    atatus.stormLogger.info('Slow mode updated successfully', { slowMode: slowModeValue });
                    this.notifications.show('Slow mode changed successfully!', {
                        severity: 'success',
                    });
                    setSlowMode(slowModeValue);
                    logEvent(analytics, "change_slow_mode");
                } else {
                    atatus.failOperation('change-slow-mode', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to change slow mode', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to change slow mode:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['change_slow_mode_failed'] });
                        atatus.stormLogger.error('Failed to change slow mode', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "change_slow_mode_failed");
                }
            })
            .catch(error => {
                atatus.failOperation('change-slow-mode', error.message);
                this.notifications.show('An error occurred while changing slow mode', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_change_slow_mode_error'] });
                atatus.stormLogger.error('Error changing slow mode', {}, error);
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

        atatus.startOperation('start-more-channels', { count: channels.length });
        atatus.addAction('storm-start-more-channels-requested', { channels });

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
                    atatus.succeedOperation('start-more-channels');
                    atatus.stormLogger.info('Additional channels started successfully', { count: channels.length });
                    this.notifications.show('More channels started successfully!', {
                        severity: 'success',
                    });
                    logEvent(analytics, "start_more_channels");
                } else {
                    atatus.failOperation('start-more-channels', data.error || data.message);
                    this.notifications.show(data.message || 'Failed to start more channels', {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to start more channels:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['start_more_channels_failed'] });
                        atatus.stormLogger.error('Failed to start more channels', { response: data }, new Error(data.error));
                    }
                    logEvent(analytics, "start_more_channels_failed");
                }
            })
            .catch(error => {
                atatus.failOperation('start-more-channels', error.message);
                this.notifications.show('An error occurred while starting more channels', {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['storm_start_more_channels_error'] });
                atatus.stormLogger.error('Error starting more channels', {}, error);
                logEvent(analytics, "start_more_channels_error");
            })
            .finally(() => {
                this.setMoreChannelsLoading(false);
                this.setControlsDisabled(false);
            });
    }

}

export default StormControlsClass;
