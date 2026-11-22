import { useState } from 'react';
/* eslint-disable react/prop-types */
import { Button, Divider } from "@mui/material";
import { Users } from 'lucide-react';

import "./RightPanel.css";
import * as atatus from "../../../../../lib/atatus";
import StormControls from './StormControls/StormControls';
import { useCustomMUIProps } from '../../../../../context/CustomMUIPropsContext';
import ChannelsStatus from '../../../../Modals/ChannelsStatus/ChannelsStatus'; 
import ViewConfig from '../../../../Modals/ViewConfig/ViewConfig';

const RightPanel = () => {

    const { btnProps } = useCustomMUIProps();

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
                data-atatus-action-name="btn-open-channels-status"
                onClick={() => {
                    atatus.addAction("open-channels-status-clicked");
                    setChannelsStatusOpen(true);
                }}
            >
                Channels Status
            </Button>

            <Button
                startIcon={<Users size="1rem" />}
                sx={btnProps}
                data-atatus-action-name="btn-open-view-configurations"
                onClick={() => {
                    atatus.addAction("open-view-configurations-clicked");
                    setViewConfigurationsOpen(true);
                }}
            >
                View Configurations
            </Button>

            <ChannelsStatus open={channelsStatusOpen} setOpen={setChannelsStatusOpen} />
            <ViewConfig open={viewConfigurationsOpen} setOpen={setViewConfigurationsOpen} />
        </div>
    );
};

export default RightPanel;
