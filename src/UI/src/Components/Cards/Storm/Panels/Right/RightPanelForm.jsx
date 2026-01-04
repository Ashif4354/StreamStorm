/* eslint-disable react/prop-types */
import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Switch, Button, Divider, Tooltip } from "@mui/material";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { RefreshCw, Users, StopCircle } from 'lucide-react';
import { logEvent } from "firebase/analytics";
import { useDialogs } from "@toolpad/core/useDialogs";

import "./RightPanel.css";
import { analytics } from "../../../../../config/firebase";
import ErrorText from '../../../../Elements/ErrorText';
import StormControlsClass from "../../../../../lib/StormControlsClass";
import { useStormData } from '../../../../../context/StormDataContext';
import { useSystemInfo } from '../../../../../context/SystemInfoContext';
import { useCustomMUIProps } from '../../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../../context/AppStateContext';
import ManageProfilesModal from "../../../../Modals/ManageProfiles/ManageProfiles";
import LogsModal from "../../../../Modals/Logs/Logs";
import { useSocket } from '../../../../../context/SocketContext';
import AreYouSure from "../../../../Dialogs/AreYouSure";

const RightPanelForm = () => {

    const { colorScheme } = useColorScheme();
    const { socket, socketConnected } = useSocket();
    const { btnProps } = useCustomMUIProps();
    const formControls = useStormData();
    const systemInfoControls = useSystemInfo();
    const appState = useAppState();
    const dialogs = useDialogs();

    const [stopping, setStopping] = useState(false);
    const [manageProfilesOpen, setManageProfilesOpen] = useState(false);
    const [logsOpen, setLogsOpen] = useState(false);


    const handleSubmit = () => {
        // Check if user is logged in
        if (!appState.isLoggedIn) {
            formControls.setErrorText("Not logged in. Log in first in Manage Environments section.");
            return;
        }

        formControls.setErrorText("");
        formControls.SC.current.startStorm(formControls, systemInfoControls, appState);
    }

    const onStopHandler = async () => {
        formControls.SC.current.stopStorm2(setStopping);
    }

    const askToJoinStartedStorm = async () => {
        return await dialogs.open(AreYouSure, {
            text: <span>A Storm has just begun. Do you wanna hop in?</span>
        });
    }

    useEffect(() => {
        formControls.SC.current = new StormControlsClass(appState.hostAddress);
        formControls.SC.current.notifications = formControls.notifications;
    }, [appState.hostAddress]);

    useEffect(() => {
        if (manageProfilesOpen) {
            logEvent(analytics, "manage_profiles_open");
        }

        if (logsOpen) {
            logEvent(analytics, "logs_open");
        }
    }, [manageProfilesOpen, logsOpen]);

    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("storm_started", async () => {
            const confirmed = await askToJoinStartedStorm();
            if (!confirmed) return;
            appState.setStormInProgress(true);
        });

        return () => {
            socket.off("storm_started");
        }

    }, [socket, socketConnected]);

    return (
        <div className="right-panel-container">

            <div className="switches-container">
                <div className={`switch-container ${colorScheme}-bordered-container`}>
                    <span className="switch-label">Load in background</span>
                    <Switch
                        checked={formControls.loadInBackground}
                        disabled={appState.stormInProgress || formControls.loading}
                        onChange={(e) => formControls.setLoadInBackground(e.target.checked)}
                    />
                </div>
            </div>

            <Button
                variant="contained"
                color="primary"
                className={`start-storm-button ${colorScheme}-bordered-container`}
                startIcon={formControls.loading ? <RefreshCw size={20} className="spin" /> : <PlayArrowIcon />}
                sx={{
                    ...btnProps,
                    marginTop: "16px",
                    backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                    borderRadius: "var(--border-radius)",
                    border: "none",
                    '&:hover': {
                        backgroundColor: colorScheme === 'light' ? "var(--light-primary-hover)" : "var(--input-active-red-dark-hover)",
                    },
                    height: "40px",
                    color: "var(--light-text)",
                }}
                disabled={appState.stormInProgress || formControls.loading}
                onClick={handleSubmit}
            >
                {formControls.loading ? "Starting Storm..." : "Start Storm"}
            </Button>

            <ErrorText errorText={formControls.errorText} />
            <Tooltip title="Auxiliary stop button, in case you need it" placement="bottom">
                <Button
                    variant="contained"
                    startIcon={stopping ? <RefreshCw size={18} className="spin" /> : <StopCircle size={18} />}
                    onClick={onStopHandler}
                    sx={{
                        ...btnProps,
                        backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-light)",
                        color: "var(--light-text)",
                    }}
                >
                    {
                        stopping ? "Stopping Storm..." : "Stop"
                    }
                </Button>
            </Tooltip>

            <Divider
                sx={{
                    margin: "calc(16px - 0.5rem) 0",
                }}
            />

            <Button
                startIcon={<Users size="1rem" />}
                sx={btnProps}
                onClick={() => setManageProfilesOpen(true)}
            >
                Manage Environment
            </Button>

            <Button
                startIcon={<Users size="1rem" />}
                sx={btnProps}
                onClick={() => setLogsOpen(true)}
            >
                Logs
            </Button>

            <ManageProfilesModal open={manageProfilesOpen} setOpen={setManageProfilesOpen} />
            <LogsModal open={logsOpen} setOpen={setLogsOpen} />

        </div>
    );
}

export default RightPanelForm;
