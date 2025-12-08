/* eslint-disable react-refresh/only-export-components */
/* eslint-disable react/prop-types */
import { createContext, useState, useRef, useContext } from 'react';
import { useNotifications } from "@toolpad/core/useNotifications";
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { DEFAULT_HOST_ADDRESS } from '../lib/Constants';

const StormDataContext = createContext();

const StormDataProvider = ({ children }) => {

    const notifications = useNotifications();
    const [hostAddress] = useLocalStorageState('hostAddress', DEFAULT_HOST_ADDRESS);

    const SC = useRef(null);

    const [loading, setLoading] = useState(false);
    const [stormInProgress, setStormInProgress] = useState(false);

    const [videoURL, setVideoURL] = useState("");
    const [videoURLError, setVideoURLError] = useState(false);
    const [videoURLHelperText, setVideoURLHelperText] = useState("");

    const [chatURL, setChatURL] = useState("");

    const [messages, setMessages] = useState([]);
    const [messagesString, setMessagesString] = useState("");
    const [messagesError, setMessagesError] = useState(false);
    const [messagesHelperText, setMessagesHelperText] = useState("");

    const [subscribe, setSubscribe] = useState(false);
    const [subscribeAndWait, setSubscribeAndWait] = useState(false);

    const [subscribeWaitTime, setSubscribeWaitTime] = useState(65);
    const [subscribeWaitTimeError, setSubscribeWaitTimeError] = useState(false);
    const [subscribeWaitTimeHelperText, setSubscribeWaitTimeHelperText] = useState("");

    const [slowMode, setSlowMode] = useState(5);
    const [slowModeError, setSlowModeError] = useState(false);
    const [slowModeHelperText, setSlowModeHelperText] = useState("");

    const [channelSelection, setChannelSelection] = useState('basic');

    const [noOfChannels, setNoOfChannels] = useState(1);
    const [noOfChannelsError, setNoOfChannelsError] = useState(false);
    const [noOfChannelsHelperText, setNoOfChannelsHelperText] = useState("");

    const [startChannelIndex, setStartChannelIndex] = useState(1);
    const [startChannelIndexError, setStartChannelIndexError] = useState(false);
    const [startChannelIndexHelperText, setStartChannelIndexHelperText] = useState("");

    const [endChannelIndex, setEndChannelIndex] = useState(0);
    const [endChannelIndexError, setEndChannelIndexError] = useState(false);
    const [endChannelIndexHelperText, setEndChannelIndexHelperText] = useState("");

    const [advancedSelectedChannels, setAdvancedSelectedChannels] = useState([]);
    const [advancedChannelsErrorText, setAdvancedChannelsErrorText] = useState("");

    const [loadInBackground, setLoadInBackground] = useState(false);
    const [errorText, setErrorText] = useState("");  
    const [engineVersion, setEngineVersion] = useState('...');  

    const getChannels = () => {
        const getRange = (start, end) => {
            const range = [];
            
            for (let i = start; i <= end; i++) {
                range.push(i);
            }

            return range;
        }

        if (channelSelection === 'basic') {
            return getRange(1, noOfChannels);
        } else if (channelSelection === 'intermediate') {
            return getRange(startChannelIndex, endChannelIndex);
        } else if (channelSelection === 'advanced') {
            return advancedSelectedChannels;
        }
    }

    const formControls = {
        loading, setLoading, stormInProgress, setStormInProgress, notifications,
        videoURL, setVideoURL, videoURLError, setVideoURLError, videoURLHelperText, setVideoURLHelperText, chatURL, setChatURL,
        messages, setMessages, messagesString, setMessagesString, messagesError, setMessagesError, messagesHelperText, setMessagesHelperText,
        subscribe, setSubscribe, subscribeAndWait, setSubscribeAndWait,
        subscribeWaitTime, setSubscribeWaitTime, subscribeWaitTimeError, setSubscribeWaitTimeError, subscribeWaitTimeHelperText, setSubscribeWaitTimeHelperText,
        slowMode, setSlowMode, slowModeError, setSlowModeError, slowModeHelperText, setSlowModeHelperText,
        channelSelection, setChannelSelection,
        noOfChannels, setNoOfChannels, noOfChannelsError, setNoOfChannelsError, noOfChannelsHelperText, setNoOfChannelsHelperText,
        startChannelIndex, setStartChannelIndex, startChannelIndexError, setStartChannelIndexError, startChannelIndexHelperText, setStartChannelIndexHelperText,
        endChannelIndex, setEndChannelIndex, endChannelIndexError, setEndChannelIndexError, endChannelIndexHelperText, setEndChannelIndexHelperText,
        advancedSelectedChannels, setAdvancedSelectedChannels, advancedChannelsErrorText, setAdvancedChannelsErrorText,
        loadInBackground, setLoadInBackground, errorText, setErrorText,
        hostAddress, SC, engineVersion, setEngineVersion,

        getStormData: () => {
            return {
                videoUrl: videoURL,
                chatUrl: "https://www.youtube.com/live_chat?v=" + videoURL.split('v=')[1],
                messages,
                subscribe,
                subscribeAndWait,
                subscribeAndWaitTime: subscribeWaitTime,
                slowMode,
                background: loadInBackground,
                channels: getChannels(),
            };
        }
    }

    return (
        <StormDataContext.Provider value={formControls}>
            {children}
        </StormDataContext.Provider>
    )
}

const useStormData = () => {
    return useContext(StormDataContext);
}

export { StormDataProvider, useStormData }
