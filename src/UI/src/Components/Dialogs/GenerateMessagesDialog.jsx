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

const GenerateMessagesDialog = ({ open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const notifications = useNotifications();
    const appState = useAppState();

    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [helperText, setHelperText] = useState("");

    const isProviderConfigured = appState.defaultAIProvider !== null && appState.defaultAIProvider !== undefined;

    useEffect(() => {
        if (open) {
            atatus.setViewName('/dialog/ai-generate-messages');
            atatus.setViewContext({ provider: appState.defaultAIProvider, model: appState.defaultAIModel });
        }
    }, [open, appState.defaultAIProvider, appState.defaultAIModel]);

    const handleSubmit = async () => {
        if (!prompt.trim()) {
            setError(true);
            setHelperText("Enter a prompt.");
            return;
        }

        setLoading(true);
        setError(false);
        setHelperText("");

        atatus.startFeatureOperation('ai-generate-messages', { provider: appState.defaultAIProvider, model: appState.defaultAIModel });
        atatus.startDurationVital('ai-generate-messages');
        atatus.addAction('ai-generate-messages-submitted', { prompt: prompt.trim(), provider: appState.defaultAIProvider, model: appState.defaultAIModel });
        atatus.aiLogger.info('Generating messages via AI', { prompt: prompt.trim(), provider: appState.defaultAIProvider, model: appState.defaultAIModel });

        try {
            const response = await fetch(`${appState.hostAddress}/ai/generate/messages`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt: prompt.trim() }),
            });

            const data = await response.json();
            atatus.stopDurationVital('ai-generate-messages');

            if (!data.success) {
                atatus.failOperation('ai-generate-messages', data.error || data.message);
                setError(true);
                setHelperText(data.message || 'Failed to generate messages.');
                if (data.error) {
                    console.error('Failed to generate messages:', data.error);
                    atatus.addError(new Error(data.error), { response: data, tags: ['ai_generate_messages_failed'] });
                    atatus.aiLogger.error('Failed to generate messages', { response: data, prompt: prompt.trim() }, new Error(data.error));
                }
                logEvent(analytics, "ai_generate_messages_failed");
                return;
            }

            if (!data.messages || data.messages.length === 0) {
                atatus.failOperation('ai-generate-messages', 'Empty messages response');
                setError(true);
                setHelperText("No messages were generated. Try a different prompt.");
                atatus.aiLogger.warn('No messages returned by AI', { prompt: prompt.trim() });
                logEvent(analytics, "ai_generate_messages_empty");
                return;
            }

            // Return the generated messages
            atatus.succeedOperation('ai-generate-messages');
            atatus.aiLogger.info('Messages generated successfully', { count: data.messages.length, messages: data.messages });
            atatus.addAction('ai-generate-messages-success', { count: data.messages.length, messages: data.messages });
            logEvent(analytics, "ai_generate_messages_success", { count: data.messages.length });
            onClose(data.messages);
            setPrompt("");
        } catch (err) {
            atatus.stopDurationVital('ai-generate-messages');
            atatus.failOperation('ai-generate-messages', err.message);
            setError(true);
            setHelperText("Failed to connect to server. Try again.");
            notifications.show("Failed to generate messages", {
                severity: "error",
                autoHideDuration: 3000,
            });
            atatus.addError(err, { tags: ['ai_generate_messages_error'], prompt: prompt.trim() });
            atatus.aiLogger.error('Network error during AI messages generation', { prompt: prompt.trim() }, err);
            logEvent(analytics, "ai_generate_messages_error");
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setPrompt("");
        setError(false);
        setHelperText("");
        atatus.addAction('ai-generate-messages-closed');
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
                Generate Messages with AI
                <span
                    style={{ fontSize: "0.875rem", color: "var(--slight-light-text)" }}
                >
                    Enter a prompt to generate a list of messages using AI.
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
                            label="What kind of messages do you want and how many?"
                            placeholder="10 Messages that would make IShowSpeed smile"
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
                        {appState.defaultAIModel && (
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
                                Using model: {appState.defaultAIModel}
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
                    data-atatus-action-name="Cancel AI Messages"
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
                    data-atatus-action-name="Generate AI Messages"
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

export default GenerateMessagesDialog;
