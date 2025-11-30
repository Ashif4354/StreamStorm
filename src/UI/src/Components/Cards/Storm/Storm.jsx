import { useColorScheme } from '@mui/material/styles';
import Card from '@mui/material/Card';
import { CardHeader, CardContent, Divider } from "@mui/material";
import { Settings2 } from 'lucide-react';

import "./Storm.css";
import LeftPanel from "./Panels/Left/LeftPanelForm";
import LeftPanelDashboard from "./Panels/Left/LeftPanelDashboard";
import RightPanelForm from "./Panels/Right/RightPanelForm";
import RightPanelDashboard from "./Panels/Right/RightPanelDashBoard";
import { useCustomMUIProps } from "../../../context/CustomMUIPropsContext";
import { useAppState } from "../../../context/AppStateContext";
import Ping from "../../Elements/Ping/Ping";

const Storm = () => {
    const { cardProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const appState = useAppState();  

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
                <div className="new-storm-card-content">
                    {
                        appState.stormInProgress ? <LeftPanelDashboard /> : <LeftPanel />
                    }  

                    <Divider orientation="vertical" />
                    
                    {
                        appState.stormInProgress ? <RightPanelDashboard /> : <RightPanelForm />
                    }
                </div>
            </CardContent>
            
        </Card>
    );
}

export default Storm;