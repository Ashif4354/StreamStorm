import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import Card from '@mui/material/Card';
import { CardHeader, CardContent, Button } from "@mui/material";
import { HardDrive, RefreshCw } from 'lucide-react';
import { useLocalStorageState } from '@toolpad/core/useLocalStorageState';
import { useNotifications } from '@toolpad/core/useNotifications';

import "./SystemInfo.css"
import { useSystemInfo } from '../../../context/SystemInfoContext';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import { useSocket } from '../../../context/Socket';

const SystemInfo = () => {
    const { btnProps, cardProps } = useCustomMUIProps();
    const systemInfoControls = useSystemInfo();
    const { colorScheme } = useColorScheme();
    const notifications = useNotifications();

    const [fetchingRAM, setFetchingRAM] = useState(false);
    const [hostAddress] = useLocalStorageState('hostAddress');

    const { socket, socketConnected } = useSocket();
    
    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("system_info", (data) => {
            console.log("Received system_info:", data);

            // Use the data received to plot the graph
        });

    }, [socket, socketConnected]);

    const refreshRAM = async () => {
        setFetchingRAM(true);
        await systemInfoControls.fetchRAM(hostAddress, notifications, systemInfoControls);
        setFetchingRAM(false);
    }

    const onIconClick = () => {
        systemInfoControls.setDebugList(prev => [...prev, 0])
    }

    useEffect(() => {
        const interval = setInterval(async () => {
            await systemInfoControls.fetchRAM(hostAddress, notifications, systemInfoControls);
        }, 1000);

        systemInfoControls.setPollingIntervals(prev => [...prev, interval]);

        return () => clearInterval(interval);
    }, [hostAddress]);

    return (
        <Card
            className={`system-info-card ${colorScheme}-bordered-container`}
            sx={{
                ...cardProps,
                color: colorScheme === 'light' ? "var(--dark-text)" : "var(--light-text)",
            }}
        >
            <div className="card-header-container">
                <CardHeader
                    avatar={<HardDrive onClick={onIconClick} />}
                    title="System Information"
                    className={`card-header card-header-${colorScheme}`}
                    sx={{
                        padding: 0,
                    }}
                />
                <span className={`card-header-description card-header-description-${colorScheme}`}>
                    View Current System Information.
                </span>
            </div>
            <CardContent
                sx={{
                    padding: 0,
                }}
            >
                <div className="system-info-container">
                    <div className="system-info-item">
                        <div className="ram-value-container">
                            <span className="ram-label">Available RAM:</span>
                            <span className={`ram-value-${colorScheme}`}>{systemInfoControls.availableRAM ? `${systemInfoControls.availableRAM} MB` : "N/A"}</span>
                        </div>
                        <Button
                            startIcon={<RefreshCw size={15} className={fetchingRAM ? "spin" : ""} />}
                            variant="contained"
                            sx={{
                                ...btnProps,
                                marginTop: "1rem"
                            }}
                            onClick={refreshRAM}
                        >
                            Refresh RAM
                        </Button>
                        <span className='ram-note'>
                            To operate one channel you need approximately {systemInfoControls.RAM_PER_PROFILE}MB of Free RAM.

                        </span>
                        <span className='ram-note'>
                            {
                                systemInfoControls.availableRAM ? (
                                    `Since you have ${systemInfoControls.availableRAM} MB of RAM available, you can run approximately ${Math.floor(systemInfoControls.availableRAM / systemInfoControls.RAM_PER_PROFILE)} channels.`
                                ) : (
                                    "RAM information is currently unavailable."
                                )
                            }
                        </span>
                    </div>
                </div>

            </CardContent>
        </Card>
    );
}


export default SystemInfo; 