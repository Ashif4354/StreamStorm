import { useEffect } from 'react';
import { createContext, useState, useContext } from 'react';
import { useNotifications } from '@toolpad/core/useNotifications';

import { RAM_PER_PROFILE } from "../lib/Constants";
import fetchRAM from "../lib/FetchRAM"

const SystemInfoContext = createContext();

const SystemInfoProvider = ({children}) => {

    const [availableRAM, setAvailableRAM] = useState(null);
    const [debugMode, setDebugMode] = useState(false);    
    const [debugCounter, setDebugCounter] = useState(0);

    const notifications = useNotifications();

    const systemInfoControls = { availableRAM, setAvailableRAM, fetchRAM, RAM_PER_PROFILE, debugMode, setDebugCounter };
     
    useEffect(() => { 
        if (debugCounter >= 10) {            
            setDebugMode(true);

            notifications.show('Debug mode enabled!', { severity: 'info' });
        }   
    }, [debugCounter]);

    useEffect(() => {
        window.enableStreamStormDebugMode = () => {
            setDebugMode(true);

            notifications.show('Debug mode enabled!', { severity: 'info' });
        }
    }, []);

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