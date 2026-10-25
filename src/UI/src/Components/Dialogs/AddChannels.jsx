import { useEffect, useState } from "react";
import { Avatar, Button, Checkbox, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, LinearProgress, List, ListItem, useColorScheme } from "@mui/material";
import { logEvent } from "firebase/analytics";

import * as atatus from "../../lib/atatus";

import "./Dialogs.css";
import ErrorText from "../Elements/ErrorText";
import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";
import { analytics } from "../../config/firebase";
import { useAppState } from "../../context/AppStateContext";

const AddChannels = ({ payload, open, onClose }) => {
    const { mode, defaultSelectedChannels, systemInfoControls } = payload;
    const { btnProps } = useCustomMUIProps();

    const { colorScheme } = useColorScheme();
    const { hostAddress } = useAppState();

    const [channelsData, setChannelsData] = useState([]);
    const [channelsDataLoading, setChannelsDataLoading] = useState(false);
    const [activeChannels, setActiveChannels] = useState([]);
    const [selectedChannels, setSelectedChannels] = useState(defaultSelectedChannels || []);
    const [maxSelectableChannels, setMaxSelectableChannels] = useState(0);
    const [errorText, setErrorText] = useState("");

    const getChannelData = () => {
        setChannelsDataLoading(true);
        atatus.startOperation('fetch-channels-data', { mode });
        atatus.startDurationVital('fetch-channels-data');

        fetch(`${hostAddress}/storm/get_channels_data`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ mode }),
        })
            .then((response) => response.json())
            .then((data) => {
                atatus.stopDurationVital('fetch-channels-data');
                if (!data.success) {
                    atatus.failOperation('fetch-channels-data', data.error || data.message);
                    setErrorText(data.message || 'Failed to fetch channels data.');
                    if (data.error) {
                        console.error('Failed to fetch channels data:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['channel_data_fetch_failed'] });
                        atatus.stormLogger.error('Failed to fetch channels data', { response: data }, new Error(data.error));
                    }
                    return;
                }
                atatus.succeedOperation('fetch-channels-data');
                atatus.stormLogger.info('Channels data loaded', { count: Object.keys(data.channels || {}).length, mode });
                setChannelsData(data.channels);
                setActiveChannels(data.activeChannels);
            })
            .catch((error) => {
                atatus.stopDurationVital('fetch-channels-data');
                atatus.failOperation('fetch-channels-data', error.message);
                setErrorText("Failed to fetch channel data.");
                atatus.addError(error, { tags: ['channel_data_fetch_error'] });
                atatus.stormLogger.error('Network error fetching channels data', {}, error);
                logEvent(analytics, "channel_data_fetch_error");
            })
            .finally(() => {
                setChannelsDataLoading(false);
            });
    };

    const handleAddRemoveChannel = (event, channel) => {
        if (event.target.checked) {
            if (!selectedChannels.includes(channel)) {
                const next = [...selectedChannels, channel];
                setSelectedChannels(next);
                atatus.addAction('channel-checked', { channel, totalSelected: next.length });
            }
        } else {
            const next = selectedChannels.filter((name) => name !== channel);
            setSelectedChannels(next);
            atatus.addAction('channel-unchecked', { channel, totalSelected: next.length });
        }
    };

    const handleSubmit = () => {
        if (selectedChannels.length > maxSelectableChannels) {
            setErrorText(`You dont have enough RAM to select ${selectedChannels.length} channels. You can only select up to ${maxSelectableChannels} channels.`);
            atatus.addAction('channels-submit-rejected-ram', { selectedCount: selectedChannels.length, maxSelectableChannels });
            return;
        }
        if (selectedChannels.length === 0) {
            setErrorText("Select at least one channel.");
            atatus.addAction('channels-submit-rejected-empty');
            return;
        }

        atatus.addAction('channels-selection-confirmed', { mode, selectedChannels, count: selectedChannels.length });
        atatus.stormLogger.info('Channels selection confirmed', { mode, count: selectedChannels.length, selectedChannels });
        onClose(selectedChannels.map((channel) => parseInt(channel)));
    };


    useEffect(() => {
        if (open) {
            atatus.setViewName('/dialog/select-channels');
            atatus.setViewContext({ mode, preselectedCount: selectedChannels.length });
            getChannelData();
        }
    }, [open, hostAddress]);


    useEffect(() => {
        if (systemInfoControls.availableRAM) {
            const maxChannels = Math.floor(systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE);
            setMaxSelectableChannels(maxChannels);
        }
    }, [systemInfoControls.availableRAM, systemInfoControls.RAM_PER_PROFILE]);


    return (
        <Dialog
            open={open}
            fullWidth={true}
            maxWidth="xs"
            onClose={() => {
                atatus.addAction('channels-selection-cancelled');
                onClose(null);
            }}
            sx={{
                "& .MuiDialog-paper": {
                    backgroundColor: colorScheme === 'light' ? "var(--light-card-bg)" : "var(--light-gray)",
                    backgroundImage: "none",
                    borderRadius: "var(--border-radius)",
                },
            }}
        >
            <DialogTitle sx={{ display: "flex", flexDirection: "column" }}>
                {
                    mode === "new" ? "Select Channels to use" : "Add More Channels to Storm"
                }
                <span style={{ fontSize: "0.875rem", color: "var(--slight-light-text)" }}>
                    Select the channels you want to add to your storm.
                </span>
            </DialogTitle>
            <DialogContent>
                {
                    channelsDataLoading ? (
                        <LinearProgress />
                    ) : (
                        <div className="add-channels-dialog-content-container">
                            <span style={{ fontSize: "0.875rem", color: "var(--slight-light-text)" }}>
                                You have {systemInfoControls.availableRAM} MB of Free RAM, So you can select up to <strong>{maxSelectableChannels}</strong> channels.
                            </span>
                            <DialogContentText sx={{ marginTop: "1rem" }}>
                                Available Channels
                            </DialogContentText>
                            <div className={`available-channels-container ${colorScheme}-bordered-container`}>
                                <List>
                                    {
                                        Object.keys(channelsData).map((channel) => {
                                            return (
                                                <ListItem
                                                    key={channel}
                                                    sx={{
                                                        "&.MuiListItem-root": {
                                                            width: "100%",
                                                        }
                                                    }}>
                                                    <Avatar src={channelsData[channel].logo} alt={channelsData[channel].name} />
                                                    <div style={{ flex: 1, marginLeft: '1rem', display: 'flex' }} >

                                                        <span className='channel-name'>{channelsData[channel].name}</span>
                                                    </div>
                                                    <Checkbox
                                                        checked={activeChannels.includes(parseInt(channel)) || selectedChannels.includes(channel)}
                                                        disabled={activeChannels.includes(parseInt(channel))}
                                                        onChange={(event) => handleAddRemoveChannel(event, channel)}
                                                    />
                                                </ListItem>
                                            )
                                        }

                                        )
                                    }

                                </List>

                            </div>

                            <DialogContentText sx={{ marginTop: "1rem" }}>
                                Selected Channels
                            </DialogContentText>

                            <div className={`selected-channels-container ${colorScheme}-bordered-container`}>
                                {
                                    selectedChannels.sort((a, b) => a - b).map((channel) => (
                                        <span key={channel}>

                                            {`${channel}. ${channelsData[channel]?.name}`}
                                        </span>
                                    ))
                                }

                            </div>

                            <DialogContentText sx={{ fontSize: "0.7rem" }}>
                                Total Channels Selected: {selectedChannels.length}
                            </DialogContentText>

                            <ErrorText errorText={errorText} />

                        </div>

                    )
                }

            </DialogContent>
            <DialogActions>
                <Button
                    variant="outlined"
                    onClick={() => {
                        atatus.addAction('channels-selection-cancelled');
                        onClose(null);
                    }}
                    data-atatus-action-name="Cancel Add Channels"
                    sx={btnProps}
                >
                    Cancel
                </Button>
                <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={channelsDataLoading || selectedChannels.length === 0}
                    data-atatus-action-name="Confirm Add Channels"
                    sx={{
                        ...btnProps,
                        backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                        '&:hover': {
                            backgroundColor: colorScheme === 'light' ? "var(--light-primary-hover)" : "var(--input-active-red-dark-hover)",
                        },
                    }}
                >
                    Confirm
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddChannels;
