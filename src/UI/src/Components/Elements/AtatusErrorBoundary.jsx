import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { RefreshCw, AlertTriangle } from 'lucide-react';
import * as atatus from '../../lib/atatus';

class AtatusErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        atatus.startSessionReplayRecording();
        const replayUrl = atatus.getSessionReplayLink();

        atatus.addError(error, {
            componentStack: errorInfo?.componentStack,
            boundary: 'AtatusErrorBoundary',
            sessionReplayUrl: replayUrl,
        });

        atatus.systemLogger.error('React render error caught by AtatusErrorBoundary', {
            componentStack: errorInfo?.componentStack,
            sessionReplayUrl: replayUrl,
        }, error);
    }

    handleReload = () => {
        atatus.addAction('error-boundary-retry-clicked');
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '100vh',
                        padding: 3,
                        textAlign: 'center',
                        backgroundColor: '#1a1a1a',
                        color: '#ffffff',
                    }}
                >
                    <AlertTriangle size={56} color="#f44336" style={{ marginBottom: 16 }} />
                    <Typography variant="h4" gutterBottom fontWeight="bold">
                        Something went wrong
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#aaaaaa', maxWidth: 500, marginBottom: 3 }}>
                        An unexpected application error occurred. A sanitized error report is sent to Atatus when telemetry is available.
                    </Typography>
                    {this.state.error?.message && (
                        <Box
                            sx={{
                                backgroundColor: '#2a2a2a',
                                border: '1px solid #444',
                                borderRadius: '8px',
                                padding: 2,
                                marginBottom: 3,
                                maxWidth: '80%',
                                overflowX: 'auto',
                                fontFamily: 'monospace',
                                fontSize: '0.875rem',
                                color: '#ff8a80',
                            }}
                        >
                            {this.state.error.message}
                        </Box>
                    )}
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<RefreshCw size={18} />}
                        onClick={this.handleReload}
                        data-atatus-action-name="ErrorBoundary Reload App"
                        sx={{
                            backgroundColor: '#d32f2f',
                            '&:hover': { backgroundColor: '#b71c1c' },
                            paddingX: 3,
                            paddingY: 1,
                        }}
                    >
                        Reload StreamStorm
                    </Button>
                </Box>
            );
        }

        return this.props.children;
    }
}

export default AtatusErrorBoundary;
