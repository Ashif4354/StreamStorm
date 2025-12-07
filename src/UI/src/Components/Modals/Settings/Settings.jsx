/* eslint-disable react/prop-types */
import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box, useMediaQuery } from '@mui/material';
import { Settings as SettingsIcon, Cog, Server, Palette, KeyRound } from 'lucide-react';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../context/AppStateContext';

import GeneralSettings from './Sections/GeneralSettings';
import HostSettings from './Sections/HostSettings';
import AppearanceSettings from './Sections/AppearanceSettings';
import ApiKeysSettings from './Sections/ApiKeysSettings';

const STORAGE_KEY_DEFAULT_PROVIDER = 'defaultAIProvider';

const Settings = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const { hostAddress } = useAppState();
    const verticalTab = useMediaQuery('(min-width: 900px)')
    const isVerySmallScreen = useMediaQuery('(max-width: 650px)')

    const [tabValue, setTabValue] = useState(0);

    // API Keys state - fetched once when modal opens
    const [apiKeysData, setApiKeysData] = useState({});
    const [apiKeysLoading, setApiKeysLoading] = useState(false);

    // Default provider state
    const [defaultProvider, setDefaultProvider] = useState(() => {
        // Initialize from localStorage if available
        return localStorage.getItem(STORAGE_KEY_DEFAULT_PROVIDER) || null;
    });
    const [defaultModel, setDefaultModel] = useState(() => {
        return localStorage.getItem('defaultAIModel') || null;
    });

    // Fetch all API keys and default provider when modal opens
    useEffect(() => {
        const fetchAllApiKeys = async () => {
            if (!open) return;

            setApiKeysLoading(true);
            try {
                const response = await fetch(`${hostAddress}/settings/ai/keys`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    // Expected format: { openai: {...}, anthropic: {...}, google: {...}, defaultProvider: 'openai', defaultModel: 'gpt-4' }
                    const { defaultProvider: fetchedDefault, defaultModel: fetchedModel, ...providers } = data;
                    setApiKeysData(providers);

                    // Update default provider and model if fetched from backend
                    if (fetchedDefault) {
                        setDefaultProvider(fetchedDefault);
                        localStorage.setItem(STORAGE_KEY_DEFAULT_PROVIDER, fetchedDefault);
                    }
                    if (fetchedModel) {
                        setDefaultModel(fetchedModel);
                        localStorage.setItem('defaultAIModel', fetchedModel);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch API keys:', error);
            } finally {
                setApiKeysLoading(false);
            }
        };

        fetchAllApiKeys();
    }, [open, hostAddress]);

    const handleUpdateApiKey = (providerId, data) => {
        setApiKeysData(prev => ({
            ...prev,
            [providerId]: data
        }));
    };

    const handleSetDefaultProvider = async (providerId) => {
        try {
            const response = await fetch(`${hostAddress}/settings/ai/default`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ provider: providerId }),
            });

            if (response.ok) {
                const data = await response.json();
                setDefaultProvider(providerId);
                localStorage.setItem(STORAGE_KEY_DEFAULT_PROVIDER, providerId);
                if (data.defaultModel) {
                    setDefaultModel(data.defaultModel);
                    localStorage.setItem('defaultAIModel', data.defaultModel);
                }
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to set default provider:', error);
            return false;
        }
    };

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
                maxWidth: '700px',
                width: verticalTab ? '70%' : '90%',
                height: '60vh',
                display: 'flex',
                flexDirection: 'column',
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
                    style={{
                        flexDirection: verticalTab ? 'row' : 'column'
                    }}
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
                            orientation={verticalTab ? 'vertical' : 'horizontal'}
                            sx={{
                                minWidth: verticalTab ? '140px' : 'auto',
                                flexShrink: 0,
                            }}
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
                                iconPosition='start'
                                sx={{
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
                                iconPosition='start'
                                sx={{
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
                                iconPosition='start'
                                sx={{
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
                                iconPosition='start'
                                sx={{
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

                    </div>
                    <div className='settings-tab-content-container'>
                        {
                            tabValue === 0 ? (
                                <GeneralSettings />
                            ) : tabValue === 1 ? (
                                <HostSettings />
                            ) : tabValue === 2 ? (
                                <AppearanceSettings />
                            ) : tabValue === 3 ? (
                                <ApiKeysSettings
                                    apiKeysData={apiKeysData}
                                    onUpdateApiKey={handleUpdateApiKey}
                                    isLoading={apiKeysLoading}
                                    defaultProvider={defaultProvider}
                                    onSetDefault={handleSetDefaultProvider}
                                    onDefaultModelUpdated={(modelName) => {
                                        setDefaultModel(modelName);
                                        localStorage.setItem('defaultAIModel', modelName);
                                    }}
                                />
                            ) : null
                        }

                    </div>
                </div>
            </Box>
        </Modal>
    );
};

export default Settings;

