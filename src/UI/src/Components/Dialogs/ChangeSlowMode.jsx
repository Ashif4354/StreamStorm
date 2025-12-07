import { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField } from '@mui/material';
import { useColorScheme } from '@mui/material/styles';
import { useCustomMUIProps } from '../../context/CustomMUIPropsContext';

const ChangeSlowMode = ({ payload, open, onClose }) => {
    const { btnProps, inputProps } = useCustomMUIProps();
    const { formControls } = payload;
    const { colorScheme } = useColorScheme();
    const [slowMode, setSlowMode] = useState(formControls.slowMode);
    const [slowModeError, setSlowModeError] = useState(false);
    const [slowModeHelperText, setSlowModeHelperText] = useState("");

    useEffect(() => {
        setSlowMode(formControls.slowMode);
    }, [formControls.slowMode]);

    const onSubmitHandler = () => {
        const slowModeValue = parseInt(slowMode);

        if (isNaN(slowModeValue) || slowModeValue < 0) {
            setSlowModeError(true);
            setSlowModeHelperText("Enter a valid slow mode time in seconds");
            return;
        }

        onClose(slowModeValue);
    };

    return (
        <Dialog
            open={open}
            onClose={() => onClose(null)}
            sx={{
                "& .MuiDialog-paper": {
                    backgroundColor: colorScheme === 'light' ? "var(--light-card-bg)" : "var(--light-gray)",
                    backgroundImage: "none",
                    borderRadius: "var(--border-radius)",
                },
            }}
        >
            <DialogTitle>
                Change Slow Mode
            </DialogTitle>
            <DialogContent>
                <TextField
                    variant="outlined"
                    label="Slow Mode (seconds)"
                    fullWidth
                    value={slowMode}
                    onChange={(e) => {
                        setSlowMode(e.target.value);
                        setSlowModeError(false);
                        setSlowModeHelperText("");
                    }}
                    error={slowModeError}
                    helperText={slowModeHelperText}
                    sx={{
                        ...inputProps,
                        marginTop: "1rem",
                    }}
                />
            </DialogContent>

            <DialogActions>
                <Button
                    variant="outlined"
                    onClick={() => onClose(null)}
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

export default ChangeSlowMode;