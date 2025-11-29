import { useState } from 'react';
/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Switch, Button, Divider } from "@mui/material";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { RefreshCw, Users } from 'lucide-react';

import "./RightPanel.css";
import StormControls from './StormControls/StormControls';
import { useStormData } from '../../../../../context/StormDataContext';
import { useSystemInfo } from '../../../../../context/SystemInfoContext';
import { useCustomMUIProps } from '../../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../../context/AppStateContext';
import ChannelsStatus from '../../../../Modals/ChannelsStatus/ChannelsStatus'; 
import ViewConfig from '../../../../Modals/ViewConfig/ViewConfig';

const RightPanel = () => {

    const { colorScheme } = useColorScheme();
    const { btnProps } = useCustomMUIProps();
    const formControls = useStormData();
    const systemInfoControls = useSystemInfo();
    const appState = useAppState();

    const [channelsStatusOpen, setChannelsStatusOpen] = useState(false);
    const [viewConfigurationsOpen, setViewConfigurationsOpen] = useState(false);

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
                onClick={() => setChannelsStatusOpen(true)}
            >
                Channels Status
            </Button>

            <Button
                startIcon={<Users size="1rem" />}
                sx={btnProps}
                onClick={() => setViewConfigurationsOpen(true)}
            >
                View Configurations
            </Button>

            <ChannelsStatus open={channelsStatusOpen} setOpen={setChannelsStatusOpen} />
            <ViewConfig open={viewConfigurationsOpen} setOpen={setViewConfigurationsOpen} />
        </div>
    );
}

export default RightPanel;
