import { useEffect, useState } from "react";
import { useColorScheme } from '@mui/material/styles';
import Card from '@mui/material/Card';
import { CardHeader, CardContent, Divider } from "@mui/material";
import { Settings2 } from 'lucide-react';
import { logEvent } from "firebase/analytics";

import "./NewStorm.css";
import LeftPanel from "./Panels/Left/LeftPanelForm";
import LeftPanelDashboard from "./Panels/Left/LeftPanelDashboard";
import RightPanelForm from "./Panels/Right/RightPanelForm";
import RightPanelDashboard from "./Panels/Right/RightPanelDashBoard";
import ManageProfilesModal from "../../Modals/ManageProfiles/ManageProfiles";
import fetchStatus from "../../../lib/FetchStatus";
import { useStormData } from "../../../context/StormDataContext";
import { analytics } from "../../../config/firebase";
import { useCustomMUIProps } from "../../../context/CustomMUIPropsContext";
import { useAppState } from "../../../context/AppStateContext";
import Ping from "../../Elements/Ping/Ping";

const NewStorm = () => {
    const { cardProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const [manageProfilesOpen, setManageProfilesOpen] = useState(false);
    const formControls = useStormData();
    const appState = useAppState();

    useEffect(() => {
        fetchStatus(appState);
    }, [])

    // setInterval(() => {
    //     const interval = fetchStatus(formControls);
    //     return () => clearInterval(interval);
    // }, 2000);

    // useEffect(() => {
    //     const interval = setInterval(() => {
    //         fetchStatus(formControls);
    //     }, 2000);

    //     systemInfoControls.setPollingIntervals(prev => [...prev, interval]);

    //     return () => clearInterval(interval);
    // }, []);

    useEffect(() => {
        if(manageProfilesOpen) {
            logEvent(analytics, "manage_profiles_open");
        }
    }, [manageProfilesOpen]);

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
                    title={appState.stormStatus === "Storming" ? "Storm In Progress" : appState.stormStatus === "Paused" ? "Storm Paused" : "New Storm"}
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
                <div className="new-storm-card-content">
                    {
                        appState.stormInProgress ? <LeftPanelDashboard /> : <LeftPanel />
                    }  

                    <Divider orientation="vertical" />
                    
                    {
                        appState.stormInProgress ? <RightPanelDashboard /> : <RightPanelForm setManageProfilesOpen={setManageProfilesOpen} />
                    }
                </div>
            </CardContent>

            <ManageProfilesModal open={manageProfilesOpen} setOpen={setManageProfilesOpen} />
        </Card>
    );
}

export default NewStorm;