import { Card, Avatar, Chip, Button } from "@mui/material";
import { useColorScheme } from '@mui/material/styles';
import { logEvent } from "firebase/analytics";
import * as atatus from "../../../lib/atatus";

import { useAppState } from "../../../context/AppStateContext";
import { useNotifications } from "@toolpad/core/useNotifications";
import { useDialogs } from "@toolpad/core/useDialogs";
import { analytics } from "../../../config/firebase";
import AreYouSure from "../../Dialogs/AreYouSure";

const ChannelCard = (props) => {
    const { id, channel } = props;
    const { colorScheme } = useColorScheme();
    const appState = useAppState();
    const notifications = useNotifications();
    const dialogs = useDialogs();
    let statusColor, statusText, channelStatus;

    if (channel.status === undefined || channel.status === null) {
        channelStatus = -1; // Default to Idle if no status provided
    } else {
        channelStatus = channel.status;
    }

    if (channelStatus === -1) { // Idle
        statusColor = 'default';
        statusText = 'Idle';
    } else if (channelStatus === 0) { // Dead
        statusColor = 'error';
        statusText = 'Dead';
    } else if (channelStatus === 1) { // Getting Ready
        statusColor = 'secondary';
        statusText = 'Getting Ready';
    } else if (channelStatus === 2) { // Ready
        statusColor = 'info';
        statusText = 'Ready';
    } else if (channelStatus === 3) { // Storming
        statusColor = 'success';
        statusText = 'Storming';
    }

    const onHandleKillInstance = async () => {
        atatus.addAction('kill-instance-prompted', { instance: id, channelName: channel.name });
        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>Are you sure you want to <strong style={{ color: "var(--input-active-red-dark)" }}>KILL</strong> Instance {id}. {channel.name}</span>
        });

        if (confirmed) {
            atatus.startOperation('kill-instance', { instance: id, name: channel.name });
            atatus.startDurationVital('kill-instance');
            atatus.addAction('kill-instance-confirmed', { instance: id, name: channel.name });

            fetch(appState.hostAddress + `/storm/kill_instance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ index: parseInt(id), name: channel.name })
            })
                .then(response => response.json())
                .then(data => {
                    atatus.stopDurationVital('kill-instance');
                    if (data.success) {
                        atatus.succeedOperation('kill-instance');
                        atatus.stormLogger.info('Instance killed successfully', { instance: id, channelName: channel.name });
                        notifications.show('Instance Killed', { severity: 'success' });
                        logEvent(analytics, "kill_instance_success", { instance: id });
                    } else {
                        atatus.failOperation('kill-instance', data.error || data.message);
                        notifications.show(data.message || 'Failed to kill instance', { severity: 'error' });
                        if (data.error) {
                            console.error('Failed to kill instance:', data.error);
                            atatus.addError(new Error(data.error), { response: data, tags: ['kill_instance_failed'] });
                            atatus.stormLogger.error('Failed to kill instance', { response: data, instance: id }, new Error(data.error));
                        }
                        logEvent(analytics, "kill_instance_failed", { instance: id });
                    }
                })
                .catch((error) => {
                    atatus.stopDurationVital('kill-instance');
                    atatus.failOperation('kill-instance', error.message);
                    notifications.show(error.message || 'An error occurred while starting the storm', {
                        severity: 'error',
                    });
                    atatus.addError(error, { tags: ['kill_instance_error'], instance: id });
                    atatus.stormLogger.error('Error killing instance', { instance: id }, error);
                    logEvent(analytics, "kill_instance_error", { instance: id });
                });
        }
    };

    return (
        <Card
            sx={{
                height: '60px',
                minWidth: '400px',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: "var(--border-radius)",
                backgroundColor: colorScheme === 'light' ? "var(--light-card-bg)" : "var(--gray)",
                backgroundImage: "none",
                "&.MuiCard-root": {
                    overflow: 'hidden',
                    boxShadow: "none",
                },
                "@media (max-width: 580px)": {
                    minWidth: "unset",
                    height: '100px',
                }
            }}
            className={`${colorScheme}-bordered-container`}
        >
            <div className="channel-card-content">
                <Avatar
                    sx={{
                        width: 36,
                        height: 36,
                        fontSize: '0.875rem',
                        bgcolor: 'var(--primary)',
                        "@media (max-width: 580px)": {
                            width: 48,
                            height: 48,
                            fontSize: "1rem"
                        }
                    }}
                    alt={channel.name}
                    src={channel.logo}
                />
                <div className="channel-and-chip-grid">
                    <span className='channel-name' style={{ color: `var(--${colorScheme === 'light' ? 'dark' : 'light'}-text)` }}>
                        {channel.name}
                    </span>
                    <Chip
                        sx={{
                            width: '100px',
                        }}
                        variant="filled"
                        size="small"
                        color={statusColor}
                        label={statusText}
                        icon={null}
                    />
                </div>
                <Button
                    variant="outlined"
                    size="small"
                    disabled={channelStatus <= 0}
                    onClick={onHandleKillInstance}
                    data-atatus-action-name={`Kill Channel ${channel.name}`}
                    sx={{
                        minWidth: 0,
                        width: '50px',
                        height: '100%',
                        borderRadius: "0 var(--border-radius) var(--border-radius) 0",
                        "&:hover": {
                            backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                            borderColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                            color: "var(--light-text)",
                        },
                    }}
                >
                    Kill
                </Button>
            </div>
        </Card>
    );
};

export default ChannelCard;
