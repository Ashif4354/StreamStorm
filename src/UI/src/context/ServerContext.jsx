import { createContext, useContext, useEffect, useState } from 'react';
import * as atatus from 'atatus-spa';

import { useAppState } from './AppStateContext';
import { useStormData } from './StormDataContext';


const ServerContext = createContext();

const ServerContextProvider = ({ children }) => {

    const appState = useAppState();
    const formControls = useStormData();

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

    useEffect(() => {
        if (serverContextFetched && stormData) {
            formControls.setVideoURL(stormData.video_url);
            formControls.setChatURL(stormData.chat_url);
            formControls.setSubscribe(stormData.subscribe);
            formControls.setSubscribeAndWait(stormData.subscribe_and_wait);
            formControls.setSubscribeWaitTime(stormData.subscribe_and_wait_time);
            formControls.setSlowMode(stormData.slow_mode);
            formControls.setLoadInBackground(stormData.background);
            formControls.setMessagesString(stormData.messages.join("\n"));
            formControls.setMessages(stormData.messages);
        }        
    }, [serverContextFetched, stormData])


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