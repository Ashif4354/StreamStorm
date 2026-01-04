import { useState, useEffect } from 'react';
import { createContext, useContext } from 'react';

import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { DEFAULT_HOST_ADDRESS } from '../lib/Constants';
import * as atatus from "atatus-spa";


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

    // General settings (stored in app state, synced with backend)
    const [loginMethod, setLoginMethod] = useState('cookies');

    const [settingsLoading, setSettingsLoading] = useState(true);

    // Fetch all settings (engine config + AI defaults + general) on app startup
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const response = await fetch(`${hostAddress}/settings`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                const data = await response.json();
                if (data.success) {
                    // Set engine config
                    setEngineVersion(data.version);
                    setLogFilePath(data.log_file_path);

                    // Set AI defaults from 'ai' sub-key
                    if (data.ai) {
                        setDefaultAIProvider(data.ai.defaultProvider ?? null);
                        setDefaultAIModel(data.ai.defaultModel ?? null);
                        setDefaultAIBaseUrl(data.ai.defaultBaseUrl ?? null);
                    }

                    // Set general settings from 'general' sub-key
                    if (data.general) {
                        setLoginMethod(data.general.login_method ?? 'cookies');
                    }
                } else {
                    console.error("Failed to fetch settings:", data.message);
                    atatus.notify(data.message, {}, ['settings_fetch_failed']);
                }
            } catch (error) {
                console.error('Failed to fetch settings:', error);
                atatus.notify(error, {}, ['settings_fetch_error']);
            } finally {
                setSettingsLoading(false);
            }
        };

        if (hostAddress) {
            fetchSettings();
        } else {
            setSettingsLoading(false);
        }
    }, [hostAddress]);

    const values = {
        hostAddress, logs, setLogs, UIVersion, setUIVersion, engineVersion, setEngineVersion, allChannels, setAllChannels,
        stormInProgress, setStormInProgress, stormStatus, setStormStatus, logFilePath, setLogFilePath,
        // AI Settings
        defaultAIProvider, setDefaultAIProvider,
        defaultAIModel, setDefaultAIModel,
        defaultAIBaseUrl, setDefaultAIBaseUrl,
        // General Settings
        loginMethod, setLoginMethod,
        settingsLoading
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
