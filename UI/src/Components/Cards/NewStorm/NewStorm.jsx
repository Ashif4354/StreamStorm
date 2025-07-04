import { useContext, useEffect, useRef, useState } from "react";
import { useColorScheme } from '@mui/material/styles';
import { useNotifications } from "@toolpad/core/useNotifications";
import Card from '@mui/material/Card';
import { CardHeader, CardContent, Divider } from "@mui/material";
import { Settings2 } from 'lucide-react';

import "./NewStorm.css";
import LeftPanel from "./Panels/Left/LeftPanel";
import RightPanel from "./Panels/Right/RightPanel";
import { CustomMUIPropsContext } from "../../../lib/ContextAPI";
import ManageProfilesModal from "../../Modals/ManageProfiles/ManageProfiles";
import { StormDataContext } from "../../../lib/ContextAPI";
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import StormControlsClass from "../../../lib/StormControlsClass";

const NewStorm = () => {
    const { cardProps } = useContext(CustomMUIPropsContext);
    const { colorScheme } = useColorScheme();
    const notifications = useNotifications();
    const [hostAddress] = useLocalStorageState('hostAddress');
    const [manageProfilesOpen, setManageProfilesOpen] = useState(false);

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

    const [subscribeWaitTime, setSubscribeWaitTime] = useState(0);
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

    const [browser, setBrowser] = useState('');
    const [browserError, setBrowserError] = useState(false);
    const [browserHelperText, setBrowserHelperText] = useState("");

    const [loadInBackground, setLoadInBackground] = useState(false);
    const [errorText, setErrorText] = useState("");



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
        browser, setBrowser, browserError, setBrowserError, browserHelperText, setBrowserHelperText,
        loadInBackground, setLoadInBackground, errorText, setErrorText,
        hostAddress, SC,

        getStormData: () => {
            return {
                video_url: videoURL,
                chat_url: "https://www.youtube.com/live_chat?v=" + videoURL.split('v=')[1],
                messages: messages,
                subscribe: subscribe,
                subscribe_and_wait: subscribeAndWait,
                subscribe_and_wait_time: subscribeWaitTime,
                slow_mode: slowMode,
                // start_channel_index: channelSelection === 'basic' ? 1 : startChannelIndex,
                // end_channel_index: channelSelection === 'basic' ? noOfChannels : endChannelIndex,
                browser: browser,
                background: loadInBackground,
                channels: getChannels(),
            };
        }
    };

    return (
        <Card
            className={
                `new-storm-card  ${colorScheme}-bordered-container`
            }
            sx={cardProps}
        >
            <div className="card-header-container" id="new-storm">
                <CardHeader
                    avatar={<Settings2 />}
                    title="New Storm"
                    className={`card-header card-header-${colorScheme}`}
                    sx={{
                        padding: 0
                    }}
                />
                <span className={`card-header-description card-header-description-${colorScheme}`}>
                    Set up parameters for your new storm and manage active storm.
                </span>
            </div>
            <CardContent
                sx={{
                    padding: 0,
                }}
            >
                <div className="new-storm-card-content">
                    <StormDataContext.Provider value={formControls}>
                        <LeftPanel />
                        <Divider orientation="vertical" />
                        <RightPanel setManageProfilesOpen={setManageProfilesOpen} />
                    </StormDataContext.Provider>
                </div>
            </CardContent>

            <ManageProfilesModal open={manageProfilesOpen} setOpen={setManageProfilesOpen} />
        </Card>
    );
}

export default NewStorm;