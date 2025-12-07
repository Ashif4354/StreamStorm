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
import { useNotifications } from "@toolpad/core/useNotifications";

import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";
import { useAppState } from "../../context/AppStateContext";

const GenerateChannelNamesDialog = ({ open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const { hostAddress, defaultAIProvider } = useAppState();
    const notifications = useNotifications();

    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [helperText, setHelperText] = useState("");

    const isProviderConfigured = defaultAIProvider !== null && defaultAIProvider !== undefined;

    const handleSubmit = async () => {
        if (!prompt.trim()) {
            setError(true);
            setHelperText("Please enter a prompt.");
            return;
        }

        setLoading(true);
        setError(false);
        setHelperText("");

        try {
            const response = await fetch(`${hostAddress}/ai/generate/channel-names`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt: prompt.trim() }),
            });

            const data = await response.json();

            if (!data.success) {
                setError(true);
                setHelperText(data.message || "Failed to generate channel names.");
                return;
            }

            if (!data.channelNames || data.channelNames.length === 0) {
                setError(true);
                setHelperText("No channel names were generated. Try a different prompt.");
                return;
            }

            // Return the generated channel names
            onClose(data.channelNames);
            setPrompt("");
        } catch (err) {
            setError(true);
            setHelperText("Failed to connect to server. Please try again.");
            notifications.show("Failed to generate channel names", {
                severity: "error",
                autoHideDuration: 3000,
            });
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
                        Please set a default AI provider and model in Settings first.
                    </Alert>
                ) : (
                    <TextField
                        multiline
                        rows={4}
                        variant="outlined"
                        label="Prompt"
                        placeholder="Enter a prompt for AI to generate channel names for you..."
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

export default GenerateChannelNamesDialog;
