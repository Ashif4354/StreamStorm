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

    const values = {
        hostAddress, logs, setLogs, UIVersion, setUIVersion, engineVersion, setEngineVersion, allChannels, setAllChannels,
        stormInProgress, setStormInProgress, stormStatus, setStormStatus, logFilePath, setLogFilePath
    };

    useEffect(() => {

        // This useEffect is used to inject mock data for testing purposes
        // It is commented out by default, but can be uncommented to test the UI with mock data

        // setInterval(() => 
        //     setLogs(prevLogs => [...prevLogs, { message: "App State Provider mounted", time: new Date().toISOString(), level: "INFO" }])
        // , 2000);

        // for (let i = 0; i < 10; i++) {
        //     setLogs(prevLogs => [
        //         ...prevLogs, 
        //         { message: "App State Provider mounted", time: "14:30:00", level: "INFO" },
        //         { message: "This is an error log example", time: "14:30:00", level: "ERROR" }
        //     ]);
        // }

        // const status = [-1, 0, 1, 2, 3];

        // for (let i = 0; i < 20; i++) {
        //     setAllChannels(prevChannels => ({
        //         ...prevChannels,
        //         [i]: {
        //             name: `Channel ${i}Channel ${i}Channel ${i}`,
        //             logo: `https://placehold.co/400x400?text=C${i}`,
        //             status: status[Math.floor(Math.random() * status.length)]
        //         }
        //     }));
        // }
                    
    }, []);

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