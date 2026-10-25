import { useState } from 'react';
import { useColorScheme } from '@mui/material';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';
import RadioGroup from '@mui/material/RadioGroup';
import Radio from '@mui/material/Radio';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { useNotifications } from '@toolpad/core/useNotifications';
import { Tv, RefreshCw } from 'lucide-react';
import { logEvent } from 'firebase/analytics';

import * as atatus from '../../../../lib/atatus';

import "./Sections.css";
import ErrorText from '../../../Elements/ErrorText';
import GenerateChannelNamesDialog from '../../../Dialogs/GenerateChannelNamesDialog';
import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../context/AppStateContext';
import { analytics } from '../../../../config/firebase';

const CreateChannels = () => {
    const { colorScheme } = useColorScheme();
    const { btnProps, inputProps } = useCustomMUIProps();
    const notifications = useNotifications();
    const appState = useAppState();

    const [logoRequired, setLogoRequired] = useState(false);
    const [logoSelection, setLogoSelection] = useState('random');

    const [channels, setChannels] = useState([]);
    const [channelsString, setChannelsString] = useState('');
    const [channelsError, setChannelsError] = useState(false);
    const [channelsHelperText, setChannelsHelperText] = useState('');

    const [channelsLogoPath, setChannelsLogoPath] = useState('');
    const [channelsLogoPathError, setChannelsLogoPathError] = useState(false);
    const [channelsLogoPathHelperText, setChannelsLogoPathHelperText] = useState('');
    const [validatingPath, setValidatingPath] = useState(false);
    const [creatingChannels, setCreatingChannels] = useState(false);

    const [errorText, setErrorText] = useState("");
    const [validated, setValidated] = useState(false);
    const [totalChannels, setTotalChannels] = useState({});
    const [aiDialogOpen, setAiDialogOpen] = useState(false);

    const channelsChangeHandler = (value) => {
        setErrorText('');
        setChannelsError(false);
        setChannelsHelperText('');
        setChannelsString(value);

        const parsed = value.split('\n').map(channel => channel.trim()).filter(channel => channel !== '');
        setChannels(parsed);
    };

    const handleAiDialogClose = (generatedNames) => {
        setAiDialogOpen(false);
        if (generatedNames && generatedNames.length > 0) {
            setChannels(generatedNames);
            setChannelsString(generatedNames.join('\n'));
            setChannelsError(false);
            setChannelsHelperText('');
            atatus.addAction('ai-channel-names-applied', { count: generatedNames.length });
        }
    };

    const onLogosPathChangeHandler = (value) => {
        setChannelsLogoPath(value);
        setChannelsLogoPathError(false);
        setChannelsLogoPathHelperText('');
    };

    const onValidatePathHandler = () => {
        if (!channelsLogoPath) {
            setChannelsLogoPathError(true);
            setChannelsLogoPathHelperText('Enter a system path');
            atatus.addAction('validate-path-empty');
            return;
        }

        setValidatingPath(true);
        atatus.addAction('validate-path-triggered', { path: channelsLogoPath });
        atatus.startOperation('verify_dir');
        atatus.startDurationVital('verify_dir');

        fetch(`${appState.hostAddress}/environment/channels/verify_dir`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ directory: channelsLogoPath }),
        })
            .then((response) => response.json())
            .then((data) => {
                atatus.stopDurationVital('verify_dir');
                if (data.success) {
                    setValidated(true);
                    setTotalChannels({ count: data.count, files: data.files });
                    setChannelsLogoPathError(false);
                    setChannelsLogoPathHelperText('');

                    atatus.succeedOperation('verify_dir');
                    atatus.envLogger.info('Channel logo directory verified', { count: data.count });
                    atatus.addAction('validate-path-success', { count: data.count });

                    notifications.show('Directory validated', {
                        severity: 'success'
                    });

                    logEvent(analytics, 'validate_path_success');
                } else {
                    setValidated(false);
                    setTotalChannels({});
                    setChannelsLogoPathError(true);
                    setChannelsLogoPathHelperText(data.message);

                    atatus.failOperation('verify_dir', data.message || 'Validation failed');
                    notifications.show(data.message, {
                        severity: 'error'
                    });

                    if (data.error) {
                        console.error('Failed to validate directory:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['validate_path_failed'] });
                        atatus.envLogger.error('Failed to validate directory', { response: data });
                    }
                    logEvent(analytics, 'validate_path_failed');
                }
            })
            .catch((error) => {
                console.error(error);
                atatus.stopDurationVital('verify_dir');
                atatus.failOperation('verify_dir', error.message);
                setValidated(false);
                setTotalChannels({});
                setErrorText("An error occurred while validating the directory. Try again.");

                notifications.show('An error occurred while validating the directory. Try again.', {
                    severity: 'error'
                });

                logEvent(analytics, 'validate_path_error');
                atatus.addError(error, { tags: ['validate_path_error'] });
                atatus.envLogger.error('Verify directory error', { error: error.message });
            })
            .finally(() => {
                setValidatingPath(false);
            });
    };

    const onStartHandler = () => {
        setErrorText('');

        // Check if user is logged in
        if (!appState.isLoggedIn) {
            setErrorText('Not logged in. Log in first.');
            atatus.addAction('create-channels-blocked-not-logged-in');
            atatus.envLogger.warn('Create channels blocked: user not logged in');
            return;
        }

        if (logoRequired && logoSelection === "custom" && !validated) {
            setChannelsLogoPathError(true);
            setChannelsLogoPathHelperText('Enter a system path and click Validate');
            atatus.addAction('create-channels-blocked-unvalidated-path');
            return;
        }

        if ((!logoRequired || logoSelection !== "custom") && channels.length === 0) {
            setChannelsError(true);
            setChannelsHelperText('Enter at least one channel name');
            atatus.addAction('create-channels-blocked-no-names');
            return;
        }

        let finalChannels;

        if (logoSelection === "custom") {
            finalChannels = totalChannels.files;
        } else {
            finalChannels = channels.map((channel) => ({ name: channel, uri: "" }));
        }

        const data = {
            channels: finalChannels,
            randomLogo: logoSelection === "random",
            logoNeeded: logoRequired,
        };

        setCreatingChannels(true);
        atatus.addAction('create-channels-triggered', { count: finalChannels.length, logoRequired, logoSelection });
        atatus.startOperation('create_channels');
        atatus.startDurationVital('create_channels');

        fetch(`${appState.hostAddress}/environment/channels/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                atatus.stopDurationVital('create_channels');
                if (data.success) {
                    atatus.succeedOperation('create_channels');
                    atatus.envLogger.info('Channels created successfully', { count: finalChannels.length });
                    atatus.addAction('create-channels-success', { count: finalChannels.length });
                    notifications.show("Channels created successfully", {
                        severity: 'success'
                    });
                } else {
                    atatus.failOperation('create_channels', data.message || 'Failed to create channels');
                    setErrorText(data.message || 'Failed to create channels');

                    if (data.error) {
                        console.error('Failed to create channels:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['create_channels_failed'] });
                        atatus.envLogger.error('Failed to create channels', { response: data });
                    }
                    logEvent(analytics, 'create_channels_failed');
                    notifications.show(data.message || 'Failed to create channels', {
                        severity: 'error'
                    });
                }
            })
            .catch((error) => {
                console.error(error);
                atatus.stopDurationVital('create_channels');
                atatus.failOperation('create_channels', error.message);
                setErrorText("An error occurred while creating channels. Try again.");

                notifications.show('An error occurred while creating channels. Try again.', {
                    severity: 'error'
                });

                logEvent(analytics, 'create_channels_error');
                atatus.addError(error, { tags: ['create_channels_error'] });
                atatus.envLogger.error('Create channels error', { error: error.message });
            })
            .finally(() => {
                setCreatingChannels(false);
            });
    };

    return (
        <div className={`create-channels-container ${colorScheme}-text`}>
            <div className="section-header">
                <Tv className="section-logo" size={20} color={colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Create Channels</h3>
            </div>
            <div className='create-channels-grid'>
                <div className={`logo-input-container ${logoRequired ? 'logo-required' : ''}`}>
                    <div className={`switch-container logo-switch-container ${colorScheme}-bordered-container`}>
                        <span className={`switch-label-${colorScheme}`}>Logo Required? </span>
                        <Switch
                            checked={logoRequired}
                            disabled={creatingChannels}
                            onChange={(e) => {
                                setLogoRequired(e.target.checked);
                                atatus.addAction('channel-logo-required-toggled', { checked: e.target.checked });
                            }}
                        />
                    </div>
                    {
                        logoRequired && (
                            <div className={`radio-container`}>
                                <RadioGroup
                                    row
                                    defaultValue="basic"
                                    name="channel-index-radio-group"
                                    onChange={(e) => {
                                        setLogoSelection(e.target.value);
                                        atatus.addAction('channel-logo-selection-changed', { selection: e.target.value });
                                    }}
                                    disabled={creatingChannels}
                                >
                                    <div className="logo-radio-container">
                                        <div className="logo-radio">
                                            <Radio
                                                value="random"
                                                checked={logoSelection === "random"}
                                                disabled={creatingChannels}
                                            />
                                            <span className="channel-index-input-label">Random Logo</span>
                                        </div>
                                        <div className="logo-radio">
                                            <Radio
                                                value="custom"
                                                checked={logoSelection === "custom"}
                                                disabled={creatingChannels}
                                            />
                                            <span className="channel-index-input-label">Custom Logo</span>
                                        </div>
                                    </div>
                                </RadioGroup>
                            </div>
                        )
                    }
                </div>

                <div className='channel-data-input-container'>

                    {
                        logoRequired && logoSelection == "custom" ? (
                            <div className="channel-logo-path-container">
                                <span className="experimental-warning">Custom Logo is an experimental feature. It may break sometimes.</span>
                                <TextField
                                    fullWidth
                                    variant="outlined"
                                    label="Channel logos path in PC"
                                    sx={{
                                        ...inputProps,
                                        marginTop: "1rem",
                                        '.MuiInputBase-root.MuiOutlinedInput-root': {
                                            paddingRight: ".4rem",
                                            backgroundColor: colorScheme === 'light' ? "var(--light-surface)" : "var(--dark-gray)",
                                            borderRadius: "var(--border-radius)",
                                        }
                                    }}
                                    value={channelsLogoPath}
                                    onChange={e => onLogosPathChangeHandler(e.target.value)}
                                    error={channelsLogoPathError}
                                    helperText={channelsLogoPathHelperText}
                                    disabled={creatingChannels}
                                    slotProps={{
                                        input: {
                                            endAdornment: (
                                                <InputAdornment position="end">
                                                    <Button
                                                        variant="contained"
                                                        data-atatus-action-name="btn-validate-channels-logo-dir"
                                                        sx={{
                                                            ...btnProps,
                                                            marginTop: "0",
                                                            backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)"
                                                        }}
                                                        disabled={creatingChannels || validatingPath}
                                                        onClick={onValidatePathHandler}
                                                    >
                                                        Validate
                                                    </Button>
                                                </InputAdornment>
                                            )
                                        }
                                    }}
                                />
                                {
                                    Object.keys(totalChannels).length !== 0 && (
                                        <div className="total-channels-container">
                                            <span className="total-channels-data">Total Channels Found: {totalChannels.count}</span>
                                        </div>
                                    )
                                }

                            </div>

                        ) : (
                            <>
                                <TextField
                                    multiline
                                    fullWidth
                                    rows={4}
                                    variant="outlined"
                                    label="Channel names"
                                    sx={{
                                        ...inputProps,
                                        marginTop: "1rem",
                                        '& .MuiInputBase-root': {
                                            alignItems: 'flex-start',
                                        },
                                    }}
                                    value={channelsString}
                                    onChange={e => channelsChangeHandler(e.target.value)}
                                    error={channelsError}
                                    helperText={channelsHelperText}
                                    disabled={creatingChannels}
                                    InputProps={{
                                        endAdornment: (
                                            <InputAdornment
                                                position="end"
                                                sx={{
                                                    alignSelf: 'flex-start',
                                                    marginTop: '-8px',
                                                    marginRight: '-8px',
                                                }}
                                            >
                                                <Tooltip title="Generate channel names with AI">
                                                    <IconButton
                                                        size="small"
                                                        data-atatus-action-name="btn-open-ai-channel-names-dialog"
                                                        onClick={() => setAiDialogOpen(true)}
                                                        disabled={creatingChannels}
                                                        sx={{
                                                            backgroundColor: 'transparent',
                                                            color: colorScheme === 'light' ? 'var(--dark-text)' : 'var(--light-text)',
                                                            padding: '4px',
                                                            '&:hover': {
                                                                backgroundColor: colorScheme === 'light' ? 'rgba(0,0,0,0.04)' : 'rgba(255,255,255,0.08)',
                                                            },
                                                        }}
                                                    >
                                                        <AutoAwesomeIcon fontSize="small" />
                                                    </IconButton>
                                                </Tooltip>
                                            </InputAdornment>
                                        ),
                                    }}
                                />
                                <GenerateChannelNamesDialog
                                    open={aiDialogOpen}
                                    onClose={handleAiDialogClose}
                                />
                            </>
                        )
                    }
                </div>
            </div>

            <Button
                variant="contained"
                data-atatus-action-name="btn-create-channels-submit"
                sx={{
                    ...btnProps,
                    marginTop: "1rem",
                }}
                disabled={creatingChannels}
                startIcon={creatingChannels ? <RefreshCw size={20} className="spin" /> : null}
                onClick={onStartHandler}
            >
                {
                    creatingChannels ? "Creating Channels..." : "Create Channels"
                }
            </Button>
            <ErrorText errorText={errorText} />
        </div>
    );
};

export default CreateChannels;
