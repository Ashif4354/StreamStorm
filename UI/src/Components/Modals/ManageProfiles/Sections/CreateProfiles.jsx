import { useContext, useState } from 'react';
import { UserPlus } from 'lucide-react';
import { Button, MenuItem, TextField, useColorScheme } from '@mui/material';
import { useLocalStorageState } from '@toolpad/core/useLocalStorageState';
import { useNotifications } from '@toolpad/core/useNotifications';
import { RefreshCw } from 'lucide-react';

import "./Sections.css";
import { BROWSERS } from '../../../../lib/Constants';
import { CustomMUIPropsContext } from '../../../../lib/ContextAPI';
import ErrorText from '../../../Elements/ErrorText';

const CreateProfiles = ({ currentBrowser }) => {

    const { btnProps, inputProps } = useContext(CustomMUIPropsContext);
    const { colorScheme } = useColorScheme();
    const [hostAddress] = useLocalStorageState("hostAddress");
    const notifications = useNotifications();

    const [browser, setBrowser] = useState("");
    const [browserError, setBrowserError] = useState(false);
    const [browserHelperText, setBrowserHelperText] = useState("");

    const [profiles, setProfiles] = useState(1);
    const [profilesError, setProfilesError] = useState(false);
    const [profilesHelperText, setProfilesHelperText] = useState("");

    const [errorText, setErrorText] = useState("");
    const [loading, setLoading] = useState(false);



    const handleCreateProfiles = () => {

        setErrorText("");


        if (!browser) {
            setBrowserError(true);
            setBrowserHelperText("Select a browser");
            return;
        } else {
            setBrowserError(false);
            setBrowserHelperText("");
        }


        if (profiles < 1) {
            setProfilesError(true);
            setProfilesHelperText("Enter a valid number of profiles");
            return;
        } else {
            setProfilesError(false);
            setProfilesHelperText("");
        }

        // setBrowserDisabled(true);
        // setProfilesDisabled(true);
        setLoading(true);

        const data = {
            browser: browser.toLowerCase(),
            limit: profiles,
        }

        fetch(`${hostAddress}/create_profiles`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    setBrowser("");
                    setProfiles(1);
                    notifications.show("Profiles created successfully!", {
                        severity: "success",
                    });
                } else {
                    setErrorText(data.message || "An error occurred while creating profiles.");
                    notifications.show("Failed to create profiles.", {
                        severity: "error",
                    });
                }
            })
            .catch((error) => {
                console.error("Error creating profiles:", error);
                setErrorText("An error occurred while creating profiles. Try again.");
                notifications.show("Failed to create profiles.", {
                    severity: "error",
                });
            })
            .finally(() => {
                // setBrowserDisabled(false);
                // setProfilesDisabled(false);
                setLoading(false);
            })
    }

    return (
        <div className="create-profiles-container">
            <div className="section-header">
                <UserPlus className="section-logo" size={20} color={"var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Create Profiles</h3>
            </div>

            <div className="section-content-grid">
                <TextField
                    fullWidth
                    select
                    disabled={loading}
                    label="Browser"
                    variant="outlined"
                    sx={{
                        ...inputProps,
                        marginTop: "1rem",
                    }}
                    value={browser}
                    onChange={(e) => {
                        setBrowser(e.target.value);
                        setBrowserError(false);
                        setBrowserHelperText("");
                        setErrorText("");
                    }}
                    error={browserError}
                    helperText={browserHelperText}
                >
                    {
                        BROWSERS.map((browser) => {
                            let browserText = browser.toLowerCase();
                            return (
                                <MenuItem key={browser} value={browserText} disabled={browserText === currentBrowser}>
                                    {browser} {browserText === currentBrowser ? "(Current browser)" : ""}
                                </MenuItem>
                            )
                        })
                    }
                </TextField>

                <TextField
                    fullWidth
                    disabled={loading}
                    type="number"
                    label="No. of profiles"
                    variant="outlined"
                    sx={{
                        ...inputProps,
                        marginTop: "1rem",
                    }}
                    value={profiles}
                    onChange={(e) => {
                        setProfiles(Math.trunc(e.target.value));
                        setProfilesError(false);
                        setProfilesHelperText("");
                        setErrorText("");
                    }}
                    error={profilesError}
                    helperText={profilesHelperText}
                />
            </div>

            <div className="section-action">
                <Button
                    variant="contained"
                    color="primary"
                    className={`create-profiles-button`}
                    disabled={loading}
                    sx={{
                        ...btnProps,
                        marginTop: "1rem",
                    }}
                    onClick={handleCreateProfiles}
                >
                    {
                        loading ? (
                            <>
                                <RefreshCw size={20} className="spin" /> 
                                &nbsp;&nbsp;Creating Profiles...
                            </>
                        ) : "Create Profiles"
                    }
                </Button>

                <ErrorText errorText={errorText} />

            </div>
        </div>
    );
};

export default CreateProfiles;