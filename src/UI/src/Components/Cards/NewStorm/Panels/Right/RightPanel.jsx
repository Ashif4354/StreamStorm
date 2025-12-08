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

const RightPanel = (props) => {

    const { setManageProfilesOpen } = props;
    const { colorScheme } = useColorScheme();
    const { btnProps } = useCustomMUIProps();
    const formControls = useStormData();
    const systemInfoControls = useSystemInfo();


    const handleSubmit = () => {
        formControls.setErrorText("");
        formControls.SC.current.startStorm(formControls, systemInfoControls)
    }

    return (
        <div className="right-panel-container">

            <div className="switches-container">
                <div className={`switch-container ${colorScheme}-bordered-container`}>
                    <span className="switch-label">Load in background</span>
                    <Switch
                        checked={formControls.loadInBackground}
                        disabled={formControls.stormInProgress || formControls.loading}
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
                    backgroundColor: colorScheme === 'light' ? "var(--input-active-red-light)" : "var(--input-active-red-dark)",
                    borderRadius: "var(--border-radius)",
                    border: "none",
                    '&:hover': {
                        backgroundColor: colorScheme === 'light' ? "var(--input-active-red-light-hover)" : "var(--input-active-red-dark-hover)",
                    },
                    height: "40px",
                    color: "var(--light-text)",
                }}
                disabled={formControls.stormInProgress || formControls.loading}
                onClick={handleSubmit}
            >
                {formControls.loading ? "Starting Storm..." : "Start Storm"}
            </Button>
            
            <ErrorText errorText={formControls.errorText} />

            <div id="storm-controls" />

            <Divider
                sx={{
                    margin: "calc(16px - 0.5rem) 0",
                }}
            />

            <StormControls />

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


        </div>
    );
}

export default RightPanel;
