import { createContext, useContext, useEffect, useState } from 'react';
import * as atatus from '../lib/atatus';

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
    };

    useEffect(() => {
        if (!appState.stormInProgress) return;

        const controller = new AbortController();
        atatus.startOperation('fetch-server-context');
        atatus.startDurationVital('fetch-server-context');

        fetch(`${appState.hostAddress}/storm/context`, {
            method: 'GET',
            signal: controller.signal,
        })
            .then(response => response.json())
            .then(data => {
                atatus.stopDurationVital('fetch-server-context');
                if (data.success) {
                    atatus.succeedOperation('fetch-server-context');
                    setFormControls(data.context);
                    setChannelsStatus(data.context.all_channels);
                    setStormStatus(data.context.storm_status);
                    setStartTime(new Date(data.context.start_time).getTime());
                    setServerContextFetched(true);
                    atatus.setGlobalContextProperty('activeStormChannelsCount', Object.keys(data.context?.all_channels || {}).length);
                    atatus.serverLogger.info('Server storm context loaded', {
                        storm_status: data.context.storm_status,
                        channels_count: Object.keys(data.context?.all_channels || {}).length,
                    });
                } else {
                    atatus.failOperation('fetch-server-context', data.message || 'Storm ended or error');
                    if (!data.storm) {
                        appState.setStormInProgress(false);
                        notifications.show("The storm has ended", {
                            severity: "warning",
                            autoHideDuration: 3000,
                        });
                        atatus.serverLogger.warn('Storm ended on server');
                    }
                    if (data.error) {
                        console.error('Server context error:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['server_context_error'] });
                        atatus.serverLogger.error('Server context returned error', { response: data }, new Error(data.error));
                    }
                }
            })
            .catch(error => {
                atatus.stopDurationVital('fetch-server-context');
                // Ignore abort errors - they're expected when component unmounts
                if (error.name === 'AbortError') return;

                atatus.failOperation('fetch-server-context', error.message);
                console.error("Error fetching server context:", error);
                atatus.addError(error, { tags: ['server_context_fetch_error'] });
                atatus.serverLogger.error('Failed to fetch server context', {}, error);
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
