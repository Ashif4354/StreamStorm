import { useState, useEffect } from "react";
import { Button, Card, CardActions, CardContent, CardHeader, TextField } from "@mui/material";
import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { useColorScheme } from '@mui/material/styles';
import { Save, RotateCcw } from 'lucide-react';
import { useNotifications } from "@toolpad/core/useNotifications";
import { logEvent } from "firebase/analytics";

import "./HostConfig.css";
import { DEFAULT_HOST_ADDRESS } from "../../../lib/Constants";
import { analytics } from "../../../config/firebase";
import { useCustomMUIProps } from "../../../context/CustomMUIPropsContext";

const isValidURL = (url) => {
  if (!url || url.trim() === "") return false;

  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
};

const HostConfig = () => {
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
        <Card
            className={`host-config-card ${colorScheme}-bordered-container`}
            sx={{
                borderRadius: "var(--border-radius)",
                backgroundColor: colorScheme === 'light' ? "var(--white)" : "var(--light-gray)",
                backgroundImage: "none",
                color: colorScheme === 'light' ? "var(--dark-text)" : "var(--light-text)",
            }}
        >
            <div className="card-header-container">
                <CardHeader
                    avatar={<Save />}
                    title="Host Configuration"
                    className={`card-header card-header-${colorScheme}`}
                    sx={{
                        padding: 0,
                    }}
                />
                <span className={`card-header-description card-header-description-${colorScheme}`}>
                    Set the base URL of the host.
                </span>
            </div>

            <CardContent
                sx={{
                    padding: 0,
                }}
            >
                <div className="host-config-container">
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
                </div>
            </CardContent>

            <CardActions
                sx={{
                    "padding": "0 1.5rem 1.5rem 1.5rem",
                }}>
                <Button
                    startIcon={<RotateCcw size={16} />}
                    variant="contained"
                    onClick={handleReset}
                    sx={{
                        ...btnProps,
                        marginTop: "1rem",
                    }}
                >
                    Reset
                </Button>

                <Button
                    variant="contained"
                    startIcon={<Save size={16} />}
                    onClick={handleSave}
                    sx={{
                        ...btnProps,
                        marginTop: "1rem",
                        backgroundColor: colorScheme === 'light' ? "var(--input-active-red-light)" : "var(--input-active-red-dark)",
                        color: "var(--light-text)",
                    }}
                >
                    Save
                </Button>
            </CardActions>
        </Card>
    );
};

export default HostConfig;
