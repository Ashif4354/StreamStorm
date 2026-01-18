import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, useColorScheme } from "@mui/material";
import { useCustomMUIProps } from "../../context/CustomMUIPropsContext";

const AreYouSure = ({ payload, open, onClose }) => {
    const { btnProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();

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
            <DialogTitle>
                Confirm
            </DialogTitle>
            <DialogContent>
                <DialogContentText>
                    {payload.text}
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button
                    variant="outlined"
                    onClick={() => onClose(false)}
                    color="primary"
                    sx={{
                        ...btnProps,
                        width: "100px",
                    }}
                >
                    Cancel
                </Button>

                <Button
                    variant="outlined"
                    onClick={() => onClose(true)}
                    color="error"
                    sx={{
                        ...btnProps,
                        width: "100px",
                        backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                        '&:hover': {
                            backgroundColor: colorScheme === 'light' ? "var(--light-primary-hover)" : "var(--input-active-red-dark-hover)",
                        },
                    }}
                >
                    Confirm
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default AreYouSure;
