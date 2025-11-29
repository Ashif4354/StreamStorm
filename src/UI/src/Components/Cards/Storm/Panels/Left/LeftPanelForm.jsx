import { useColorScheme } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';
import { Button, Radio, RadioGroup } from "@mui/material";
import { useDialogs } from "@toolpad/core/useDialogs";

import "./LeftPanel.css";
import AddChannels from "../../../../Dialogs/AddChannels";
import ErrorText from "../../../../Elements/ErrorText";
import { useStormData } from "../../../../../context/StormDataContext";
import { useCustomMUIProps } from "../../../../../context/CustomMUIPropsContext";
import { useSystemInfo } from '../../../../../context/SystemInfoContext';
import { useAppState } from '../../../../../context/AppStateContext';

const LeftPanelForm = () => {

    const { colorScheme } = useColorScheme();
    const { inputProps, btnProps } = useCustomMUIProps();
    const formControls = useStormData();
    const systemInfoControls = useSystemInfo();
    const dialogs = useDialogs();
    const appState = useAppState();

    const messagesChangeHandler = (e) => {
        // sourcery skip: use-object-destructuring
        const value = e.target.value;
        formControls.setMessagesString(value);

        let allMessages = value.split('\n').filter((message) => {
            return message !== '';
        });

        allMessages = allMessages.map((message) => message.trim())

        formControls.setMessages(allMessages);
        formControls.setMessagesError(false);
        formControls.setMessagesHelperText("");
    }

    const handleURLChange = (e) => {
        let value = e.target.value.trim();
        if (value.includes("youtu.be/")) {
            value = value.replace("youtu.be/", "youtube.com/watch?v=");
        }
        if (value.startsWith("https://youtube.com")) {
            value = value.replace("https://youtube.com", "https://www.youtube.com");
        }
        formControls.setVideoURL(value);
        formControls.setVideoURLError(false);
        formControls.setVideoURLHelperText("");
    }

    const handleAdvancedChannelSelection = async () => {

        const selectedChannels = await dialogs.open(AddChannels, {
            mode: "new",
            formControls,
            defaultSelectedChannels: formControls.advancedSelectedChannels.map((channel) => channel.toString()),
            systemInfoControls
        });

        if (!selectedChannels || selectedChannels.length === 0) {
            return;
        }

        formControls.setAdvancedSelectedChannels(selectedChannels);

    }





    return (
        <div className="left-panel-form-container">
            <TextField
                variant="outlined"
                sx={inputProps}
                label="Video URL"
                value={formControls.videoURL}
                onChange={handleURLChange}
                error={formControls.videoURLError}
                helperText={formControls.videoURLHelperText}
                disabled={appState.stormInProgress || formControls.loading}
            />

            <TextField
                multiline
                rows={4}
                variant="outlined"
                label="Messages"
                sx={inputProps}
                value={formControls.messagesString}
                onChange={messagesChangeHandler}
                error={formControls.messagesError}
                helperText={formControls.messagesHelperText}
                disabled={appState.stormInProgress || formControls.loading}
            />

            <div className="left-panel-switches-container">
                <div className={`switch-container ${colorScheme}-bordered-container`}>
                    <span className="switch-label">Subscribe</span>
                    <Switch
                        checked={formControls.subscribe}
                        disabled={appState.stormInProgress || formControls.loading}
                        onChange={(e) => {
                            if (!e.target.checked) {
                                formControls.setSubscribeAndWait(false);
                            }
                            formControls.setSubscribe(e.target.checked);
                        }}
                    />
                </div>
                <div className={`switch-container ${colorScheme}-bordered-container`}>
                    <span className="switch-label">Subscribe & Wait</span>
                    <Switch
                        checked={formControls.subscribeAndWait}
                        disabled={appState.stormInProgress || formControls.loading}
                        onChange={(e) => {
                            if (e.target.checked) {
                                formControls.setSubscribe(true);
                            }
                            formControls.setSubscribeAndWait(e.target.checked);
                        }}
                    />
                </div>
            </div>

            <div className="times-input-container">
                <TextField
                    type="number"
                    variant="outlined"
                    label="Slow Mode (s)"
                    sx={inputProps}
                    value={formControls.slowMode}
                    onChange={(e) => {
                        formControls.setSlowMode(parseInt(e.target.value));
                        formControls.setSlowModeError(false);
                        formControls.setSlowModeHelperText("");
                    }}
                    error={formControls.slowModeError}
                    helperText={formControls.slowModeHelperText}
                    disabled={appState.stormInProgress || formControls.loading}
                />

                {
                    formControls.subscribeAndWait ? (
                        <TextField
                            type="number"
                            variant="outlined"
                            label="Subscribe & Wait Time (s)"
                            sx={inputProps}
                            value={formControls.subscribeWaitTime}
                            onChange={(e) => {
                                formControls.setSubscribeWaitTime(parseInt(e.target.value));
                                formControls.setSubscribeWaitTimeError(false);
                                formControls.setSubscribeWaitTimeHelperText("");
                            }}
                            error={formControls.subscribeWaitTimeError}
                            helperText={formControls.subscribeWaitTimeHelperText}
                            disabled={appState.stormInProgress || formControls.loading}
                        />
                    ) : null

                }

            </div>

            <div className="channel-index-inputs-container">
                <span className="channel-index-input-heading">Channels Selection</span>

                <div className="channel-index-input-radio-container">
                    <RadioGroup
                        row
                        defaultValue="basic"
                        name="channel-index-radio-group"
                        onChange={(e) => formControls.setChannelSelection(e.target.value)}
                        disabled={appState.stormInProgress || formControls.loading}
                    >
                        <div className="channel-index-radio-container">
                            <Radio
                                value="basic"
                                checked={formControls.channelSelection === "basic"}
                                disabled={appState.stormInProgress || formControls.loading}
                            />
                            <span className="channel-index-input-label">Basic</span>
                        </div>
                        <div className="channel-index-radio-container">
                            <Radio
                                value="intermediate"
                                checked={formControls.channelSelection === "intermediate"}
                                disabled={appState.stormInProgress || formControls.loading}
                            />
                            <span className="channel-index-input-label">Intermediate</span>
                        </div>
                        <div className="channel-index-radio-container">
                            <Radio
                                value="advanced"
                                checked={formControls.channelSelection === "advanced"}
                                disabled={appState.stormInProgress || formControls.loading}
                            />
                            <span className="channel-index-input-label">Advanced</span>
                        </div>
                    </RadioGroup>
                </div>
                {
                    formControls.channelSelection === "basic" ? (
                        <div className="channel-selection-basic-container">
                            <TextField
                                type="number"
                                // defaultValue={1}
                                variant="outlined"
                                label="No.of Channels"
                                className="channel-index-input"
                                sx={inputProps}
                                value={formControls.noOfChannels}
                                onChange={(e) => {
                                    formControls.setNoOfChannels(parseInt(e.target.value));
                                    formControls.setNoOfChannelsError(false);
                                    formControls.setNoOfChannelsHelperText("");
                                }}
                                error={formControls.noOfChannelsError}
                                helperText={formControls.noOfChannelsHelperText}
                                disabled={appState.stormInProgress || formControls.loading}

                            />
                        </div>
                    ) : (
                        <div>
                            {
                                formControls.channelSelection === "intermediate" ? (
                                    <div className="channel-selection-intermediate-container">
                                        <TextField
                                            type="number"
                                            defaultValue={1}
                                            variant="outlined"
                                            label="Start Channel Index"
                                            className="channel-index-input"
                                            sx={inputProps}
                                            value={formControls.startChannelIndex}
                                            onChange={(e) => {
                                                formControls.setStartChannelIndex(parseInt(e.target.value));
                                                formControls.setStartChannelIndexError(false);
                                                formControls.setStartChannelIndexHelperText("");
                                            }}
                                            error={formControls.startChannelIndexError}
                                            helperText={formControls.startChannelIndexHelperText}
                                            disabled={appState.stormInProgress || formControls.loading}
                                        />
                                        <TextField
                                            type="number"
                                            // defaultValue={5}
                                            variant="outlined"
                                            label="End Channel Index"
                                            className="channel-index-input"
                                            sx={inputProps}
                                            value={formControls.endChannelIndex}
                                            onChange={(e) => {
                                                formControls.setEndChannelIndex(parseInt(e.target.value));
                                                formControls.setEndChannelIndexError(false);
                                                formControls.setEndChannelIndexHelperText("");
                                            }}
                                            error={formControls.endChannelIndexError}
                                            helperText={formControls.endChannelIndexHelperText}
                                            disabled={appState.stormInProgress || formControls.loading}
                                        />
                                    </div>
                                ) : (
                                    <div className="channel-selection-advanced-container">
                                        <div className="row">
                                            <Button
                                                variant="contained"
                                                className="channel-index-input"
                                                onClick={handleAdvancedChannelSelection}
                                                disabled={appState.stormInProgress || formControls.loading}
                                                sx={{
                                                    ...btnProps,
                                                    width: "100px",
                                                    margin: "0",
                                                }}
                                            >
                                                Select
                                            </Button>
                                            <TextField
                                                fullWidth
                                                variant="outlined"
                                                size="small"
                                                placeholder="Click 'Select' to choose"

                                                value={formControls.advancedSelectedChannels.join(', ')}
                                                sx={{
                                                    ...inputProps,
                                                }}
                                            />
                                        </div>
                                        <span style={{ fontSize: "0.7rem", color: "var(--slight-light-text)" }}>
                                            Total Channels Selected: {formControls.advancedSelectedChannels.length}
                                        </span>


                                        <ErrorText errorText={formControls.advancedChannelsErrorText} />


                                    </div>
                                )
                            }
                        </div>
                    )
                }
                {
                    formControls.channelSelection === "intermediate" ? (
                        <span className='channel-selection-note'>
                            Note: Index starts from 1, and the end index is inclusive.
                        </span>
                    ) : null

                }


            </div>
        </div>

    );
}

export default LeftPanelForm;
