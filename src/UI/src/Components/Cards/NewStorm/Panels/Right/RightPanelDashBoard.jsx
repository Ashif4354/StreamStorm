/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Switch, Button, Divider } from "@mui/material";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { RefreshCw, Users } from 'lucide-react';

import "./RightPanel.css";
import StormControls from './StormControls/StormControls';
import ErrorText from '../../../../Elements/ErrorText';
import { useStormData } from '../../../../../context/StormDataContext';
import { useSystemInfo } from '../../../../../context/SystemInfoContext';
import { useCustomMUIProps } from '../../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../../context/AppStateContext';

const RightPanel = () => {

    const { colorScheme } = useColorScheme();
    const { btnProps } = useCustomMUIProps();
    const formControls = useStormData();
    const systemInfoControls = useSystemInfo();
    const appState = useAppState();


    const handleSubmit = () => {
        formControls.setErrorText("");
        formControls.SC.current.startStorm(formControls, systemInfoControls, appState);
    }

    return (
        <div className="right-panel-container">

            <StormControls />

            <Divider
                sx={{
                    margin: "calc(16px - 0.5rem) 0",
                }}
            />

            <Button
                startIcon={<Users size="1rem" />}
                sx={btnProps}
                onClick={null}
            >
                Channels Status
            </Button>

            <Button
                startIcon={<Users size="1rem" />}
                sx={btnProps}
                onClick={null}
            >
                View Configurations
            </Button>


        </div>
    );
}

export default RightPanel;
