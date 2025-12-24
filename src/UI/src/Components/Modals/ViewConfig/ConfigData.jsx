import { Link, Users, Clock, UserCheck, Package } from "lucide-react";

import TextBasedConfig from "./TextBasedConfig";
import ChipBasedConfig from "./ChipBasedConfig";
import MessagesConfig from "./MessagesConfig";
import { useStormData } from "../../../context/StormDataContext";
import { useServerContext } from "../../../context/ServerContext";

const ConfigData = () => {

    const formControls = useStormData();

    const { stormData } = useServerContext();

    return (
        <div className='config-data-container'>
            <TextBasedConfig icon={<Link size={16} />} title="Video URL" value={stormData.video_url} />
            <TextBasedConfig
                icon={<Users size={16} />}
                title="Channels initially"
                value={`${stormData.channels.length} ${formControls.channelSelection ? `(${formControls.channelSelection})` : ""}`}
            />
            <TextBasedConfig icon={<Clock size={16} />} title="Slow Mode" value={`${stormData.slow_mode}s`} />
            <ChipBasedConfig icon={<UserCheck size={16} />} title="Subscribe" value="Enabled" disabled={!stormData.subscribe} />
            {
                stormData.subscribe_and_wait && (
                    <ChipBasedConfig
                        icon={<UserCheck size={16} />}
                        title="Subscribe and Wait"
                        value={`Enabled (${stormData.subscribe_wait_time}s)`}
                        disabled={!stormData.subscribe_and_wait}
                    />
                )
            }
            <ChipBasedConfig icon={<Package size={16} />} title="Load in Background" value="Enabled" disabled={!stormData.load_in_background} />
            <MessagesConfig messages={stormData.messages} />
        </div>
    );
};

export default ConfigData;
