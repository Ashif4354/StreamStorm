import { useEffect } from 'react';
import { createContext, useState, useContext } from 'react';
import { useNotifications } from '@toolpad/core/useNotifications';

import { RAM_PER_PROFILE } from "../lib/Constants";
import fetchRAM from "../lib/FetchRAM"

const SystemInfoContext = createContext();

const SystemInfoProvider = ({children}) => {

    const [availableRAM, setAvailableRAM] = useState(null);
    const [debugMode, setDebugMode] = useState(false);
    
    const [debugList, setDebugList] = useState([]);
    const [pollingIntervals, setPollingIntervals] = useState([]);

    const notifications = useNotifications();

    const systemInfoControls = { availableRAM, setAvailableRAM, fetchRAM, RAM_PER_PROFILE, debugMode, setDebugList, setPollingIntervals };


    const stopPolling = () => {
        setPollingIntervals(currentIntervals => {
            currentIntervals.forEach(interval => clearInterval(interval));
            return [];
        })
    }
     
    useEffect(() => { 
        if (debugList.length == 10) {            
            setDebugMode(true);
            stopPolling();

            notifications.show('Debug mode enabled!', { severity: 'info' });
        }   
    }, [debugList]);

    useEffect(() => {
        window.enableStreamStormDebugMode = () => {
            setDebugMode(true);
            stopPolling();

            notifications.show('Debug mode enabled!', { severity: 'info' });
        }
        // stopPolling(); //comment this line in production
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