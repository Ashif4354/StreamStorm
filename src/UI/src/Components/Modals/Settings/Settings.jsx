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
import * as atatus from 'atatus-spa';

import GeneralSettings from './Sections/GeneralSettings';
import HostSettings from './Sections/HostSettings';
import AppearanceSettings from './Sections/AppearanceSettings';
import ApiKeysSettings from './Sections/ApiKeysSettings';

const Settings = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const {
        hostAddress,
        defaultAIProvider, setDefaultAIProvider,
        defaultAIModel, setDefaultAIModel,
        defaultAIBaseUrl, setDefaultAIBaseUrl
    } = useAppState();
    const verticalTab = useMediaQuery('(min-width: 900px)')
    const isVerySmallScreen = useMediaQuery('(max-width: 650px)')

    const [tabValue, setTabValue] = useState(0);

    // API Keys state - fetched once when modal opens
    const [apiKeysData, setApiKeysData] = useState({});
    const [apiKeysLoading, setApiKeysLoading] = useState(false);

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
                    // Expected format: { openai: {...}, anthropic: {...}, google: {...}, defaultProvider, defaultModel, defaultBaseUrl }
                    const { defaultProvider: fetchedDefault, defaultModel: fetchedModel, defaultBaseUrl: fetchedBaseUrl, ...providers } = data;
                    setApiKeysData(providers);

                    // Update app state with fetched default settings (handle nulls)
                    setDefaultAIProvider(fetchedDefault ?? null);
                    setDefaultAIModel(fetchedModel ?? null);
                    setDefaultAIBaseUrl(fetchedBaseUrl ?? null);
                }
            } catch (error) {
                console.error('Failed to fetch API keys:', error);
                atatus.notify(error, {}, ['settings_api_keys_fetch_error']);
            } finally {
                setApiKeysLoading(false);
            }
        };

        fetchAllApiKeys();
    }, [open, hostAddress, setDefaultAIProvider, setDefaultAIModel, setDefaultAIBaseUrl]);

    const handleUpdateApiKey = (providerId, data) => {
        setApiKeysData(prev => ({
            ...prev,
            [providerId]: data
        }));
    };

    const handleSetDefaultProvider = async (providerId, model, baseUrl) => {
        try {
            const response = await fetch(`${hostAddress}/settings/ai/default`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    provider: providerId,
                    model: model,
                    baseUrl: baseUrl
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setDefaultAIProvider(data.defaultProvider);
                setDefaultAIModel(data.defaultModel);
                setDefaultAIBaseUrl(data.defaultBaseUrl ?? null);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to set default provider:', error);
            atatus.notify(error, {}, ['settings_set_default_provider_error']);
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
                                    defaultProvider={defaultAIProvider}
                                    onSetDefault={handleSetDefaultProvider}
                                    onDefaultModelUpdated={(modelName) => {
                                        setDefaultAIModel(modelName);
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

