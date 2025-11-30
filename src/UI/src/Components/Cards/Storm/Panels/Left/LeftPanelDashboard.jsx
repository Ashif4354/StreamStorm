import { useState, useEffect, useRef } from "react";
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
    const [startTime, setStartTime] = useState(Date.now());
    const [previousActiveInstances, setPreviousActiveInstances] = useState(0);
    const instanceCountChangedOnceRef = useRef(false);

    useEffect(() => {
        if (stormStatus === "Running") {
            setStatusColor(`var(--info-card-${theme}-green)`);
        }
    }, [theme]);

    useEffect(() => {
        fetch(appState.hostAddress + "/storm/start_time")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let time = new Date(data.start_time).getTime();
                    console.log("Storm Start Time:", time);
                    setStartTime(time);
                }
            })
            .catch(error => {
                console.error("Error fetching storm start time:", error);
            });
    }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            const diff = (Date.now() - startTime) / 1000;

            const hh = String(Math.floor(diff / 3600)).padStart(2, "0");
            const mm = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
            const ss = String(Math.floor(diff % 60)).padStart(2, "0");
            setStormDuration(`${hh}:${mm}:${ss}`);
        }, 1000);

        return () => {
            clearInterval(interval);
        };

    }, [startTime]);

    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("storm_stopped", () => {
            setStormStatus("Stopped");
            setStatusColor("var(--info-card-red)");
            appState.setStormInProgress(false);
            appState.setStormStatus("Stopped");
        });

        socket.on("storm_paused", () => {
            setStormStatus("Paused");
            setStatusColor("var(--info-card-yellow)");
            appState.setStormStatus("Paused");
        });

        socket.on("storm_resumed", () => {
            setStormStatus("Running");
            setStatusColor(`var(--info-card-${theme}-green)`);
            appState.setStormStatus("in Progress");
        });

        socket.on('messages_rate', (data) => {
            setMessagesRate(parseFloat(data.message_rate).toFixed(2));
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
                // setActiveInstances(prev => prev - 1);

            } else if (data.status === "0") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 0;
                    return newChannels;
                });
                // setActiveInstances(prev => prev - 1);
                // setDeadInstances(prev => prev + 1);

            } else if (data.status === "1") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 1;
                    return newChannels;
                });
                // setActiveInstances(prev => prev + 1);

            } else if (data.status === "2") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 2;
                    return newChannels;
                });

            } else if (data.status === "3") {
                appState.setAllChannels(prev => {
                    const newChannels = { ...prev };
                    newChannels[data.instance].status = 3;
                    return newChannels;
                });
            }
        });

        return () => {
            socket.off("storm_stopped");
            socket.off("storm_paused");
            socket.off("storm_resumed");
            socket.off("message_rate");
            socket.off("total_messages");
            socket.off("instance_status");
        };

    }, [socket, socketConnected]);

    useEffect(() => {
        console.log(instanceCountChangedOnceRef.current, activeInstances);
        if (!instanceCountChangedOnceRef.current) {
            instanceCountChangedOnceRef.current = true;
            return;
        }

        if (activeInstances === 0 && previousActiveInstances !== 0) {
            console.log("All instances are dead or inactive. Stopping storm.");
            setStormStatus("Stopped");
            setStatusColor("var(--info-card-red)");
            instanceCountChangedOnceRef.current = false;
            appState.setStormInProgress(false);
            appState.setStormStatus("Stopped");
        }
        setPreviousActiveInstances(activeInstances);
    }, [activeInstances]);


    useEffect(() => { // Runs once on mount to initialize instance counts
        const channels = Object.values(appState.allChannels);
        const active = channels.filter(channel => channel.status > 0).length;
        const dead = channels.filter(channel => channel.status === 0).length;
        setActiveInstances(active);
        setDeadInstances(dead);
    }, [appState.allChannels]);

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