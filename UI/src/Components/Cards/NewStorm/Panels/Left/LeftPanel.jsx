import { useState, useContext } from "react";
import { useColorScheme } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';
import { Radio, RadioGroup } from "@mui/material";

import "./LeftPanel.css";
import { CustomMUIPropsContext, StormDataContext } from "../../../../../lib/ContextAPI";

const LeftPanel = () => {

    const { colorScheme } = useColorScheme();
    const { inputProps } = useContext(CustomMUIPropsContext);
    const formControls = useContext(StormDataContext);

    const messagesChangeHandler = (e) => {
        const value = e.target.value;
        formControls.setMessagesString(value);

        const allMessages = value.split('\n').filter((message) => {
            return message !== '';
        });

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
        formControls.setVideoURLHelperText("Enter the URL of the video to be used in the storm.");
    }



    return (
        <div className="left-panel-container">
            <TextField
                variant="outlined"
                sx={inputProps}
                label="Video URL"
                value={formControls.videoURL}
                onChange={handleURLChange}
                error={formControls.videoURLError}
                helperText={formControls.videoURLHelperText}
                disabled={formControls.stormInProgress || formControls.loading}
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
                disabled={formControls.stormInProgress || formControls.loading}
            />

            <div className="left-panel-switches-container">
                <div className={`switch-container ${colorScheme}-bordered-container`}>
                    <span className="switch-label">Subscribe</span>
                    <Switch
                        checked={formControls.subscribe}
                        disabled={formControls.stormInProgress || formControls.loading}
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
                        disabled={formControls.stormInProgress || formControls.loading}
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
                {
                    formControls.subscribeAndWait ? (
                        <TextField
                            type="number"
                            variant="outlined"
                            label="Subscribe & Wait Time (s)"
                            sx={inputProps}
                            onChange={(e) => {
                                formControls.setSubscribeWaitTime(parseInt(e.target.value));
                                formControls.setSubscribeWaitTimeError(false);
                                formControls.setSubscribeWaitTimeHelperText("");
                            }}
                            error={formControls.subscribeWaitTimeError}
                            helperText={formControls.subscribeWaitTimeHelperText}
                            disabled={formControls.stormInProgress || formControls.loading}
                        />
                    ) : null

                }

                <TextField
                    type="number"
                    variant="outlined"
                    label="Slow Mode (s)"
                    sx={inputProps}
                    onChange={(e) => {
                        formControls.setSlowMode(parseInt(e.target.value));
                        formControls.setSlowModeError(false);
                        formControls.setSlowModeHelperText("");
                    }}
                    error={formControls.slowModeError}
                    helperText={formControls.slowModeHelperText}
                    defaultValue={5}
                    disabled={formControls.stormInProgress || formControls.loading}
                />
            </div>

            <div className="account-index-inputs-container">
                <span className="account-index-input-heading">Accounts Selection</span>

                <div className="account-index-input-radio-container">
                    <RadioGroup
                        row
                        defaultValue="basic"
                        name="account-index-radio-group"
                        onChange={(e) => formControls.setAccountSelection(e.target.value)}
                        disabled={formControls.stormInProgress || formControls.loading}
                    >
                        <div className="account-index-radio-container">
                            <Radio
                                value="basic"
                                checked={formControls.accountSelection === "basic"}
                                disabled={formControls.stormInProgress || formControls.loading}
                            />
                            <span className="account-index-input-label">Basic</span>
                        </div>
                        <div className="account-index-radio-container">
                            <Radio
                                value="advanced"
                                checked={formControls.accountSelection === "advanced"}
                                disabled={formControls.stormInProgress || formControls.loading}
                            />
                            <span className="account-index-input-label">Advanced</span>
                        </div>
                    </RadioGroup>
                </div>
                {
                    formControls.accountSelection === "basic" ? (
                        <div className="account-selection-basic-container">
                            <TextField
                                type="number"
                                defaultValue={1}
                                variant="outlined"
                                label="No.of Accounts"
                                className="account-index-input"
                                sx={inputProps}
                                onChange={(e) => {
                                    formControls.setNoOfAccounts(parseInt(e.target.value));
                                    formControls.setNoOfAccountsError(false);
                                    formControls.setNoOfAccountsHelperText("");
                                }}
                                error={formControls.noOfAccountsError}
                                helperText={formControls.noOfAccountsHelperText}
                                disabled={formControls.stormInProgress || formControls.loading}

                            />
                        </div>
                    ) : (
                        <div className="account-selection-advanced-container">
                            <TextField
                                type="number"
                                defaultValue={1}
                                variant="outlined"
                                label="Start Account Index"
                                className="account-index-input"
                                sx={inputProps}
                                onChange={(e) => {
                                    formControls.setStartAccountIndex(parseInt(e.target.value));
                                    formControls.setStartAccountIndexError(false);
                                    formControls.setStartAccountIndexHelperText("");
                                }}
                                error={formControls.startAccountIndexError}
                                helperText={formControls.startAccountIndexHelperText}
                                disabled={formControls.stormInProgress || formControls.loading}
                            />
                            <TextField
                                type="number"
                                // defaultValue={5}
                                variant="outlined"
                                label="End Account Index"
                                className="account-index-input"
                                sx={inputProps}
                                onChange={(e) => {
                                    formControls.setEndAccountIndex(parseInt(e.target.value));
                                    formControls.setEndAccountIndexError(false);
                                    formControls.setEndAccountIndexHelperText("");
                                }}
                                error={formControls.endAccountIndexError}
                                helperText={formControls.endAccountIndexHelperText}
                                disabled={formControls.stormInProgress || formControls.loading}
                            />
                        </div>
                    )
                }
                {
                    formControls.accountSelection === "advanced" ? (
                        <span className='account-selection-note'>
                            Note: Index starts from 1, and the end index is inclusive.
                        </span>
                    ) : null

                }


            </div>
        </div>

    );
}

export default LeftPanel;
