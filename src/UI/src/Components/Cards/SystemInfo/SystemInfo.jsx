import { useEffect, useState } from "react";
import { useColorScheme } from "@mui/material/styles";
import Card from "@mui/material/Card";
import { CardHeader, CardContent, Divider } from "@mui/material";
import { HardDrive } from "lucide-react";

import "./SystemInfo.css";
import * as atatus from "../../../lib/atatus";
import { useSystemInfo } from "../../../context/SystemInfoContext";
import { useCustomMUIProps } from "../../../context/SystemInfoContext";
import { useCustomMUIProps as useMUIProps } from "../../../context/CustomMUIPropsContext";
import SystemInfoChart from "./SystemInfoChart";
import { useSocket } from "../../../context/SocketContext";
import SystemStatsCard from "./SystemStatsCard";
import { TIME_INTERVAL_IN_SEC } from "../../../lib/Constants";

const DATA_POINTS_LENGTH = 60 / TIME_INTERVAL_IN_SEC;
const START_POINT =
    -(DATA_POINTS_LENGTH * TIME_INTERVAL_IN_SEC) + TIME_INTERVAL_IN_SEC;

const SystemInfo = () => {
    const { cardProps } = useMUIProps();
    const systemInfoControls = useSystemInfo();
    const { colorScheme } = useColorScheme();

    const onIconClick = () => {
        systemInfoControls.setDebugCounter((prev) => {
            const next = prev + 1;
            atatus.addAction("debug-icon-click", { count: next });
            return next;
        });
    };

    const createInitialPoints = () => {
        return Array.from({ length: DATA_POINTS_LENGTH }, (_, idx) => ({
            timeStep: START_POINT + TIME_INTERVAL_IN_SEC * idx,
            cpu_percent: 0,
            ram_percent: 0,
            used_ram_gb: 0,
            free_ram_percent: 0,
            free_ram_gb: 0,
            free_ram_mb: 0,
        }));
    };

    const initialData = createInitialPoints();
    const [chartSeries, setChartSeries] = useState(initialData);
    const { socket, socketConnected } = useSocket();

    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("system_metrics", (data) => {
            systemInfoControls.setAvailableRAM(data.free_ram_mb);
            atatus.setGlobalContextProperty("systemMetrics", {
                cpuPercent: data.cpu_percent,
                ramPercent: data.ram_percent,
                freeRamMb: data.free_ram_mb,
                usedRamGb: data.used_ram_gb,
            });
            setChartSeries((prev) => {
                const incoming = { ...data };

                const last = [...prev, incoming].slice(-DATA_POINTS_LENGTH);

                return last.map((item, idx) => ({
                    ...item,
                    timeStep: START_POINT + TIME_INTERVAL_IN_SEC * idx,
                }));
            });
        });

        return () => {
            socket.off("system_metrics");
        };
    }, [socket, socketConnected]);

    return (
        <Card
            className={`system-info-card ${colorScheme}-bordered-container`}
            sx={{
                ...cardProps,
                color:
                    colorScheme === "light" ? "var(--dark-text)" : "var(--light-text)",
            }}
        >
            <div className="card-header-container">
                <CardHeader
                    avatar={<HardDrive data-atatus-action-name="icon-system-info-debug" onClick={onIconClick} />}
                    title="System Information"
                    className={`card-header card-header-${colorScheme}`}
                    sx={{
                        padding: 0,
                    }}
                />
                <span
                    className={`card-header-description card-header-description-${colorScheme}`}
                >
                    Live CPU and RAM usage for the last minute.
                </span>
            </div>
            <CardContent
                sx={{
                    padding: 0,
                }}
            >
                <div className="system-info-container">
                    <SystemInfoChart series={chartSeries} colorScheme={colorScheme} />
                    <Divider sx={{ marginY: "20px" }} />
                    <SystemStatsCard
                        stats={chartSeries[chartSeries.length - 1]}
                        note={`To operate one account you need approximately ${systemInfoControls.RAM_PER_PROFILE}MB of RAM. ${systemInfoControls.availableRAM
                            ? `Since you have ${systemInfoControls.availableRAM} MB of RAM available, you can run approximately ${Math.floor(systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE)} channels.`
                            : "RAM information is currently unavailable."
                            }`}
                    />
                </div>
            </CardContent>
        </Card>
    );
};

export default SystemInfo;
