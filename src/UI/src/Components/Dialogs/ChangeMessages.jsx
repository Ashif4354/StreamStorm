import { useState, useEffect } from "react";
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField, useColorScheme } from "@mui/material";

import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";

const ChangeMessages = ({ payload, open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { formControls } = payload;
    const { colorScheme } = useColorScheme();

    const [messagesString, setMessagesString] = useState("");

    useEffect(() => {
        setMessagesString(formControls.messagesString);
    }, [formControls.messagesString]);

    const [messages, setMessages] = useState([]);
    const [messagesError, setMessagesError] = useState(false);
    const [messagesHelperText, setMessagesHelperText] = useState("");

    const messagesChangeHandler = (e) => {
        // sourcery skip: use-object-destructuring
        const value = e.target.value;
        setMessagesString(value);

        let allMessages = value.split('\n').filter((message) => {
            return message !== '';
        });

        allMessages = allMessages.map((message) => message.trim())

        setMessages(allMessages);
        setMessagesError(false);
        setMessagesHelperText("");
    }

    const onSubmitHandler = () => {
        if (messages.length === 0) {
            setMessagesError(true);
            setMessagesHelperText("Enter at least one message.");
            return;
        }

        if (JSON.stringify(messages) === JSON.stringify(formControls.messages)) {
            setMessagesError(true);
            setMessagesHelperText("No changes made to the messages.");
            return;
        }

        onClose(messages);
    }

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
                    sx={inputProps}
                />

            </DialogContent>

            <DialogActions>
                <Button
                    variant="outlined"
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
    )
}

export default ChangeMessages;