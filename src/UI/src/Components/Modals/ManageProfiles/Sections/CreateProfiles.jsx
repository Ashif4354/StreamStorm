import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { Button, TextField, useColorScheme } from '@mui/material';
import { useLocalStorageState } from '@toolpad/core/useLocalStorageState';
import { useNotifications } from '@toolpad/core/useNotifications';
import { RefreshCw } from 'lucide-react';
import { logEvent } from 'firebase/analytics';

import * as atatus from 'atatus-spa';

import "./Sections.css";
import ErrorText from '../../../Elements/ErrorText';
import { analytics } from '../../../../config/firebase';
import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';

const CreateProfiles = () => {

    const { btnProps, inputProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const [hostAddress] = useLocalStorageState("hostAddress");
    const notifications = useNotifications();


    const [profiles, setProfiles] = useState(1);
    const [profilesError, setProfilesError] = useState(false);
    const [profilesHelperText, setProfilesHelperText] = useState("");

    const [errorText, setErrorText] = useState("");
    const [loading, setLoading] = useState(false);

    const handleCreateProfiles = () => {

        setErrorText("");

        if (isNaN(profiles) || profiles < 1) {
            setProfilesError(true);
            setProfilesHelperText("Enter a valid number of profiles");
            return;
        } else {
            setProfilesError(false);
            setProfilesHelperText("");
        }

        setLoading(true);

        const data = {
            count: profiles,
        }
        
        logEvent(analytics, "create_profiles", { count: profiles });

        fetch(`${hostAddress}/environment/profiles/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    setProfiles(1);
                    notifications.show("Profiles created successfully!", {
                        severity: "success",
                    });
                    logEvent(analytics, "create_profiles_success", { count: profiles });
                } else {
                    setErrorText(data.message || "An error occurred while creating profiles.");
                    notifications.show("Failed to create profiles.", {
                        severity: "error",
                    });
                    logEvent(analytics, "create_profiles_failed", { count: profiles });
                }
            })
            .catch((error) => {
                setErrorText("An error occurred while creating profiles. Try again.");
                notifications.show("Failed to create profiles.", {
                    severity: "error",
                });
                atatus.notify(error, {}, ['create_profiles_error']);
                logEvent(analytics, "create_profiles_error", { count: profiles });
            })
            .finally(() => {
                setLoading(false);
            })
    }

    return (
        <div className="create-profiles-container">
            <div className="section-header">
                <UserPlus className="section-logo" size={20} color={"var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Create / Fix Profiles</h3>
            </div>

            <div className="section-content-grid">                

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
                        setProfiles(parseInt(e.target.value));
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
                    startIcon={loading ? <RefreshCw size={20} className="spin" /> : <UserPlus size={20} />}
                    sx={{
                        ...btnProps,
                        marginTop: "1rem",
                    }}
                    onClick={handleCreateProfiles}
                >
                    {
                        loading ? "Creating Profiles..." : "Create Profiles"
                    }
                </Button>

                <ErrorText errorText={errorText} />

            </div>
        </div>
    );
};

export default CreateProfiles;