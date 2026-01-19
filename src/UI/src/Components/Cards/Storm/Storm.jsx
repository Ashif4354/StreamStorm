import { useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import Card from '@mui/material/Card';
import { CardHeader, CardContent, Divider } from "@mui/material";
import { Settings2 } from 'lucide-react';
import { useDialogs } from '@toolpad/core/useDialogs';
import * as atatus from "atatus-spa";

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

    const askToJoinExistingStorm = async () => {
        return await dialogs.open(AreYouSure, {
            text: <span>A Storm is already in progress. Do you wanna hop in?</span>
        });
    }

    useEffect(() => {
        const checkStorm = async () => {
            try {
                const res = await fetch(appState.hostAddress + "/storm");
                const data = await res.json();

                if (data.success) {
                    if (data.storm) {

                        const confirmed = await askToJoinExistingStorm();
                        if (!confirmed) return;

                        appState.setStormInProgress(true);

                    } else {
                        appState.setStormInProgress(false);
                    }
                } else {
                    if (data.error) {
                        console.error("Failed to fetch storm status:", data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['storm_status_check_failed']);
                    }
                }
            } catch (error) {
                console.error("Error fetching storm status:", error);
                atatus.notify(error, {}, ['storm_status_check_error']);
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
}

export default Storm;