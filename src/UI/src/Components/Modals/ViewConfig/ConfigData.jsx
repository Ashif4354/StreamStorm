import { Link, Users, Clock, UserCheck, Package } from "lucide-react";

import TextBasedConfig from "./TextBasedConfig";
import ChipBasedConfig from "./ChipBasedConfig";
import MessagesConfig from "./MessagesConfig";
import { useStormData } from "../../../context/StormDataContext";

const ConfigData = () => {

    const formControls = useStormData();
    const stormConfig = formControls.getStormData();

    return (
        <div className='config-data-container'>
            <TextBasedConfig icon={<Link size={16} />} title="Video URL" value={formControls.videoURL} />
            <TextBasedConfig icon={<Users size={16} />} title="Channels initially" value={`${stormConfig.channels.length} (${formControls.channelSelection})`} />
            <TextBasedConfig icon={<Clock size={16} />} title="Slow Mode" value={`${formControls.slowMode}s`} />
            <ChipBasedConfig icon={<UserCheck size={16} />} title="Subscribe" value="Enabled" disabled={!formControls.subscribe} />
            {
                formControls.subscribeAndWait && (
                    <ChipBasedConfig icon={<UserCheck size={16} />} title="Subscribe and Wait" value={`Enabled (${formControls.subscribeWaitTime}s)`} disabled={!stormConfig.subscribeAndWait} />
                )
            }
            <ChipBasedConfig icon={<Package size={16} />} title="Load in Background" value="Enabled" disabled={!formControls.loadInBackground} />
            <MessagesConfig messages={formControls.messages} />
        </div>
    );
};

export default ConfigData;
