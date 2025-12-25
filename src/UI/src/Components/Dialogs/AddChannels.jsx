import { useEffect, useState } from "react";
import { Avatar, Button, Checkbox, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, LinearProgress, List, ListItem, useColorScheme } from "@mui/material";
import { logEvent } from "firebase/analytics";

import * as atatus from "atatus-spa";

import "./Dialogs.css";
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import ErrorText from "../Elements/ErrorText";
import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";
import { analytics } from "../../config/firebase";

const AddChannels = ({ payload, open, onClose }) => {
    const { mode, defaultSelectedChannels, systemInfoControls } = payload;
    const { btnProps } = useCustomMUIProps();

    const { colorScheme } = useColorScheme();
    const [hostAddress] = useLocalStorageState('hostAddress');

    const [channelsData, setChannelsData] = useState([]);
    const [channelsDataLoading, setChannelsDataLoading] = useState(false);
    const [activeChannels, setActiveChannels] = useState([]);
    const [selectedChannels, setSelectedChannels] = useState(defaultSelectedChannels || []);
    const [maxSelectableChannels, setMaxSelectableChannels] = useState(0);
    const [errorText, setErrorText] = useState("");

    const getChannelData = () => {
        setChannelsDataLoading(true);
        fetch(`${hostAddress}/storm/get_channels_data`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ mode }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (!data.success) {
                    setErrorText(data.message || "Failed to fetch channels data.");
                    return;
                }
                setChannelsData(data.channels);
                setActiveChannels(data.activeChannels);
            })
            .catch((error) => {
                setErrorText("Failed to fetch channel data.");
                atatus.notify(error, {}, ['channel_data_fetch_error']);
                logEvent(analytics, "channel_data_fetch_error");
            })
            .finally(() => {
                setChannelsDataLoading(false);
            });
    };

    const handleAddRemoveChannel = (event, channel) => {
        if (event.target.checked) {
            if (!selectedChannels.includes(channel)) {
                setSelectedChannels([...selectedChannels, channel]);
            }
        } else {
            setSelectedChannels(selectedChannels.filter((name) => name !== channel));
        }
    };

    const handleSubmit = () => {
        if (selectedChannels.length > maxSelectableChannels) {
            setErrorText(`You dont have enough RAM to select ${selectedChannels.length} channels. You can only select up to ${maxSelectableChannels} channels.`);
            return;
        }
        if (selectedChannels.length === 0) {
            setErrorText("Select at least one channel.");
            return;
        }

        onClose(selectedChannels.map((channel) => parseInt(channel)));
    };


    useEffect(() => {
        if (open) {
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
            onClose={() => onClose(null)}
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
                                {/* <span>
                                    {
                                        selectedChannels.map((channel) => `${channelsData[channel].name}, `)
                                    }
                                </span> */}
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
                        onClose(null);
                    }}
                    sx={btnProps}
                >
                    Cancel
                </Button>
                <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={channelsDataLoading || selectedChannels.length === 0}
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
    )
}

export default AddChannels;