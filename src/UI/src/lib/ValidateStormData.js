import * as atatus from "./atatus";

const ValidateStormData = (formControls, systemInfoControls) => {
    let isValid = true;

    if (!formControls.videoURL) {
        isValid = false;
        formControls.setVideoURLError(true);
        formControls.setVideoURLHelperText("Video URL is required.");
        atatus.addAction('validation-failed', { field: 'videoURL', reason: 'Video URL is required' });
        atatus.validationLogger.warn("Validation failed: Video URL is required");
    } else {
        try {
            let url = new URL(formControls.videoURL);

            if (url.hostname != "www.youtube.com") {
                isValid = false;
                formControls.setVideoURLError(true);
                formControls.setVideoURLHelperText("Invalid Video URL. Must be a YouTube link.");
                atatus.addAction('validation-failed', { field: 'videoURL', reason: 'Hostname must be www.youtube.com', value: formControls.videoURL });
                atatus.validationLogger.warn("Validation failed: Not a YouTube link", { value: formControls.videoURL });
            } else if (!url.search.startsWith('?v=')) {
                isValid = false;
                formControls.setVideoURLError(true);
                formControls.setVideoURLHelperText("Invalid Youtube Video Link.");
                atatus.addAction('validation-failed', { field: 'videoURL', reason: 'Missing ?v= parameter', value: formControls.videoURL });
                atatus.validationLogger.warn("Validation failed: Missing video ID (?v=)", { value: formControls.videoURL });
            } else if (url.pathname != "/watch") {
                isValid = false;
                formControls.setVideoURLError(true);
                formControls.setVideoURLHelperText("Invalid Youtube Video Link.");
                atatus.addAction('validation-failed', { field: 'videoURL', reason: 'Pathname is not /watch', value: formControls.videoURL });
                atatus.validationLogger.warn("Validation failed: Pathname is not /watch", { value: formControls.videoURL });
            }
        } catch (e) {
            atatus.addError(e, { tags: ['video_url_validation_error'], videoURL: formControls.videoURL });
            atatus.validationLogger.error("URL parse error during validation", { videoURL: formControls.videoURL }, e);
            isValid = false;
            formControls.setVideoURLError(true);
            formControls.setVideoURLHelperText("Invalid Video URL.");
        }
    }

    if (formControls.messages.length === 0) {
        isValid = false;
        formControls.setMessagesError(true);
        formControls.setMessagesHelperText("At least one message is required.");
        atatus.addAction('validation-failed', { field: 'messages', reason: 'At least one message is required' });
        atatus.validationLogger.warn("Validation failed: At least one message is required");
    }

    if (isNaN(formControls.slowMode)) {
        isValid = false;
        formControls.setSlowModeError(true);
        formControls.setSlowModeHelperText("Enter a value for slow mode.");
        atatus.addAction('validation-failed', { field: 'slowMode', reason: 'Enter a value for slow mode' });
        atatus.validationLogger.warn("Validation failed: NaN slow mode");
    }

    if (formControls.slowMode < 1) {
        isValid = false;
        formControls.setSlowModeError(true);
        formControls.setSlowModeHelperText("Slow mode must be at least 1 seconds.");
        atatus.addAction('validation-failed', { field: 'slowMode', reason: 'Slow mode must be >= 1', value: formControls.slowMode });
        atatus.validationLogger.warn("Validation failed: Slow mode < 1", { value: formControls.slowMode });
    }

    if (formControls.subscribeAndWait) {
        if (isNaN(formControls.subscribeWaitTime)) {
            isValid = false;
            formControls.setSubscribeWaitTimeError(true);
            formControls.setSubscribeWaitTimeHelperText("Enter a valid number for subscribe wait time.");
            atatus.addAction('validation-failed', { field: 'subscribeWaitTime', reason: 'NaN wait time' });
            atatus.validationLogger.warn("Validation failed: NaN subscribe wait time");
        } else if (formControls.subscribeWaitTime < 1) {
            isValid = false;
            formControls.setSubscribeWaitTimeError(true);
            formControls.setSubscribeWaitTimeHelperText("Enter a valid number for subscribe wait time.");
            atatus.addAction('validation-failed', { field: 'subscribeWaitTime', reason: 'Wait time < 1', value: formControls.subscribeWaitTime });
            atatus.validationLogger.warn("Validation failed: Subscribe wait time < 1", { value: formControls.subscribeWaitTime });
        }
    }

    if (formControls.channelSelection === 'basic') {
        if (isNaN(formControls.noOfChannels)) {
            isValid = false;
            formControls.setNoOfChannelsError(true);
            formControls.setNoOfChannelsHelperText("Enter a valid number of channels.");
            atatus.addAction('validation-failed', { field: 'noOfChannels', reason: 'NaN channels' });
            atatus.validationLogger.warn("Validation failed: NaN number of channels");
        } else if (formControls.noOfChannels < 1) {
            isValid = false;
            formControls.setNoOfChannelsError(true);
            formControls.setNoOfChannelsHelperText("Number of channels must be at least 1.");
            atatus.addAction('validation-failed', { field: 'noOfChannels', reason: 'Channels < 1', value: formControls.noOfChannels });
            atatus.validationLogger.warn("Validation failed: Number of channels < 1", { value: formControls.noOfChannels });
        } else if (formControls.noOfChannels > (systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE)) {
            isValid = false;
            const maxChannels = Math.floor(systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE);
            formControls.setErrorText(`You can run a maximum of ${maxChannels} channels with your available RAM.`);
            atatus.addAction('validation-failed', { field: 'noOfChannels', reason: 'Insufficient RAM', requested: formControls.noOfChannels, maxChannels });
            atatus.validationLogger.warn("Validation failed: Insufficient RAM for channels", { requested: formControls.noOfChannels, maxChannels });
        }
    } else if (formControls.channelSelection === 'intermediate') {
        if (isNaN(formControls.startChannelIndex)) {
            isValid = false;
            formControls.setStartChannelIndexError(true);
            formControls.setStartChannelIndexHelperText("Enter a valid start channel index.");
            atatus.addAction('validation-failed', { field: 'startChannelIndex', reason: 'NaN start index' });
            atatus.validationLogger.warn("Validation failed: NaN start channel index");
        } else if (formControls.startChannelIndex < 1) {
            isValid = false;
            formControls.setStartChannelIndexError(true);
            formControls.setStartChannelIndexHelperText("Start channel index must be at least 1.");
            atatus.addAction('validation-failed', { field: 'startChannelIndex', reason: 'Start index < 1', value: formControls.startChannelIndex });
            atatus.validationLogger.warn("Validation failed: Start channel index < 1", { value: formControls.startChannelIndex });
        }
        
        if (isNaN(formControls.endChannelIndex)) {
            isValid = false;
            formControls.setEndChannelIndexError(true);
            formControls.setEndChannelIndexHelperText("Enter a valid end channel index.");
            atatus.addAction('validation-failed', { field: 'endChannelIndex', reason: 'NaN end index' });
            atatus.validationLogger.warn("Validation failed: NaN end channel index");
        } else if (formControls.endChannelIndex < formControls.startChannelIndex) {
            isValid = false;
            formControls.setEndChannelIndexError(true);
            formControls.setEndChannelIndexHelperText("End channel index cannot be less than start channel index.");
            atatus.addAction('validation-failed', { field: 'endChannelIndex', reason: 'End index < start index', start: formControls.startChannelIndex, end: formControls.endChannelIndex });
            atatus.validationLogger.warn("Validation failed: End channel index < start index", { start: formControls.startChannelIndex, end: formControls.endChannelIndex });
        }

        const totalChannels = formControls.endChannelIndex - formControls.startChannelIndex + 1;
        if (totalChannels > (systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE)) {
            isValid = false;
            const maxChannels = Math.floor(systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE);
            formControls.setErrorText(`You can run a maximum of ${maxChannels} channels with your available RAM.`);
            atatus.addAction('validation-failed', { field: 'rangeChannels', reason: 'Insufficient RAM for range', totalChannels, maxChannels });
            atatus.validationLogger.warn("Validation failed: Insufficient RAM for channel range", { totalChannels, maxChannels });
        }
    } else if (formControls.channelSelection === 'advanced') {
        if (formControls.advancedSelectedChannels.length === 0) {
            isValid = false;
            formControls.setAdvancedChannelsErrorText("Select at least one channel.");
            atatus.addAction('validation-failed', { field: 'advancedSelectedChannels', reason: 'Zero channels selected' });
            atatus.validationLogger.warn("Validation failed: Zero advanced channels selected");
        }
    }

    if (isValid) {
        atatus.addAction('storm-validation-passed', {
            videoURL: formControls.videoURL,
            messagesCount: formControls.messages.length,
            slowMode: formControls.slowMode,
            channelSelection: formControls.channelSelection,
        });
        atatus.validationLogger.info("Storm data validated successfully");
    }

    return isValid;
};

export default ValidateStormData;
