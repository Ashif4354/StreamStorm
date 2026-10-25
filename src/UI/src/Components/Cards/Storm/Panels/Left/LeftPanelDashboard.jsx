import { useState, useEffect, useRef } from "react";
import { CirclePlay, ArrowUpToLine, Timer, HeartPulse, HeartCrack, TrendingUp } from "lucide-react";
import { useColorScheme } from "@mui/material/styles";

import * as atatus from "../../../../../lib/atatus";
import InfoCard from "../../../../Elements/InfoCard";
import { useSocket } from "../../../../../context/SocketContext";
import { useAppState } from "../../../../../context/AppStateContext";
import LogsBox from "../../../../Elements/LogsCard";
import { useServerContext } from "../../../../../context/ServerContext";


const LeftPanelDashboard = () => {
    const { colorScheme: theme } = useColorScheme();
    const { socket, socketConnected } = useSocket();
    const appState = useAppState();
    const serverContext = useServerContext();

    const [stormStatus, setStormStatus] = useState("Running");
    const [statusColor, setStatusColor] = useState("");
    const [activeInstances, setActiveInstances] = useState(0);
    const [messagesSent, setMessagesSent] = useState(0);
    const [stormDuration, setStormDuration] = useState("00:00:00");
    const [deadInstances, setDeadInstances] = useState(0);
    const [messagesRate, setMessagesRate] = useState(0);
    const [previousActiveInstances, setPreviousActiveInstances] = useState(0);
    const instanceCountChangedOnceRef = useRef(false);

    useEffect(() => {
        if (stormStatus === "Running") {
            setStatusColor(`var(--info-card-${theme}-green)`);
        }
    }, [theme, stormStatus]);

    useEffect(() => {
        if (serverContext.serverContextFetched) {
            setStormStatus(serverContext.stormStatus);
            appState.setAllChannels(serverContext.channelsStatus);
        }
    }, [serverContext.serverContextFetched]);

    useEffect(() => {
        const interval = setInterval(() => {
            const diff = (Date.now() - serverContext.startTime) / 1000;

            const hh = String(Math.floor(diff / 3600)).padStart(2, "0");
            const mm = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
            const ss = String(Math.floor(diff % 60)).padStart(2, "0");
            setStormDuration(`${hh}:${mm}:${ss}`);
        }, 1000);

        return () => {
            clearInterval(interval);
        };

    }, [serverContext.startTime]);

    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("storm_stopped", () => {
            setStormStatus("Stopped");
            setStatusColor("var(--info-card-red)");
            appState.setStormInProgress(false);
            appState.setStormStatus("Stopped");
            atatus.addAction("socket-storm-stopped");
            atatus.setViewContextProperty("stormStatus", "Stopped");
            atatus.stormLogger.info("Received storm_stopped event from engine");
        });

        socket.on("storm_paused", () => {
            setStormStatus("Paused");
            setStatusColor("var(--info-card-yellow)");
            appState.setStormStatus("Paused");
            atatus.addAction("socket-storm-paused");
            atatus.setViewContextProperty("stormStatus", "Paused");
            atatus.stormLogger.info("Received storm_paused event from engine");
        });

        socket.on("storm_resumed", () => {
            setStormStatus("Running");
            setStatusColor(`var(--info-card-${theme}-green)`);
            appState.setStormStatus("in Progress");
            atatus.addAction("socket-storm-resumed");
            atatus.setViewContextProperty("stormStatus", "Running");
            atatus.stormLogger.info("Received storm_resumed event from engine");
        });

        socket.on('messages_rate', (data) => {
            const rate = parseFloat(data.message_rate).toFixed(2);
            setMessagesRate(rate);
            atatus.setViewContextProperty("messagesRate", rate);
        });

        socket.on('total_messages', (data) => {
            setMessagesSent(data.total_messages);
            atatus.setViewContextProperty("messagesSent", data.total_messages);
        });

        socket.on('instance_status', (data) => {
            atatus.stormLogger.debug(`Instance ${data.instance} status updated to ${data.status}`, data);
            if (data.status === "-1") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    if (newChannels[data.instance]) newChannels[data.instance].status = -1;
                    return newChannels;
                });
            } else if (data.status === "0") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    if (newChannels[data.instance]) newChannels[data.instance].status = 0;
                    return newChannels;
                });
                atatus.addAction("channel-instance-dead", { instance: data.instance });
            } else if (data.status === "1") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    if (newChannels[data.instance]) newChannels[data.instance].status = 1;
                    return newChannels;
                });
            } else if (data.status === "2") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    if (newChannels[data.instance]) newChannels[data.instance].status = 2;
                    return newChannels;
                });
            } else if (data.status === "3") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    if (newChannels[data.instance]) newChannels[data.instance].status = 3;
                    return newChannels;
                });
            }
        });

        return () => {
            socket.off("storm_stopped");
            socket.off("storm_paused");
            socket.off("storm_resumed");
            socket.off("messages_rate");
            socket.off("total_messages");
            socket.off("instance_status");
        };

    }, [socket, socketConnected, theme]);

    useEffect(() => {
        if (!instanceCountChangedOnceRef.current) {
            instanceCountChangedOnceRef.current = true;
            return;
        }

        if (activeInstances === 0 && previousActiveInstances !== 0) {
            console.log("All instances are dead or inactive. Stopping storm.");
            atatus.stormLogger.warn("All instances are dead or inactive. Stopping storm.", {
                previousActiveInstances,
                deadInstances,
                messagesSent,
            });
            atatus.addAction("storm-auto-stopped-all-dead", {
                deadInstances,
                messagesSent,
            });
            setStormStatus("Stopped");
            setStatusColor("var(--info-card-red)");
            instanceCountChangedOnceRef.current = false;
            appState.setStormInProgress(false);
            appState.setStormStatus("Stopped");
        }
        setPreviousActiveInstances(activeInstances);
    }, [activeInstances]);


    useEffect(() => {
        const channels = Object.values(appState.allChannels);
        const active = channels.filter(channel => channel.status > 0).length;
        const dead = channels.filter(channel => channel.status === 0).length;
        setActiveInstances(active);
        setDeadInstances(dead);
        atatus.setViewContextProperty("activeInstances", active);
        atatus.setViewContextProperty("deadInstances", dead);
    }, [appState.allChannels]);

    return (
        <div className="left-panel-dashboard-container">
            <div className="info-card-container">
                <InfoCard title="Storm Status" icon={<CirclePlay size={20} />} text={stormStatus} color={statusColor} />
                <InfoCard title="Active Instances" icon={<HeartPulse size={20} />} text={activeInstances} color={`var(--info-card-${theme}-green)`} />
                <InfoCard title="Messages Sent" icon={<ArrowUpToLine size={20} />} text={messagesSent} color="" />
                <InfoCard title="Storm Duration" icon={<Timer size={20} />} text={stormDuration} color="" />
                <InfoCard title="Dead Instances" icon={<HeartCrack size={20} />} text={deadInstances} color="var(--info-card-red)" />
                <InfoCard title="Messages Rate" icon={<TrendingUp size={20} />} text={`${messagesRate} / min`} color="" />
            </div>
            <div className="logs-box-container">
                <LogsBox />
            </div>

        </div>
    );
};

export default LeftPanelDashboard;
