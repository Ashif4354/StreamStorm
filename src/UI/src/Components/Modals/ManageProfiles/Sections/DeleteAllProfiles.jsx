import { useState } from 'react';
import { Trash2 } from 'lucide-react';
import { Button, useColorScheme } from '@mui/material';
import { useNotifications } from '@toolpad/core/useNotifications';
import { RefreshCw } from 'lucide-react';
import { useDialogs } from '@toolpad/core/useDialogs';
import { logEvent } from 'firebase/analytics';

import * as atatus from '../../../../lib/atatus';

import "./Sections.css";
import ErrorText from '../../../Elements/ErrorText';
import AreYouSure from '../../../Dialogs/AreYouSure';
import { analytics } from '../../../../config/firebase';
import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../context/AppStateContext';

const DeleteAllProfiles = () => {

    const { colorScheme } = useColorScheme();
    const { btnProps } = useCustomMUIProps();
    const dialogs = useDialogs();

    const { hostAddress } = useAppState();
    const notifications = useNotifications();

    const [errorText, setErrorText] = useState("");
    const [loading, setLoading] = useState(false);

    const handleDeleteAllProfiles = async () => {
        atatus.addAction('delete-all-profiles-dialog-prompted');

        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>Are you sure you want to <strong style={{ color: "var(--input-active-red-dark)" }}>DELETE</strong> all profiles</span>
        });

        if (!confirmed) {
            atatus.addAction('delete-all-profiles-cancelled');
            atatus.envLogger.info('User cancelled delete all profiles');
            return;
        }

        atatus.addAction('delete-all-profiles-confirmed');
        atatus.startOperation('delete_all_profiles');
        atatus.startDurationVital('delete_all_profiles');

        setErrorText("");
        setLoading(true);

        logEvent(analytics, "delete_all_profiles");

        fetch(`${hostAddress}/environment/profiles/delete`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
        })
            .then((response) => response.json())
            .then((data) => {
                atatus.stopDurationVital('delete_all_profiles');
                if (data.success) {
                    atatus.succeedOperation('delete_all_profiles');
                    atatus.envLogger.info('All profiles deleted successfully');
                    atatus.addAction('delete-all-profiles-success');
                    notifications.show("All profiles deleted successfully!", {
                        severity: "success",
                    });
                    logEvent(analytics, "delete_all_profiles_success");
                } else {
                    atatus.failOperation('delete_all_profiles', data.message || 'Failed to delete all profiles');
                    setErrorText(data.message || 'Failed to delete all profiles');
                    notifications.show("Failed to delete all profiles", {
                        severity: 'error',
                    });
                    if (data.error) {
                        console.error('Failed to delete all profiles:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['delete_all_profiles_failed'] });
                        atatus.envLogger.error('Failed to delete all profiles', { response: data });
                    }
                    logEvent(analytics, "delete_all_profiles_failed");
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('delete_all_profiles');
                atatus.failOperation('delete_all_profiles', error.message);
                setErrorText(error.message || "An error occurred while deleting all profiles");
                notifications.show("An error occurred while deleting all profiles", {
                    severity: 'error',
                });
                atatus.addError(error, { tags: ['delete_all_profiles_error'] });
                atatus.envLogger.error('Delete all profiles error', { error: error.message });
                logEvent(analytics, "delete_all_profiles_error");
            })
            .finally(() => {
                setLoading(false);
            });
    };


    return (
        <div className="fix-profiles-container">
            <div className="section-header">
                <Trash2 className="section-logo" size={20} color={colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Delete All Profiles</h3>
            </div>

            <div className="section-content">

            </div>

            <div className="section-action">
                <Button
                    variant="outlined"
                    color="primary"
                    data-atatus-action-name="btn-delete-all-profiles-confirm"
                    sx={{
                        ...btnProps,
                        marginTop: "1rem",
                        backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                        color: "var(--light-text)",
                    }}
                    onClick={handleDeleteAllProfiles}
                    disabled={loading}
                    startIcon={loading ? <RefreshCw size={20} className="spin" /> : <Trash2 size={20} />}
                >
                    {
                        loading ? "Deleting Profiles..." : "Delete All Profiles"
                    }
                </Button>

            </div>
            <ErrorText errorText={errorText} />
        </div>
    );
};

export default DeleteAllProfiles;
