import { useState, useEffect } from "react";
import { CirclePlay, ArrowUpToLine, Timer, HeartPulse, HeartCrack, TrendingUp, Terminal } from "lucide-react";
import { useColorScheme } from "@mui/material/styles";

import InfoCard from "../../../../Elements/InfoCard";
import { useSocket } from "../../../../../context/SocketContext";
import { useAppState } from "../../../../../context/AppStateContext";
import LogsBox from "../../../../Elements/LogsCard";


const LeftPanelDashboard = () => {
    const { colorScheme: theme } = useColorScheme();
    const { socket, socketConnected } = useSocket();
    const appState = useAppState();

    const [stormStatus, setStormStatus] = useState("Running");
    const [statusColor, setStatusColor] = useState("");
    const [activeInstances, setActiveInstances] = useState(0);
    const [messagesSent, setMessagesSent] = useState(0);
    const [stormDuration, setStormDuration] = useState("00:00:00");
    const [deadInstances, setDeadInstances] = useState(0);
    const [messagesRate, setMessagesRate] = useState(0);
    const [start] = useState(Date.now());

    useEffect(() => {
        if (stormStatus === "Running") {
            setStatusColor(`var(--info-card-${theme}-green)`);
        }
    }, [theme]);

    useEffect(() => {
        setInterval(() => {
            const diff = (Date.now() - start) / 1000;

            const hh = String(Math.floor(diff / 3600)).padStart(2, "0");
            const mm = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
            const ss = String(Math.floor(diff % 60)).padStart(2, "0");
            setStormDuration(`${hh}:${mm}:${ss}`);
        }, 1000);
    }, []);

    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("storm_stopped", () => {
            setStormStatus("Stopped");
            setStatusColor("var(--info-card-red)");
            appState.setStormInProgress(false);
        });

        socket.on("storm_paused", () => {
            setStormStatus("Paused");
            setStatusColor("var(--info-card-yellow)");
        });

        socket.on("storm_resumed", () => {
            setStormStatus("Running");
            setStatusColor(`var(--info-card-${theme}-green)`);
        });

        socket.on('message_rate', (data) => {
            setMessagesRate(data.message_rate);
        });

        socket.on('total_messages', (data) => {
            setMessagesSent(data.total_messages);
        });

        socket.on('instance_status', (data) => {
            if (data.status === "-1") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = -1;
                    return newChannels;
                });

                setActiveInstances(prev => prev - 1);
                setDeadInstances(prev => prev + 1);
            } else if (data.status === "0") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 0;
                    return newChannels;
                });
                setActiveInstances(prev => prev - 1);
            } else if (data.status === "1") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 1;
                    return newChannels;
                });
            } else if (data.status === "2") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 2;
                    return newChannels;
                });
                setActiveInstances(prev => prev + 1);
            } else if (data.status === "3") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 3;
                    return newChannels;
                });
            }
        });
    }, [socket, socketConnected]);

    return (
        <div className="left-panel-dashboard-container">
            <div className="info-card-container">
                <InfoCard title="Storm Status" icon={<CirclePlay size={20} />} text={stormStatus} color={statusColor} />
                <InfoCard title="Active Instances" icon={<HeartPulse size={20} />} text={activeInstances} color={`var(--info-card-${theme}-green)`} />
                <InfoCard title="Messages Sent" icon={<ArrowUpToLine size={20} />} text={messagesSent} color="" />
                <InfoCard title="Storm Duration" icon={<Timer size={20} />} text={stormDuration} color="" />
                <InfoCard title="Dead Instances" icon={<HeartCrack size={20} />} text={deadInstances} color="var(--info-card-red)" />
                <InfoCard title="Messages Rate" icon={<TrendingUp size={20} />} text={messagesRate} color="" />
            </div>
            <div className="logs-box-container">
                <LogsBox />
            </div>

        </div >

    );
}


export default LeftPanelDashboard;