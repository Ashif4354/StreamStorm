import { useState, useEffect } from "react";
import { Button, TextField } from "@mui/material";
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { useColorScheme } from '@mui/material/styles';
import { Save, RotateCcw } from 'lucide-react';
import { useNotifications } from "@toolpad/core/useNotifications";
import { logEvent } from "firebase/analytics";

import { DEFAULT_HOST_ADDRESS } from "../../../../lib/Constants";
import { analytics } from "../../../../config/firebase";
import { useCustomMUIProps } from "../../../../context/CustomMUIPropsContext";

const isValidURL = (url) => {
    if (!url || url.trim() === "") return false;

    try {
        new URL(url);
        return true;
    } catch (error) {
        return false;
    }
};

const HostSettings = () => {
    const { colorScheme } = useColorScheme();
    const { btnProps, inputProps } = useCustomMUIProps();
    const [savedHostAddress, setSavedHostAddress] = useLocalStorageState("hostAddress");
    const notifications = useNotifications();

    const [hostAddress, setHostAddress] = useState("");
    const [hostAddressError, setHostAddressError] = useState(false);
    const [hostAddressHelperText, setHostAddressHelperText] = useState("");

    const handleSave = () => {
        const trimmed = hostAddress.trim();

        if (trimmed === "") {
            setHostAddressError(true);
            setHostAddressHelperText("Host address cannot be empty.");
            return;
        }

        if (!isValidURL(trimmed)) {
            setHostAddressError(true);
            setHostAddressHelperText("Invalid URL format, Enter a valid URL.");
            return;
        }

        logEvent(analytics, "host_address_change");

        setHostAddressError(false);
        setHostAddressHelperText("");
        setSavedHostAddress(trimmed);

        notifications.show("Host address saved successfully!", {
            severity: "success",
        });
    }

    const handleReset = () => {
        setHostAddress(DEFAULT_HOST_ADDRESS);
        setSavedHostAddress(DEFAULT_HOST_ADDRESS);

        setHostAddressError(false);
        setHostAddressHelperText("");

        logEvent(analytics, "host_address_reset");

        notifications.show("Host address reset to default!", {
            severity: "info",
        });
    }

    useEffect(() => {
        if (!savedHostAddress || !isValidURL(savedHostAddress)) {
            setSavedHostAddress(DEFAULT_HOST_ADDRESS);
            setHostAddress(DEFAULT_HOST_ADDRESS);
        } else {
            setHostAddress(savedHostAddress);
        }
    }, [savedHostAddress, setSavedHostAddress]);

    return (
        <div className="settings-section">
            <h3 className={`settings-section-title ${colorScheme}-text`}>Host Configuration</h3>
            <p className={`settings-section-description settings-section-description-${colorScheme}`}>
                Set the base URL of the StreamStorm backend server.
            </p>

            <div className="settings-section-content">
                <TextField
                    fullWidth
                    variant="outlined"
                    label="Host Address"
                    placeholder="Enter base URL"
                    sx={inputProps}
                    value={hostAddress}
                    error={hostAddressError}
                    helperText={hostAddressHelperText}
                    onChange={(e) => {
                        setHostAddress(e.target.value)
                        setHostAddressError(false);
                        setHostAddressHelperText("");
                    }}
                />

                <div className="settings-button-group">
                    <Button
                        startIcon={<RotateCcw size={16} />}
                        variant="contained"
                        onClick={handleReset}
                        sx={btnProps}
                    >
                        Reset
                    </Button>

                    <Button
                        variant="contained"
                        startIcon={<Save size={16} />}
                        onClick={handleSave}
                        sx={{
                            ...btnProps,
                            backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                            color: "var(--light-text)",
                        }}
                    >
                        Save
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default HostSettings;
