import { useState } from "react";
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
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { useNotifications } from "@toolpad/core/useNotifications";
import { logEvent } from "firebase/analytics";
import * as atatus from "atatus-spa";

import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";
import { useAppState } from "../../context/AppStateContext";
import { analytics } from "../../config/firebase";

const GenerateMessagesDialog = ({ open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const [hostAddress] = useLocalStorageState("hostAddress");
    const notifications = useNotifications();
    const appState = useAppState();

    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [helperText, setHelperText] = useState("");

    const isProviderConfigured = appState.defaultAIProvider !== null && appState.defaultAIProvider !== undefined;

    const handleSubmit = async () => {
        if (!prompt.trim()) {
            setError(true);
            setHelperText("Enter a prompt.");
            return;
        }

        setLoading(true);
        setError(false);
        setHelperText("");

        try {
            const response = await fetch(`${hostAddress}/ai/generate/messages`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt: prompt.trim() }),
            });

            const data = await response.json();

            if (!data.success) {
                setError(true);
                setHelperText(data.message || "Failed to generate messages.");
                logEvent(analytics, "ai_generate_messages_failed");
                return;
            }

            if (!data.messages || data.messages.length === 0) {
                setError(true);
                setHelperText("No messages were generated. Try a different prompt.");
                logEvent(analytics, "ai_generate_messages_empty");
                return;
            }

            // Return the generated messages
            logEvent(analytics, "ai_generate_messages_success", { count: data.messages.length });
            onClose(data.messages);
            setPrompt("");
        } catch (err) {
            setError(true);
            setHelperText("Failed to connect to server. Try again.");
            notifications.show("Failed to generate messages", {
                severity: "error",
                autoHideDuration: 3000,
            });
            atatus.notify(err, {}, ['ai_generate_messages_error']);
            logEvent(analytics, "ai_generate_messages_error");
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setPrompt("");
        setError(false);
        setHelperText("");
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
