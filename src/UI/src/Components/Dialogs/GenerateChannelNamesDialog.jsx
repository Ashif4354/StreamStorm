import { useState, useEffect } from "react";
import {
    Alert,
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    TextField,
    useColorScheme
} from "@mui/material";
import { useNotifications } from "@toolpad/core/useNotifications";
import { logEvent } from "firebase/analytics";
import * as atatus from "../../lib/atatus";

import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";
import { useAppState } from "../../context/AppStateContext";
import { analytics } from "../../config/firebase";

const GenerateChannelNamesDialog = ({ open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const { hostAddress, defaultAIProvider, defaultAIModel } = useAppState();
    const notifications = useNotifications();

    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [helperText, setHelperText] = useState("");

    const isProviderConfigured = defaultAIProvider !== null && defaultAIProvider !== undefined;

    useEffect(() => {
        if (open) {
            atatus.setViewName('/dialog/ai-generate-channel-names');
            atatus.setViewContext({ provider: defaultAIProvider, model: defaultAIModel });
        }
    }, [open, defaultAIProvider, defaultAIModel]);

    const handleSubmit = async () => {
        if (!prompt.trim()) {
            setError(true);
            setHelperText("Enter a prompt.");
            return;
        }

        setLoading(true);
        setError(false);
        setHelperText("");

        atatus.startFeatureOperation('ai-generate-channel-names', { provider: defaultAIProvider, model: defaultAIModel });
        atatus.startDurationVital('ai-generate-channel-names');
        atatus.addAction('ai-generate-channel-names-submitted', { prompt: prompt.trim(), provider: defaultAIProvider, model: defaultAIModel });
        atatus.aiLogger.info('Generating channel names via AI', { prompt: prompt.trim(), provider: defaultAIProvider, model: defaultAIModel });

        try {
            const response = await fetch(`${hostAddress}/ai/generate/channel-names`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt: prompt.trim() }),
            });

            const data = await response.json();
            atatus.stopDurationVital('ai-generate-channel-names');

            if (!data.success) {
                atatus.failOperation('ai-generate-channel-names', data.error || data.message);
                setError(true);
                setHelperText(data.message || 'Failed to generate channel names.');
                if (data.error) {
                    console.error('Failed to generate channel names:', data.error);
                    atatus.addError(new Error(data.error), { response: data, tags: ['ai_generate_channel_names_failed'] });
                    atatus.aiLogger.error('Failed to generate channel names', { response: data, prompt: prompt.trim() }, new Error(data.error));
                }
                logEvent(analytics, "ai_generate_channel_names_failed");
                return;
            }

            if (!data.channelNames || data.channelNames.length === 0) {
                atatus.failOperation('ai-generate-channel-names', 'Empty channel names response');
                setError(true);
                setHelperText("No channel names were generated. Try a different prompt.");
                atatus.aiLogger.warn('No channel names returned by AI', { prompt: prompt.trim() });
                logEvent(analytics, "ai_generate_channel_names_empty");
                return;
            }

            // Return the generated channel names
            atatus.succeedOperation('ai-generate-channel-names');
            atatus.aiLogger.info('Channel names generated successfully', { count: data.channelNames.length, channelNames: data.channelNames });
            atatus.addAction('ai-generate-channel-names-success', { count: data.channelNames.length, channelNames: data.channelNames });
            logEvent(analytics, "ai_generate_channel_names_success", { count: data.channelNames.length });
            onClose(data.channelNames);
            setPrompt("");
        } catch (err) {
            atatus.stopDurationVital('ai-generate-channel-names');
            atatus.failOperation('ai-generate-channel-names', err.message);
            setError(true);
            setHelperText("Failed to connect to server. Try again.");
            notifications.show("Failed to generate channel names", {
                severity: "error",
                autoHideDuration: 3000,
            });
            atatus.addError(err, { tags: ['ai_generate_channel_names_error'], prompt: prompt.trim() });
            atatus.aiLogger.error('Network error during AI channel names generation', { prompt: prompt.trim() }, err);
            logEvent(analytics, "ai_generate_channel_names_error");
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setPrompt("");
        setError(false);
        setHelperText("");
        atatus.addAction('ai-generate-channel-names-closed');
        onClose(null);
    };

    return (
        <Dialog
            open={open}
            fullWidth
            maxWidth="sm"
            onClose={handleClose}
            sx={{
                "& .MuiDialog-paper": {
                    backgroundColor:
                        colorScheme === "light"
                            ? "var(--light-card-bg)"
                            : "var(--light-gray)",
                    backgroundImage: "none",
                    borderRadius: "var(--border-radius)",
                },
            }}
        >
            <DialogTitle sx={{ display: "flex", flexDirection: "column" }}>
                Generate Channel Names with AI
                <span
                    style={{ fontSize: "0.875rem", color: "var(--slight-light-text)" }}
                >
                    Enter a prompt to generate a list of channel names using AI.
                </span>
            </DialogTitle>
            <DialogContent>
                {!isProviderConfigured ? (
                    <Alert
                        severity="warning"
                        sx={{
                            marginTop: '8px',
                            borderRadius: 'var(--border-radius)',
                        }}
                    >
                        Set a default AI provider and model in Settings first.
                    </Alert>
                ) : (
                    <>
                        <TextField
                            multiline
                            rows={4}
                            variant="outlined"
                            label="What kind of channel names do you want and how many?"
                            placeholder="10 channel names for a gaming channel"
                            fullWidth
                            value={prompt}
                            onChange={(e) => {
                                setPrompt(e.target.value);
                                setError(false);
                                setHelperText("");
                            }}
                            error={error}
                            helperText={helperText}
                            margin="normal"
                            disabled={loading}
                            sx={inputProps}
                        />
                        {defaultAIModel && (
                            <span
                                style={{
                                    fontSize: "0.75rem",
                                    color: colorScheme === "light"
                                        ? "var(--slight-dark-text)"
                                        : "var(--slight-light-text)",
                                    marginTop: "4px",
                                    display: "block"
                                }}
                            >
                                Using model: {defaultAIModel}
                            </span>
                        )}
                    </>
                )}
            </DialogContent>

            <DialogActions>
                <Button
                    variant="outlined"
                    onClick={handleClose}
                    disabled={loading}
                    data-atatus-action-name="Cancel AI Channel Names"
                    sx={{
                        ...btnProps,
                        width: "100px",
                    }}
                >
                    Cancel
                </Button>

                <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={loading || !prompt.trim() || !isProviderConfigured}
                    data-atatus-action-name="Generate AI Channel Names"
                    sx={{
                        ...btnProps,
                        width: "120px",
                        backgroundColor:
                            colorScheme === "light"
                                ? "var(--light-primary)"
                                : "var(--input-active-red-dark)",
                        "&:hover": {
                            backgroundColor:
                                colorScheme === "light"
                                ? "var(--light-primary-hover)"
                                : "var(--input-active-red-dark-hover)",
                        },
                    }}
                >
                    {loading ? (
                        <CircularProgress size={20} color="inherit" />
                    ) : (
                        "Generate"
                    )}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default GenerateChannelNamesDialog;
