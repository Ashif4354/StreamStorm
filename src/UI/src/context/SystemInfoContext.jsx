import { useEffect, useState, createContext, useContext } from 'react';
import { useNotifications } from '@toolpad/core/useNotifications';

import { RAM_PER_PROFILE } from "../lib/Constants";
import { useAppState } from "./AppStateContext";
import * as atatus from '../lib/atatus';

const SystemInfoContext = createContext();

const SystemInfoProvider = ({ children }) => {
    const { engine, loginMethod } = useAppState();

    const [availableRAM, setAvailableRAM] = useState(null);
    const [debugMode, setDebugMode] = useState(false);
    const [debugCounter, setDebugCounter] = useState(0);

    const notifications = useNotifications();

    // Obscura with cookie login uses lightweight ~150 MB, Chromium / Browser Profiles uses ~350 MB
    const dynamicRamPerProfile = (engine === 'obscura' && loginMethod === 'cookies') ? 150 : 350;

    const systemInfoControls = {
        availableRAM,
        setAvailableRAM,
        RAM_PER_PROFILE: dynamicRamPerProfile,
        debugMode,
        setDebugCounter
    };

    useEffect(() => {
        if (availableRAM !== null) {
            atatus.setGlobalContextProperty('availableRAM_MB', availableRAM);
            atatus.setGlobalContextProperty('maxSupportedChannels', Math.floor(availableRAM / dynamicRamPerProfile));
        }
    }, [availableRAM, dynamicRamPerProfile]);

    useEffect(() => {
        atatus.addFeatureFlagEvaluation('debug_mode', debugMode);
        atatus.setGlobalContextProperty('debugMode', debugMode);
    }, [debugMode]);

    useEffect(() => {
        if (debugCounter >= 10 && !debugMode) {
            setDebugMode(true);
            atatus.addAction('debug-mode-activated-via-counter');
            atatus.systemLogger.info('Debug mode enabled via counter threshold');
            notifications.show('Debug mode enabled!', { severity: 'info' });
        }
    }, [debugCounter, debugMode, notifications]);
    
    useEffect(() => {
        window.enableStreamStormDebugMode = () => {
            setDebugMode(true);
            atatus.addAction('debug-mode-activated-via-window');
            atatus.systemLogger.info('Debug mode enabled via window console trigger');
            notifications.show('Debug mode enabled!', { severity: 'info' });
        };

        return () => {
            delete window.enableStreamStormDebugMode;
        };
    }, [notifications]);

    return (
        <SystemInfoContext.Provider value={systemInfoControls}>
            {children}
        </SystemInfoContext.Provider>
    );
};

const useSystemInfo = () => {
    return useContext(SystemInfoContext);
};

export { SystemInfoProvider, useSystemInfo };
