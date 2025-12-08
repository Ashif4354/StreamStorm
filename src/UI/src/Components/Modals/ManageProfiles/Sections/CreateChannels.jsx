
import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';
import RadioGroup from '@mui/material/RadioGroup';
import Radio from '@mui/material/Radio';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import { useNotifications } from '@toolpad/core/useNotifications';
import { Tv, RefreshCw } from 'lucide-react';
import { logEvent } from 'firebase/analytics';

import * as atatus from 'atatus-spa';

import "./Sections.css";
import ErrorText from '../../../Elements/ErrorText';
import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';
import { useStormData } from '../../../../context/StormDataContext';
import { analytics } from '../../../../config/firebase';

const CreateChannels = () => {
    const { colorScheme } = useColorScheme();
    const { btnProps, inputProps } = useCustomMUIProps();
    const formControls = useStormData();
    const notifications = useNotifications();

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

    const channelsChangeHandler = (value) => {
        setErrorText('');
        setChannelsError(false);
        setChannelsHelperText('');
        setChannelsString(value);

        const channels = value.split('\n').map(channel => channel.trim()).filter(channel => channel !== '');
        setChannels(channels);
    };

    const onLogosPathChangeHandler = (value) => {
        setChannelsLogoPath(value);
        setChannelsLogoPathError(false);
        setChannelsLogoPathHelperText('');
    }

    const onValidatePathHandler = () => {
        if (!channelsLogoPath) {
            setChannelsLogoPathError(true);
            setChannelsLogoPathHelperText('Enter a system path');
            return;
        }

        setValidatingPath(true);

        fetch(`${formControls.hostAddress}/environment/channels/verify_dir`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ directory: channelsLogoPath }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    setValidated(true);
                    setTotalChannels({ count: data.count, files: data.files });
                    setChannelsLogoPathError(false);
                    setChannelsLogoPathHelperText('');

                    notifications.show('Directory validated', {
                        severity: 'success'
                    });

                    logEvent(analytics, 'validate_path_success');
                } else {
                    setValidated(false);
                    setTotalChannels({});
                    setChannelsLogoPathError(true);
                    setChannelsLogoPathHelperText(data.message);

                    notifications.show(data.message, {
                        severity: 'error'
                    });

                    logEvent(analytics, 'validate_path_failed');
                    atatus.notify()
                }
            })
            .catch((error) => {
                console.error(error);
                setValidated(false);
                setTotalChannels({});
                setErrorText("An error occurred while validating the directory. Try again.");

                notifications.show('An error occurred while validating the directory. Try again.', {
                    severity: 'error'
                });

                logEvent(analytics, 'validate_path_error');
                atatus.notify(error)
            })
            .finally(() => {
                setValidatingPath(false);
            });
    }

    const onStartHandler = () => {
        setErrorText('');

        if (logoRequired && logoSelection === "custom" && !validated) {
            setChannelsLogoPathError(true);
            setChannelsLogoPathHelperText('Enter a system path and click Validate');
            console.log("a")
            return;
        }

        if ((!logoRequired || logoSelection !== "custom") && channels.length === 0) {
            setChannelsError(true);
            setChannelsHelperText('Enter at least one channel name');
            return;
        }

        let finalChannels;

        if (logoSelection === "custom") {
            finalChannels = totalChannels.files
        } else {
            finalChannels = channels.map((channel) => ({ name: channel, uri: "" }))
        }

        const data = {
            channels: finalChannels,
            randomLogo: logoSelection === "random",
            logoNeeded: logoRequired,
        };

        setCreatingChannels(true);

        fetch(`${formControls.hostAddress}/environment/channels/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    notifications.show("Channels created successfully", {
                        severity: 'success'
                    });
                } else {
                    setErrorText(data.message);
                    
                    logEvent(analytics, 'create_channels_failed');
                    notifications.show(data.message, {
                        severity: 'error'
                    });
                }
            })
            .catch((error) => {
                console.error(error);
                setErrorText("An error occurred while creating channels. Try again.");

                notifications.show('An error occurred while creating channels. Try again.', {
                    severity: 'error'
                });

                logEvent(analytics, 'create_channels_error');
                atatus.notify(error)
            })
            .finally(() => {
                setCreatingChannels(false);
            })
    };

    return (
        <div className={`create-channels-container ${colorScheme}-text`}>
            <div className="section-header">
                <Tv className="section-logo" size={20} color={"var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Create Channels</h3>
            </div>
            <div className='create-channels-grid'>
                <div className={`logo-input-container ${logoRequired ? 'logo-required' : ''}`}>
                    <div className={`switch-container logo-switch-container ${colorScheme}-bordered-container`}>
                        <span className={`switch-label-${colorScheme}`}>Logo Required? </span>
                        <Switch
                            checked={logoRequired}
                            disabled={creatingChannels}
                            onChange={(e) => setLogoRequired(e.target.checked)}
                        />
                    </div>
                    {
                        logoRequired && (
                            <div className={`radio-container`}>
                                <RadioGroup
                                    row
                                    defaultValue="basic"
                                    name="channel-index-radio-group"
                                    onChange={(e) => setLogoSelection(e.target.value)}
                                    disabled={formControls.stormInProgress || formControls.loading}
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
                                            backgroundColor: colorScheme === 'light' ? "var(--very-light-red)" : "var(--dark-gray)",
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
                                                        sx={{
                                                            ...btnProps,
                                                            marginTop: "0",
                                                            // height: "3.5rem",
                                                            backgroundColor: colorScheme === 'light' ? "var(--bright-red-2)" : "var(--input-active-red-dark)"
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
                            <TextField
                                multiline
                                fullWidth
                                rows={4}
                                variant="outlined"
                                label="Channel names"
                                sx={{
                                    ...inputProps,
                                    marginTop: "1rem"
                                }}
                                value={channelsString}
                                onChange={e => channelsChangeHandler(e.target.value)}
                                error={channelsError}
                                helperText={channelsHelperText}
                                disabled={creatingChannels}
                            />
                        )
                    }
                </div>
            </div>

            <Button
                variant="contained"
                sx={{
                    ...btnProps,
                    marginTop: "1rem",
                }}
                disabled={creatingChannels}
                startIcon={creatingChannels ? <RefreshCw size={20} className="spin"/> : null}
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
