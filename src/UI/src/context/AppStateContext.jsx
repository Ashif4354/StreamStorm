import { useState, useEffect } from 'react';
import { createContext, useContext } from 'react';

import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { DEFAULT_HOST_ADDRESS } from '../lib/Constants';


const AppStateContext = createContext();

const AppStateProvider = ({ children }) => {

    const [hostAddress] = useLocalStorageState("hostAddress", DEFAULT_HOST_ADDRESS);
    const [logs, setLogs] = useState([]);
    const [UIVersion, setUIVersion] = useLocalStorageState("VITE_APP_VERSION", "0.0.0");
    const [engineVersion, setEngineVersion] = useState('...');
    const [allChannels, setAllChannels] = useState({});
    const [stormInProgress, setStormInProgress] = useState(false);
    const [stormStatus, setStormStatus] = useState("in Progress");
    const [logFilePath, setLogFilePath] = useState("");

    // Default AI provider settings (stored in app state, not localStorage)
    const [defaultAIProvider, setDefaultAIProvider] = useState(null);
    const [defaultAIModel, setDefaultAIModel] = useState(null);
    const [defaultAIBaseUrl, setDefaultAIBaseUrl] = useState(null);
    const [aiSettingsLoading, setAiSettingsLoading] = useState(true);

    // Fetch default AI settings on app startup
    useEffect(() => {
        const fetchDefaultAISettings = async () => {
            try {
                const response = await fetch(`${hostAddress}/settings/ai/default`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setDefaultAIProvider(data.defaultProvider ?? null);
                    setDefaultAIModel(data.defaultModel ?? null);
                    setDefaultAIBaseUrl(data.defaultBaseUrl ?? null);
                }
            } catch (error) {
                console.error('Failed to fetch default AI settings:', error);
            } finally {
                setAiSettingsLoading(false);
            }
        };

        if (hostAddress) {
            fetchDefaultAISettings();
        }
    }, [hostAddress]);

    const values = {
        hostAddress, logs, setLogs, UIVersion, setUIVersion, engineVersion, setEngineVersion, allChannels, setAllChannels,
        stormInProgress, setStormInProgress, stormStatus, setStormStatus, logFilePath, setLogFilePath,
        // AI Settings
        defaultAIProvider, setDefaultAIProvider,
        defaultAIModel, setDefaultAIModel,
        defaultAIBaseUrl, setDefaultAIBaseUrl,
        aiSettingsLoading
    };

    return (
        <AppStateContext.Provider value={values}>
            {children}
        </AppStateContext.Provider>
    );
};

const useAppState = () => {
    return useContext(AppStateContext);
};

export { AppStateProvider, useAppState };