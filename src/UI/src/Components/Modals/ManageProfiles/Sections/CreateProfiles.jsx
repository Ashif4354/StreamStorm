import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { Button, TextField, useColorScheme } from '@mui/material';
import { useNotifications } from '@toolpad/core/useNotifications';
import { RefreshCw } from 'lucide-react';
import { safeLogEvent as logEvent } from '../../../../config/safeAnalytics.js';

import * as atatus from '../../../../lib/atatus';

import "./Sections.css";
import ErrorText from '../../../Elements/ErrorText';
import { analytics } from '../../../../config/firebase';
import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../context/AppStateContext';

const CreateProfiles = () => {

    const { btnProps, inputProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const { hostAddress } = useAppState();
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
            atatus.addAction('create-profiles-validation-failed', { profiles });
            atatus.envLogger.warn('Create profiles validation failed: invalid profile count', { profiles });
            return;
        } else {
            setProfilesError(false);
            setProfilesHelperText("");
        }

        setLoading(true);
        atatus.addAction('create-profiles-triggered', { count: profiles });
        atatus.startOperation('create_profiles');
        atatus.startDurationVital('create_profiles');

        const data = {
            count: profiles,
            cookiesLogin: false
        };

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
                atatus.stopDurationVital('create_profiles');
                if (data.success) {
                    atatus.succeedOperation('create_profiles');
                    atatus.envLogger.info('Profiles created successfully', { count: profiles });
                    atatus.addAction('create-profiles-success', { count: profiles });
                    setProfiles(1);
                    notifications.show("Profiles created successfully!", {
                        severity: "success",
                    });
                    logEvent(analytics, "create_profiles_success", { count: profiles });
                } else {
                    atatus.failOperation('create_profiles', data.message || 'An error occurred while creating profiles.');
                    setErrorText(data.message || 'An error occurred while creating profiles.');
                    notifications.show("Failed to create profiles.", {
                        severity: "error",
                    });
                    if (data.error) {
                        console.error('Failed to create profiles:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['create_profiles_failed'] });
                        atatus.envLogger.error('Failed to create profiles', { response: data });
                    }
                    logEvent(analytics, "create_profiles_failed", { count: profiles });
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('create_profiles');
                atatus.failOperation('create_profiles', error.message);
                setErrorText("An error occurred while creating profiles. Try again.");
                notifications.show("Failed to create profiles.", {
                    severity: "error",
                });
                atatus.addError(error, { tags: ['create_profiles_error'] });
                atatus.envLogger.error('Create profiles error', { error: error.message });
                logEvent(analytics, "create_profiles_error", { count: profiles });
            })
            .finally(() => {
                setLoading(false);
            });
    };

    return (
        <div className="create-profiles-container">
            <div className="section-header">
                <UserPlus className="section-logo" size={20} color={colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)"} />
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
                        const val = parseInt(e.target.value);
                        setProfiles(val);
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
                    className="create-profiles-button"
                    disabled={loading}
                    data-atatus-action-name="btn-create-profiles-submit"
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
