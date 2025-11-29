import { useState, useEffect, Fragment } from "react";
import { Button, Tooltip } from "@mui/material";
import { useColorScheme } from '@mui/material/styles';
import { Ban, Pause, Play, Plus, RefreshCw, SquarePen, StopCircle, Zap } from 'lucide-react';
import { useDialogs } from '@toolpad/core/useDialogs';

import "./StormControls.css";
import Ping from "../../../../../Elements/Ping/Ping";
import StormControlsClass from "../../../../../../lib/StormControlsClass";
import AreYouSure from "../../../../../Dialogs/AreYouSure";
import ChangeMessages from "../../../../../Dialogs/ChangeMessages";
import ChangeSlowMode from "../../../../../Dialogs/ChangeSlowMode";
import AddChannels from "../../../../../Dialogs/AddChannels";
import { useStormData } from "../../../../../../context/StormDataContext";
import { useCustomMUIProps } from "../../../../../../context/CustomMUIPropsContext";
import { useSystemInfo } from "../../../../../../context/SystemInfoContext";
import { useAppState } from "../../../../../../context/AppStateContext";

const StormControls = () => {

    const { btnProps } = useCustomMUIProps();
    const formControls = useStormData();
    const { colorScheme } = useColorScheme();
    const dialogs = useDialogs();
    const systemInfoControls = useSystemInfo();
    const appState = useAppState();

    const [pausing, setPausing] = useState(false);
    const [stopping, setStopping] = useState(false);
    const [resuming, setResuming] = useState(false);
    const [dontWaitLoading, setDontWaitLoading] = useState(false);
    const [changeMessagesLoading, setChangeMessagesLoading] = useState(false);
    const [changeSlowModeLoading, setChangeSlowModeLoading] = useState(false);
    const [moreChannelsLoading, setMoreChannelsLoading] = useState(false);
    const [controlsDisabled, setControlsDisabled] = useState(false);

    useEffect(() => {
        formControls.SC.current = new StormControlsClass(appState.hostAddress);
        formControls.SC.current.setPausing = setPausing;
        formControls.SC.current.stopping = stopping;
        formControls.SC.current.setStopping = setStopping;
        formControls.SC.current.setResuming = setResuming;
        formControls.SC.current.setControlsDisabled = setControlsDisabled;
        formControls.SC.current.setDontWaitLoading = setDontWaitLoading;
        formControls.SC.current.setChangeMessagesLoading = setChangeMessagesLoading;
        formControls.SC.current.setChangeSlowModeLoading = setChangeSlowModeLoading;
        formControls.SC.current.setMoreChannelsLoading = setMoreChannelsLoading;
        formControls.SC.current.notifications = formControls.notifications;
    }, [appState.hostAddress]);


    const onStopHandler = async () => {

        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>Are you sure you want to <strong style={{ color: "var(--input-active-red-dark)" }}>STOP</strong> the ongoing storm?</span>
        });

        if (confirmed) {
            formControls.SC.current.stopStorm(appState.setStormInProgress);
            // appState.setStormInProgress(false);
        }

    }

    const handlePause = async () => {
        formControls.SC.current.pauseStorm();
    };

    const handleResume = async () => {
        formControls.SC.current.resumeStorm();
    };

    const handleChangeMessages = async () => {
        const messages = await dialogs.open(ChangeMessages, {
            formControls: formControls,
        });

        if (!messages) {
          return;
        }

        formControls.SC.current.changeMessages(messages, formControls.setMessages, formControls.setMessagesString);
    }

    const handleDontWait = async () => {

        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>Are you sure you want to <strong style={{ color: "var(--input-active-red-dark)" }}>NOT WAIT</strong> for all the channels to be ready?</span>
        });

        if (confirmed) {
            formControls.SC.current.dontWait();
        }
    };

    const handleChangeSlowMode = async () => {
        const slowModeValue = await dialogs.open(ChangeSlowMode, {
            formControls: formControls
        });

        if (!slowModeValue) {
          return;
        }

        formControls.SC.current.changeSlowMode(slowModeValue, formControls.setSlowMode);
    }

    const handleAddMoreChannels = async () => {

        const channels = await dialogs.open(AddChannels, {
            mode: "add",
            formControls: formControls,
            systemInfoControls: systemInfoControls
        });

        if (!channels || channels.length === 0) {
          return;
        }

        formControls.SC.current.startMoreChannels(channels);
    }

    return (
        <div className="storm-controls-container">
            <div className='storm-controls-heading-container'>
                <Zap className='zap-icon' size={20} color={colorScheme === 'light' ? "var(--input-active-red-light)" : "var(--input-active-red-dark)"} />
                <h3 className={`storm-controls-title`}>Storm Controls</h3>
            </div>

            <div className="storm-controls-btns-container">
                <div className="row">
                    <Button
                        variant="contained"
                        startIcon={pausing ? <RefreshCw size={18} className="spin" /> : <Pause size={18} />}
                        sx={btnProps}
                        onClick={handlePause}
                        disabled={controlsDisabled || !appState.stormInProgress}
                    >
                        {
                            pausing ? "Pausing..." : "Pause"
                        }
                    </Button>

                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={resuming ? <RefreshCw size={18} className="spin" /> : <Play size={18} />}
                        sx={btnProps}
                        onClick={handleResume}
                        disabled={controlsDisabled || !appState.stormInProgress}
                    >
                        {
                            resuming ? "Resuming..." : "Resume"
                        }
                    </Button>
                </div>
                <div className="row">

                    <Button
                        variant="contained"
                        startIcon={changeMessagesLoading ? <RefreshCw size={18} className="spin" /> : <SquarePen size={18} />}
                        sx={{
                            ...btnProps,
                            height: "40px",
                        }}
                        onClick={handleChangeMessages}
                        disabled={controlsDisabled || !appState.stormInProgress}
                    >
                        {
                            changeMessagesLoading ? "Processing..." : "Messages"
                        }
                    </Button>

                    <Tooltip title="Change Slow Mode" placement="right">
                        <Fragment>
                            <Button
                                variant="contained"
                                startIcon={changeSlowModeLoading ? <RefreshCw size={18} className="spin" /> : <SquarePen size={18} />}
                                sx={{
                                    ...btnProps,
                                    // padding: "0 .5rem 0 .5rem",
                                    height: "40px",
                                }}
                                onClick={handleChangeSlowMode}
                                disabled={controlsDisabled || !appState.stormInProgress}
                            >
                                {
                                    changeSlowModeLoading ? "Processing..." : "Slow Mode"
                                }
                            </Button>
                        </Fragment>
                    </Tooltip>

                </div>

                <div className="row">

                    <Tooltip title="Change existing Messages" placement="right">
                        <Fragment>
                            <Button
                                variant="contained"
                                startIcon={dontWaitLoading ? <RefreshCw size={18} className="spin" /> : <Ban size={18} />}
                                sx={{
                                    ...btnProps,
                                    height: "40px",
                                }}
                                onClick={handleDontWait}
                                disabled={controlsDisabled || !appState.stormInProgress}
                            >
                                {
                                    dontWaitLoading ? "Processing..." : "Don't Wait"
                                }
                            </Button>
                        </Fragment>
                    </Tooltip>

                    <Tooltip title="Start storming on more channels" placement="right">
                        <Fragment>
                            <Button
                                variant="contained"
                                startIcon={moreChannelsLoading ? <RefreshCw size={18} className="spin" /> : <Plus size={18} />}
                                sx={{
                                    ...btnProps,
                                    height: "40px",
                                }}
                                onClick={handleAddMoreChannels}
                                disabled={controlsDisabled || !appState.stormInProgress}
                            >
                                Channels
                            </Button>
                        </Fragment>
                    </Tooltip>

                </div>
                <Tooltip title="Stop the Storm" placement="right">
                    <Fragment>
                        <Button
                            variant="contained"
                            startIcon={stopping ? <RefreshCw size={18} className="spin" /> : <StopCircle size={18} />}
                            onClick={onStopHandler}
                            sx={{
                                ...btnProps,
                                backgroundColor: colorScheme === 'light' ? "var(--bright-red-2)" : "var(--input-active-red-dark)",
                                color: "var(--light-text)",
                            }}
                            disabled={controlsDisabled}
                        >
                            {
                                stopping ? "Stopping Storm..." : "Stop"
                            }
                        </Button>
                    </Fragment>
                </Tooltip>
            </div>
        </div>
    );
}
export default StormControls;
