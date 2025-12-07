/* eslint-disable react/prop-types */
import { useState } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box, useMediaQuery } from '@mui/material';
import { Settings as SettingsIcon, Cog, Server, Palette, KeyRound } from 'lucide-react';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import CloseIcon from '@mui/icons-material/Close';
import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../context/AppStateContext';

const Settings = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const appState = useAppState();
    const verticalTab = useMediaQuery('(min-width: 900px)')
    const isVerySmallScreen = useMediaQuery('(max-width: 650px)')

    const [tabValue, setTabValue] = useState(0);

    const modalCloseHandler = () => {
        setOpen(false);
    }

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    return (
        <Modal open={open} onClose={modalCloseHandler}>
            <Box sx={{
                ...modalProps,
                minWidth: '200px',
                maxHeight: '50vh',
                "&.MuiBox-root": {
                    overflow: "hidden",
                }
            }}>
                <div>
                    <CloseButton onClick={modalCloseHandler} />
                    <div className={`modal-heading ${colorScheme}-text`}>
                        <SettingsIcon className='profile-icon' />
                        Settings
                    </div>
                </div>

                <Divider sx={{ margin: '1rem 0 0 0' }} />
                <div
                    className='settings-content-container'
                >
                    <div
                        className='settings-tabs-container'
                        style={{
                            flexDirection: verticalTab ? 'row' : 'column'
                        }}
                    >
                        <Tabs
                            value={tabValue}
                            onChange={handleTabChange}
                            // variant='fullWidth'
                            orientation={verticalTab ? 'vertical' : 'horizontal'}
                        >
                            <Tab
                                label={
                                    <span
                                        className="tab-label"
                                        style={{
                                            justifyContent: verticalTab ? 'flex-start' : 'center'
                                        }}
                                    >
                                        <Cog size={16} />
                                        {
                                            isVerySmallScreen ? '' : 'General'
                                        }
                                    </span>
                                }
                                // icon={<Cog size={16} />}
                                iconPosition='start'
                                sx={{
                                    // alignItems: 'flex-start',
                                    textTransform: 'none',
                                    flex: 1,
                                    minWidth: 0
                                }}
                            />
                            <Tab
                                label={
                                    <span className="tab-label"
                                        style={{
                                            justifyContent: verticalTab ? 'flex-start' : 'center'
                                        }}
                                    >
                                        <Server size={16} />
                                        {isVerySmallScreen ? '' : 'Host'}
                                    </span>
                                }
                                // icon={<Server size={16} />}
                                iconPosition='start'
                                sx={{
                                    // alignItems: 'flex-start',
                                    textTransform: 'none',
                                    flex: 1,
                                    minWidth: 0
                                }}
                            />
                            <Tab
                                label={
                                    <span className="tab-label"
                                        style={{
                                            justifyContent: verticalTab ? 'flex-start' : 'center'
                                        }}
                                    >
                                        <Palette size={16} />
                                        {isVerySmallScreen ? '' : 'Appearance'}
                                    </span>
                                }
                                // icon={<Palette size={16} />}
                                iconPosition='start'
                                sx={{
                                    // alignItems: 'flex-start',
                                    textTransform: 'none',
                                    flex: 1,
                                    minWidth: 0
                                }}
                            />
                            <Tab
                                label={
                                    <span className="tab-label"
                                        style={{
                                            justifyContent: verticalTab ? 'flex-start' : 'center',

                                        }}
                                    >
                                        <KeyRound size={16} /> {isVerySmallScreen ? '' : 'API Keys'}
                                    </span>
                                }
                                // icon={<KeyRound size={16} />}
                                iconPosition='start'
                                sx={{
                                    // alignItems: 'flex-start',
                                    textTransform: 'none',
                                    flex: 1,
                                    minWidth: 0
                                }}
                            />
                        </Tabs>
                        <Divider
                            sx={{
                                margin: verticalTab ? '0 1rem 0 0' : '0 0 1rem 0'
                            }}
                            orientation={verticalTab ? 'vertical' : 'horizontal'}
                            flexItem
                        />
                        <div className='settings-tab-content-container'>
                            {
                                tabValue === 0 ? (
                                    <div>
                                        General Settings Content
                                    </div>
                                ) : tabValue === 1 ? (
                                    <div>
                                        Host Settings Content
                                    </div>
                                ) : tabValue === 2 ? (
                                    <div>
                                        Appearance Settings Content
                                    </div>
                                ) : tabValue === 3 ? (
                                    <div>
                                        API Keys Settings Content
                                    </div>
                                ) : null
                            }

                        </div>
                    </div>
                </div>
            </Box>
        </Modal>
    );
};

export default Settings;