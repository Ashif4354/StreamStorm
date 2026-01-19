import { createContext, useContext, useEffect, useState } from 'react';
import * as atatus from 'atatus-spa';

import { useAppState } from './AppStateContext';
import { useStormData } from './StormDataContext';
import { useNotifications } from '@toolpad/core/useNotifications';


const ServerContext = createContext();

const ServerContextProvider = ({ children }) => {

    const appState = useAppState();
    const formControls = useStormData();
    const notifications = useNotifications();

    const [stormData, setStormData] = useState({});
    const [channelsStatus, setChannelsStatus] = useState({});
    const [stormStatus, setStormStatus] = useState("Running");
    const [startTime, setStartTime] = useState(Date.now());
    const [serverContextFetched, setServerContextFetched] = useState(false);

    const setFormControls = (context) => {
        formControls.setVideoURL(context.video_url);
        formControls.setSubscribe(context.subscribe[0]);
        formControls.setSubscribeAndWait(context.subscribe[1]);
        formControls.setSubscribeWaitTime(context.subscribe_and_wait_time);
        formControls.setSlowMode(context.slow_mode);
        formControls.setLoadInBackground(context.background);
        formControls.setMessagesString(context.messages.join("\n"));
        formControls.setMessages(context.messages);
        formControls.setChannels(context.channels);
    }


    useEffect(() => {
        if (!appState.stormInProgress) return;

        const controller = new AbortController();

        fetch(`${appState.hostAddress}/storm/context`, {
            method: 'GET',
            signal: controller.signal,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    setFormControls(data.context);
                    setChannelsStatus(data.context.all_channels);
                    setStormStatus(data.context.storm_status);
                    // setStartTime(data.context.start_time);
                    setStartTime(new Date(data.context.start_time).getTime());
                    setServerContextFetched(true);
                } else {
                    if (!data.storm) {
                        appState.setStormInProgress(false);

                        notifications.show("The storm has ended", {
                            severity: "warning",
                            autoHideDuration: 3000,
                        });
                    }
                    if (data.error) {
                        console.error('Server context error:', data.error);
                        atatus.notify(new Error(data.error), { response: data }, ['server_context_error']);
                    }
                }
            })
            .catch(error => {
                // Ignore abort errors - they're expected when component unmounts
                if (error.name === 'AbortError') return;

                console.error("Error fetching server context:", error);
                atatus.notify(error, {}, ['server_context_fetch_error']);
            });

        // Cleanup: abort fetch if component unmounts or dependencies change
        return () => controller.abort();
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