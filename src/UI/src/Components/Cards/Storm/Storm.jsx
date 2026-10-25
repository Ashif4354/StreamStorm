import { useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import Card from '@mui/material/Card';
import { CardHeader, CardContent, Divider } from "@mui/material";
import { Settings2 } from 'lucide-react';
import { useDialogs } from '@toolpad/core/useDialogs';
import * as atatus from "../../../lib/atatus";

import "./Storm.css";
import LeftPanel from "./Panels/Left/LeftPanelForm";
import LeftPanelDashboard from "./Panels/Left/LeftPanelDashboard";
import RightPanelForm from "./Panels/Right/RightPanelForm";
import RightPanelDashboard from "./Panels/Right/RightPanelDashBoard";
import { useCustomMUIProps } from "../../../context/CustomMUIPropsContext";
import { useAppState } from "../../../context/AppStateContext";
import Ping from "../../Elements/Ping/Ping";
import { ServerContextProvider } from '../../../context/ServerContext';
import AreYouSure from '../../Dialogs/AreYouSure';

const Storm = () => {
    const { cardProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const appState = useAppState();
    const dialogs = useDialogs();

    // Track active view in Atatus RUM
    useEffect(() => {
        const view = appState.stormInProgress ? '/dashboard/active-storm' : '/dashboard/new-storm';
        atatus.setViewName(view);
        atatus.setViewContext({
            stormInProgress: appState.stormInProgress,
            stormStatus: appState.stormStatus,
            hostAddress: appState.hostAddress,
        });
        atatus.stormLogger.debug(`Dashboard view changed to ${view}`);
    }, [appState.stormInProgress, appState.stormStatus, appState.hostAddress]);

    const askToJoinExistingStorm = async () => {
        atatus.addAction('ask-join-storm-prompted');
        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>A Storm is already in progress. Do you wanna hop in?</span>
        });
        if (confirmed) {
            atatus.addAction('join-existing-storm-accepted');
            atatus.stormLogger.info('User accepted joining existing active storm');
        } else {
            atatus.addAction('join-existing-storm-declined');
            atatus.stormLogger.info('User declined joining existing active storm');
        }
        return confirmed;
    };

    useEffect(() => {
        const checkStorm = async () => {
            atatus.startOperation('check-storm-status');
            atatus.startDurationVital('check-storm-status');

            try {
                const res = await fetch(appState.hostAddress + "/storm");
                const data = await res.json();
                atatus.stopDurationVital('check-storm-status');

                if (data.success) {
                    atatus.succeedOperation('check-storm-status');
                    atatus.stormLogger.info('Storm status checked', { stormActive: data.storm });
                    if (data.storm) {
                        const confirmed = await askToJoinExistingStorm();
                        if (!confirmed) return;

                        appState.setStormInProgress(true);
                    } else {
                        appState.setStormInProgress(false);
                    }
                } else {
                    atatus.failOperation('check-storm-status', data.error || 'Check failed');
                    if (data.error) {
                        console.error("Failed to fetch storm status:", data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['storm_status_check_failed'] });
                        atatus.stormLogger.error('Failed to check storm status', { response: data }, new Error(data.error));
                    }
                }
            } catch (error) {
                atatus.stopDurationVital('check-storm-status');
                atatus.failOperation('check-storm-status', error.message);
                console.error("Error fetching storm status:", error);
                atatus.addError(error, { tags: ['storm_status_check_error'] });
                atatus.stormLogger.error('Network error checking storm status', {}, error);
            }
        };

        checkStorm();
    }, [appState.hostAddress]);

    return (
        <Card
            className={
                `new-storm-card  ${colorScheme}-bordered-container`
            }
            sx={cardProps}
        >
            <div className="card-header-container" id="new-storm">
                <CardHeader
                    avatar={appState.stormInProgress ? <Ping /> : <Settings2 />}
                    title={appState.stormInProgress ? `Storm ${appState.stormStatus}` : "New Storm"}
                    className={`card-header card-header-${colorScheme}`}
                    sx={{
                        padding: 0
                    }}
                />
                <span className={`card-header-description card-header-description-${colorScheme}`}>
                    {
                        appState.stormInProgress ? "" : "Set up parameters for your new storm and manage active storm."
                    }
                </span>
            </div>
            <CardContent
                sx={{
                    padding: 0,
                }}
            >
                <ServerContextProvider>
                    <div className="new-storm-card-content">
                        {
                            appState.stormInProgress ? <LeftPanelDashboard /> : <LeftPanel />
                        }

                        <Divider orientation="vertical" />

                        {
                            appState.stormInProgress ? <RightPanelDashboard /> : <RightPanelForm />
                        }
                    </div>
                </ServerContextProvider>
            </CardContent>

        </Card>
    );
};

export default Storm;
