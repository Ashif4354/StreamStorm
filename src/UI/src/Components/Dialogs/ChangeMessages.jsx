import { useState, useEffect } from "react";
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, InputAdornment, TextField, Tooltip, useColorScheme } from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";

import * as atatus from "../../lib/atatus";
import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";
import GenerateMessagesDialog from "./GenerateMessagesDialog";

const ChangeMessages = ({ payload, open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { formControls } = payload;
    const { colorScheme } = useColorScheme();

    const [messagesString, setMessagesString] = useState("");

    useEffect(() => {
        if (open) {
            atatus.setViewName("/dialog/change-messages");
            atatus.setViewContext({ dialog: "change-messages" });
        }
    }, [open]);

    useEffect(() => {
        setMessagesString(formControls.messagesString);
    }, [formControls.messagesString]);

    const [messages, setMessages] = useState([]);
    const [messagesError, setMessagesError] = useState(false);
    const [messagesHelperText, setMessagesHelperText] = useState("");
    const [aiDialogOpen, setAiDialogOpen] = useState(false);

    const messagesChangeHandler = (e) => {
        const value = e.target.value;
        setMessagesString(value);

        let allMessages = value.split('\n').filter((message) => {
            return message !== '';
        });

        allMessages = allMessages.map((message) => message.trim());

        setMessages(allMessages);
        setMessagesError(false);
        setMessagesHelperText("");
    };

    const onSubmitHandler = () => {
        if (messages.length === 0) {
            setMessagesError(true);
            setMessagesHelperText("Enter at least one message.");
            atatus.addAction("change-messages-validation-failed", { reason: "empty" });
            atatus.validationLogger.warn("Change messages validation failed: empty messages");
            return;
        }

        if (JSON.stringify(messages) === JSON.stringify(formControls.messages)) {
            setMessagesError(true);
            setMessagesHelperText("No changes made to the messages.");
            atatus.addAction("change-messages-validation-failed", { reason: "unchanged" });
            return;
        }

        atatus.addAction("change-messages-submitted", { count: messages.length, messages });
        atatus.stormLogger.info("User submitted updated messages", { count: messages.length, messages });
        onClose(messages);
    };

    const handleAiDialogClose = (generatedMessages) => {
        setAiDialogOpen(false);
        if (generatedMessages && generatedMessages.length > 0) {
            setMessages(generatedMessages);
            setMessagesString(generatedMessages.join('\n'));
            setMessagesError(false);
            setMessagesHelperText("");
            atatus.addAction("ai-messages-applied-in-change-dialog", { count: generatedMessages.length, messages: generatedMessages });
        }
    };

    return (
        <Dialog
            open={open}
            fullWidth
            onClose={() => onClose(null)}
            sx={{
                "& .MuiDialog-paper": {
                    backgroundColor: colorScheme === 'light' ? "var(--light-card-bg)" : "var(--light-gray)",
                    backgroundImage: "none",
                    borderRadius: "var(--border-radius)",
                },
            }}
        >
            <DialogTitle sx={{ display: "flex", flexDirection: "column" }}>
                Change Messages list
                <span style={{ fontSize: "0.875rem", color: "var(--slight-light-text)" }}>
                    Change the existing messages list in ongoing storm.
                </span>
            </DialogTitle>
            <DialogContent>
                <TextField
                    multiline
                    rows={4}
                    variant="outlined"
                    label="Messages"
                    fullWidth
                    value={messagesString}
                    onChange={messagesChangeHandler}
                    error={messagesError}
                    helperText={messagesHelperText}
                    margin="normal"
                    sx={{
                        ...inputProps,
                        '& .MuiInputBase-root': {
                            alignItems: 'flex-start',
                        },
                    }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment
                                position="end"
                                sx={{
                                    alignSelf: 'flex-start',
                                    marginTop: '-8px',
                                    marginRight: '-8px',
                                }}
                            >
                                <Tooltip title="Generate messages with AI">
                                    <IconButton
                                        size="small"
                                        data-atatus-action-name="btn-change-messages-open-ai"
                                        onClick={() => setAiDialogOpen(true)}
                                        sx={{
                                            backgroundColor: 'transparent',
                                            color: colorScheme === 'light' ? 'var(--dark-text)' : 'var(--light-text)',
                                            padding: '4px',
                                            '&:hover': {
                                                backgroundColor: colorScheme === 'light' ? 'rgba(0,0,0,0.04)' : 'rgba(255,255,255,0.08)',
                                            },
                                        }}
                                    >
                                        <AutoAwesomeIcon fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </InputAdornment>
                        ),
                    }}
                />

                <GenerateMessagesDialog
                    open={aiDialogOpen}
                    onClose={handleAiDialogClose}
                />

            </DialogContent>

            <DialogActions>
                <Button
                    variant="outlined"
                    data-atatus-action-name="btn-change-messages-cancel"
                    onClick={() => onClose(false)}
                    sx={{
                        ...btnProps,
                        width: "100px",
                    }}
                >
                    Cancel
                </Button>

                <Button
                    variant="outlined"
                    data-atatus-action-name="btn-change-messages-submit"
                    onClick={onSubmitHandler}
                    sx={{
                        ...btnProps,
                        width: "100px",
                        backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                        '&:hover': {
                            backgroundColor: colorScheme === 'light' ? "var(--light-primary-hover)" : "var(--input-active-red-dark-hover)",
                        },
                    }}
                >
                    Submit
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ChangeMessages;
