import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Box, Button, CircularProgress, Alert } from '@mui/material';
import { Cookie, UserCircle, Save, Trash2 } from 'lucide-react';
import { useDialogs } from '@toolpad/core/useDialogs';

import { useAppState } from '../../../../../context/AppStateContext';
import RadioSetting from './RadioSetting';
import ButtonSetting from './ButtonSetting';
import AreYouSure from '../../../../Dialogs/AreYouSure';

const GeneralSettings = () => {
    const { colorScheme } = useColorScheme();
    const { hostAddress, loginMethod, setLoginMethod, setIsLoggedIn, settingsLoading } = useAppState();
    const dialogs = useDialogs();

    const [localLoginMethod, setLocalLoginMethod] = useState(loginMethod);
    const [saving, setSaving] = useState(false);
    const [clearing, setClearing] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Sync local state with app state when app state is loaded
    useEffect(() => {
        setLocalLoginMethod(loginMethod);
    }, [loginMethod]);

    const hasChanges = localLoginMethod !== loginMethod;

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch(`${hostAddress}/settings/general`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ login_method: localLoginMethod }),
            });
            const data = await response.json();

            if (data.success) {
                setLoginMethod(localLoginMethod); // Update app state
                setSuccess('Settings saved successfully');
                setTimeout(() => setSuccess(null), 3000);
            } else {
                setError(data.message || 'Failed to save settings');
            }
        } catch (err) {
            setError('Failed to save settings');
        } finally {
            setSaving(false);
        }
    };

    const handleClearLoginData = async () => {
        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>Are you sure you want to <strong style={{ color: "var(--input-active-red-dark)" }}>DELETE</strong> all login data? This includes saved cookies, browser profiles, and channel data. You will need to log in again.</span>
        });

        if (!confirmed) {
            return;
        }

        setClearing(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch(`${hostAddress}/settings/general/clear-login-data`, {
                method: 'DELETE',
            });
            const data = await response.json();

            if (data.success) {
                setIsLoggedIn(false);
                setSuccess(data.message || 'All login data cleared successfully');
                setTimeout(() => setSuccess(null), 5000);
            } else {
                setError(data.message || 'Failed to clear login data');
            }
        } catch (err) {
            setError('Failed to clear login data');
        } finally {
            setClearing(false);
        }
    };

    const loginMethodOptions = [
        {
            value: 'cookies',
            icon: <Cookie size={18} color={colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)'} />,
            label: 'Cookies',
            description: 'Faster startup, lower disk usage. Recommended for most users.',
        },
        {
            value: 'profiles',
            icon: <UserCircle size={18} color={colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)'} />,
            label: 'Browser Profiles',
            description: 'Persistent sessions, uses more disk space. Better for long-term use.',
        },
    ];

    return (
        <div className="settings-section" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <h3 className={`settings-section-title ${colorScheme}-text`}>General</h3>
            <p className={`settings-section-description settings-section-description-${colorScheme}`}>
                General application settings.
            </p>

            {settingsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress size={32} />
                </Box>
            ) : (
                <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
                    {/* Login Method Setting */}
                    <RadioSetting
                        title="Login Method"
                        description="Choose how StreamStorm authenticates with YouTube. Changes require re-login."
                        value={localLoginMethod}
                        onChange={(e) => setLocalLoginMethod(e.target.value)}
                        options={loginMethodOptions}
                    />

                    {/* Clear Login Data Button */}
                    <ButtonSetting
                        title="Clear Login Data"
                        description="Remove all saved cookies, browser profiles, and channel data. You will need to log in again."
                        buttonText={clearing ? 'Clearing...' : 'Clear All Data'}
                        onClick={handleClearLoginData}
                        startIcon={<Trash2 size={16} />}
                        loading={clearing}
                        disabled={clearing}
                        variant="outlined"
                    />

                    {/* Status Messages */}
                    {
                        error && (
                            <Alert severity="error" sx={{ borderRadius: 'var(--border-radius)' }}>
                                {error}
                            </Alert>
                        )
                    }
                    {
                        success && (
                            <Alert severity="success" sx={{ borderRadius: 'var(--border-radius)' }}>
                                {success}
                            </Alert>
                        )
                    }
                </Box>
            )}

            {/* Fixed Save Button at Bottom */}
            {
                !settingsLoading && (
                    <Box sx={{
                        position: 'sticky',
                        bottom: 0,
                        pt: 2,
                        pb: 1,
                        backgroundColor: colorScheme === 'dark' ? 'var(--light-gray)' : 'var(--light-card-bg)',
                        display: 'flex',
                        justifyContent: 'flex-end',
                        // borderTop: `1px solid ${colorScheme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                        marginTop: 'auto',
                    }}>
                        <Button
                            variant="contained"
                            disabled={!hasChanges || saving}
                            onClick={handleSave}
                            startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <Save size={16} />}
                            sx={{
                                backgroundColor: colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)',
                                '&:hover': {
                                    backgroundColor: colorScheme === 'dark' ? 'var(--bright-red-2-hover)' : 'var(--dark-red-2-hover)',
                                },
                                '&.Mui-disabled': {
                                    backgroundColor: colorScheme === 'dark' ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)',
                                },
                                textTransform: 'none',
                                borderRadius: 'var(--border-radius)',
                            }}
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </Box>
                )
            }
        </div>
    );
};

export default GeneralSettings;
