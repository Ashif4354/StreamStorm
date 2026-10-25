import { useState, useEffect, createContext, useContext } from 'react';
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { DEFAULT_HOST_ADDRESS } from '../lib/Constants';
import * as atatus from '../lib/atatus';

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
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const [settingsLoading, setSettingsLoading] = useState(true);

    // Sync storm progress to global context and feature flags
    useEffect(() => {
        atatus.setGlobalContextProperty('stormInProgress', stormInProgress);
        atatus.setGlobalContextProperty('stormStatus', stormStatus);
        atatus.addFeatureFlagEvaluation('storm_in_progress', stormInProgress);
    }, [stormInProgress, stormStatus]);

    // Sync login method and status
    useEffect(() => {
        atatus.addFeatureFlagEvaluation('login_method', loginMethod);
        atatus.addFeatureFlagEvaluation('is_logged_in', isLoggedIn);
        atatus.setUserProperty('loginMethod', loginMethod);
        atatus.setUserProperty('isLoggedIn', isLoggedIn);
    }, [loginMethod, isLoggedIn]);

    // Sync AI provider
    useEffect(() => {
        if (defaultAIProvider) {
            atatus.addFeatureFlagEvaluation('ai_provider', defaultAIProvider);
            atatus.setGlobalContextProperty('defaultAIProvider', defaultAIProvider);
            atatus.setGlobalContextProperty('defaultAIModel', defaultAIModel);
        }
    }, [defaultAIProvider, defaultAIModel]);

    // Fetch all settings (engine config + AI defaults + general) on app startup
    useEffect(() => {
        const fetchSettings = async () => {
            atatus.startOperation('settings-bootstrap');
            atatus.startDurationVital('settings-bootstrap');

            try {
                const response = await fetch(`${hostAddress}/settings`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                const data = await response.json();
                atatus.stopDurationVital('settings-bootstrap');

                if (data.success) {
                    atatus.succeedOperation('settings-bootstrap');
                    atatus.setViewLoadingTime();
                    atatus.addTiming('settings_loaded');

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
                        setIsLoggedIn(data.general.is_logged_in ?? false);
                    }

                    // Register identity and global context
                    atatus.setAccount({
                        id: hostAddress,
                        name: 'StreamStorm Engine',
                        engineVersion: data.version,
                    });
                    atatus.setUser({
                        id: data.general?.is_logged_in ? 'authenticated-operator' : 'anonymous-operator',
                        loginMethod: data.general?.login_method || 'cookies',
                        isLoggedIn: data.general?.is_logged_in || false,
                    });
                    atatus.setGlobalContextProperty('engineVersion', data.version);
                    atatus.setGlobalContextProperty('uiVersion', UIVersion);
                    atatus.setGlobalContextProperty('hostAddress', hostAddress);

                    atatus.settingsLogger.info('Engine settings initialized successfully', {
                        version: data.version,
                        general: data.general,
                        ai: data.ai,
                    });
                } else {
                    atatus.failOperation('settings-bootstrap', data.error || 'Failed to fetch settings');
                    if (data.error) {
                        console.error("Failed to fetch settings:", data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['settings_fetch_failed'] });
                        atatus.settingsLogger.error('Failed to fetch settings from engine', { response: data }, new Error(data.error));
                    }
                }
            } catch (error) {
                atatus.stopDurationVital('settings-bootstrap');
                atatus.failOperation('settings-bootstrap', error.message);
                console.error('Failed to fetch settings:', error);
                atatus.addError(error, { tags: ['settings_fetch_error'] });
                atatus.settingsLogger.error('Settings fetch network error', {}, error);
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
        isLoggedIn, setIsLoggedIn,
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
