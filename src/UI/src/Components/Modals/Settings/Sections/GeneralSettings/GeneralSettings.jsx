import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Box, Button, CircularProgress, Alert } from '@mui/material';
import { Cookie, UserCircle, Save, Trash2, Zap, Globe } from 'lucide-react';
import { useDialogs } from '@toolpad/core/useDialogs';

import { useAppState } from '../../../../../context/AppStateContext';
import RadioSetting from './RadioSetting';
import ButtonSetting from './ButtonSetting';
import AreYouSure from '../../../../Dialogs/AreYouSure';

import * as atatus from '../../../../../lib/atatus';

const GeneralSettings = () => {
    const { colorScheme } = useColorScheme();
    const { hostAddress, loginMethod, setLoginMethod, engine, setEngine, setIsLoggedIn, settingsLoading } = useAppState();
    const dialogs = useDialogs();

    const [localLoginMethod, setLocalLoginMethod] = useState(loginMethod);
    const [localEngine, setLocalEngine] = useState(engine || 'obscura');
    const [saving, setSaving] = useState(false);
    const [clearing, setClearing] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Sync local state with app state when app state is loaded
    useEffect(() => {
        setLocalLoginMethod(loginMethod);
    }, [loginMethod]);

    useEffect(() => {
        setLocalEngine(engine || 'obscura');
    }, [engine]);

    const hasChanges = localLoginMethod !== loginMethod || localEngine !== engine;

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        setSuccess(null);

        atatus.addAction('save-general-settings-triggered', { loginMethod: localLoginMethod, engine: localEngine });
        atatus.startOperation('save_general_settings');
        atatus.startDurationVital('save_general_settings');

        try {
            const response = await fetch(`${hostAddress}/settings/general`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    login_method: localLoginMethod,
                    engine: localEngine,
                }),
            });
            const data = await response.json();
            atatus.stopDurationVital('save_general_settings');

            if (data.success) {
                atatus.succeedOperation('save_general_settings');
                atatus.settingsLogger.info('General settings saved', { login_method: localLoginMethod, engine: localEngine });
                atatus.addFeatureFlagEvaluation('login_method', localLoginMethod);
                atatus.addFeatureFlagEvaluation('engine', localEngine);
                atatus.setGlobalContextProperty('loginMethod', localLoginMethod);
                atatus.setGlobalContextProperty('engine', localEngine);

                setLoginMethod(localLoginMethod); // Update app state
                setEngine(localEngine);
                setSuccess('Settings saved successfully');
                setTimeout(() => setSuccess(null), 3000);
            } else {
                atatus.failOperation('save_general_settings', data.message || 'Failed to save settings');
                setError(data.message || 'Failed to save settings');
                if (data.error) {
                    console.error('Failed to save settings:', data.error);
                    atatus.addError(new Error(data.error), { response: data, tags: ['general_settings_save_failed'] });
                    atatus.settingsLogger.error('Failed to save general settings', { response: data });
                }
            }
        } catch (err) {
            console.error('Failed to save settings:', err);
            atatus.stopDurationVital('save_general_settings');
            atatus.failOperation('save_general_settings', err.message);
            atatus.addError(err, { tags: ['general_settings_save_error'] });
            atatus.settingsLogger.error('Failed to save general settings', { error: err.message });
            setError('Failed to save settings');
        } finally {
            setSaving(false);
        }
    };

    const handleClearLoginData = async () => {
        atatus.addAction('clear-login-data-dialog-prompted');

        const confirmed = await dialogs.open(AreYouSure, {
            text: <span>Are you sure you want to <strong style={{ color: "var(--input-active-red-dark)" }}>DELETE</strong> all login data? This includes saved cookies, browser profiles, and channel data. You will need to log in again.</span>
        });

        if (!confirmed) {
            atatus.addAction('clear-login-data-cancelled');
            return;
        }

        atatus.addAction('clear-login-data-confirmed');
        setClearing(true);
        setError(null);
        setSuccess(null);
        atatus.startOperation('clear_login_data');
        atatus.startDurationVital('clear_login_data');

        try {
            const response = await fetch(`${hostAddress}/settings/general/clear-login-data`, {
                method: 'DELETE',
            });
            const data = await response.json();
            atatus.stopDurationVital('clear_login_data');

            if (data.success) {
                atatus.succeedOperation('clear_login_data');
                atatus.settingsLogger.info('Login data cleared successfully');
                atatus.clearUser();
                atatus.addFeatureFlagEvaluation('is_logged_in', false);
                atatus.setGlobalContextProperty('isLoggedIn', false);

                setIsLoggedIn(false);
                setSuccess(data.message || 'All login data cleared successfully');
                setTimeout(() => setSuccess(null), 5000);
            } else {
                atatus.failOperation('clear_login_data', data.message || 'Failed to clear login data');
                setError(data.message || 'Failed to clear login data');
                if (data.error) {
                    console.error('Failed to clear login data:', data.error);
                    atatus.addError(new Error(data.error), { response: data, tags: ['clear_login_data_failed'] });
                    atatus.settingsLogger.error('Failed to clear login data', { response: data });
                }
            }
        } catch (err) {
            console.error('Failed to clear login data:', err);
            atatus.stopDurationVital('clear_login_data');
            atatus.failOperation('clear_login_data', err.message);
            atatus.addError(err, { tags: ['clear_login_data_error'] });
            atatus.settingsLogger.error('Failed to clear login data', { error: err.message });
            setError('Failed to clear login data');
        } finally {
            setClearing(false);
        }
    };

    const engineOptions = [
        {
            value: 'obscura',
            icon: <Zap size={18} color={colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)'} />,
            label: 'Obscura',
            description: 'Ultra-lightweight headless engine (~150MB RAM/account). Highly recommended for lower resource usage.',
        },
        {
            value: 'chromium',
            icon: <Globe size={18} color={colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)'} />,
            label: 'Chromium',
            description: 'Standard Chromium browser (~350MB RAM/account). Full browser engine, required when using Browser Profiles.',
        },
    ];

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
                    {/* Engine Setting */}
                    <RadioSetting
                        title="Engine"
                        description="Choose the browser automation engine used to run sessions. Obscura uses significantly less memory."
                        value={localEngine}
                        onChange={(e) => {
                            setLocalEngine(e.target.value);
                            atatus.addAction('engine-selected', { engine: e.target.value });
                        }}
                        options={engineOptions}
                    />

                    {/* Login Method Setting */}
                    <RadioSetting
                        title="Login Method"
                        description="Choose how StreamStorm authenticates with YouTube. Changes require re-login."
                        value={localLoginMethod}
                        onChange={(e) => {
                            setLocalLoginMethod(e.target.value);
                            atatus.addAction('login-method-selected', { method: e.target.value });
                        }}
                        options={loginMethodOptions}
                    />

                    {localLoginMethod === 'profiles' && localEngine === 'obscura' && (
                        <Alert severity="info" sx={{ borderRadius: 'var(--border-radius)' }}>
                            Note: Obscura currently supports the Cookies login method. Browser Profiles will use Chromium.
                        </Alert>
                    )}

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
                        marginTop: 'auto',
                    }}>
                        <Button
                            variant="contained"
                            disabled={!hasChanges || saving}
                            onClick={handleSave}
                            data-atatus-action-name="btn-save-general-settings"
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
