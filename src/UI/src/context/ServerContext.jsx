import { createContext, useContext, useEffect, useState } from 'react';
import * as atatus from 'atatus-spa';

import { useAppState } from './AppStateContext';


const ServerContext = createContext();

const ServerContextProvider = ({ children }) => {

    const appState = useAppState();

    const [stormData, setStormData] = useState({});
    const [channelsStatus, setChannelsStatus] = useState({});
    const [stormStatus, setStormStatus] = useState("Running");
    const [startTime, setStartTime] = useState(Date.now());
    const [serverContextFetched, setServerContextFetched] = useState(false);


    useEffect(() => {
        if (appState.stormInProgress) {
            fetch(`${appState.hostAddress}/storm/context`, {
                method: 'GET',
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        setStormData(data.context.storm_data);
                        setChannelsStatus(data.context.channels_status);
                        setStormStatus(data.context.storm_status);
                        // setStartTime(data.context.start_time);
                        setStartTime(new Date(data.context.start_time).getTime());
                        setServerContextFetched(true);
                    } else {
                        console.error("Failed to fetch server context:", data.message);
                    }
                })
                .catch(error => {
                    console.error("Error fetching server context:", error);
                    atatus.notify(error, {}, ['server_context_fetch_error']);
                });
        }
    }, [appState.stormInProgress, appState.hostAddress]);


    const values = {
        stormData, setStormData,
        channelsStatus, setChannelsStatus,
        stormStatus, setStormStatus,
        startTime, setStartTime,
        serverContextFetched,
    };

    return (
        <ServerContext.Provider value={values}>
            {children}
        </ServerContext.Provider>
    );
};

const useServerContext = () => {
    return useContext(ServerContext);
};

export { ServerContextProvider, useServerContext };