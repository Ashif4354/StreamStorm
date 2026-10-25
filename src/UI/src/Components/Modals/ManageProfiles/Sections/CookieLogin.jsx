import { useState, useRef } from 'react';
import { Cookie, RefreshCw, LogIn, Upload, FileUp, UserPlus } from 'lucide-react';
import { Button, useColorScheme, Alert, Divider, Typography } from '@mui/material';
import { useNotifications } from '@toolpad/core/useNotifications';
import { logEvent } from 'firebase/analytics';

import * as atatus from '../../../../lib/atatus';

import "./Sections.css";
import ErrorText from '../../../Elements/ErrorText';
import { analytics } from '../../../../config/firebase';
import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../context/AppStateContext';

const CookieLogin = () => {

    const { btnProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const { hostAddress, isLoggedIn, setIsLoggedIn } = useAppState();
    const notifications = useNotifications();

    const [errorText, setErrorText] = useState("");
    const [loading, setLoading] = useState(false);

    // Cookie file upload state
    const [cookieFiles, setCookieFiles] = useState([]);
    const [uploadLoading, setUploadLoading] = useState(false);
    const [uploadError, setUploadError] = useState("");
    const fileInputRef = useRef(null);

    // Add account state
    const [addAccountLoading, setAddAccountLoading] = useState(false);
    const [addAccountError, setAddAccountError] = useState("");

    const handleCookieLogin = () => {
        setErrorText("");
        setLoading(true);

        atatus.addAction('cookie-login-triggered', { isLoggedIn });
        atatus.startOperation('cookie_login');
        atatus.startDurationVital('cookie_login');
        logEvent(analytics, "cookie_login_start");

        fetch(`${hostAddress}/environment/profiles/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                count: null,
                cookiesLogin: true
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                atatus.stopDurationVital('cookie_login');
                if (data.success) {
                    atatus.succeedOperation('cookie_login');
                    atatus.envLogger.info('Cookie login successful');
                    atatus.addAction('cookie-login-success');
                    atatus.addFeatureFlagEvaluation('is_logged_in', true);
                    setIsLoggedIn(true);
                    notifications.show("Logged in successfully! Cookies saved.", {
                        severity: "success",
                    });
                    logEvent(analytics, "cookie_login_success");
                } else {
                    atatus.failOperation('cookie_login', data.message || 'Cookie login failed');
                    setErrorText(data.message || 'An error occurred during login.');
                    notifications.show("Failed to login.", {
                        severity: "error",
                    });
                    if (data.error) {
                        console.error('Failed to cookie login:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['cookie_login_failed'] });
                        atatus.envLogger.error('Failed to cookie login', { response: data });
                    }
                    logEvent(analytics, "cookie_login_failed");
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('cookie_login');
                atatus.failOperation('cookie_login', error.message);
                setErrorText("An error occurred during login. Try again.");
                notifications.show("Failed to login.", {
                    severity: "error",
                });
                atatus.addError(error, { tags: ['cookie_login_error'] });
                atatus.envLogger.error('Cookie login error', { error: error.message });
                logEvent(analytics, "cookie_login_error");
            })
            .finally(() => {
                setLoading(false);
            });
    };

    const handleFileChange = (e) => {
        const files = Array.from(e.target.files);
        setCookieFiles(files);
        setUploadError("");
        atatus.addAction('cookie-files-selected', { count: files.length, fileNames: files.map(f => f.name) });
    };

    const handleCookieUpload = async () => {
        if (cookieFiles.length === 0) {
            setUploadError("Select at least one cookie file.");
            atatus.addAction('cookie-upload-validation-empty');
            return;
        }

        setUploadError("");
        setUploadLoading(true);

        atatus.addAction('cookie-upload-triggered', { count: cookieFiles.length, files: cookieFiles.map(f => ({ name: f.name, size: f.size })) });
        atatus.startOperation('cookie_upload');
        atatus.startDurationVital('cookie_upload');
        logEvent(analytics, "cookie_upload_start");

        const formData = new FormData();
        cookieFiles.forEach((file) => {
            formData.append("files", file);
        });

        try {
            const response = await fetch(`${hostAddress}/environment/profiles/save_cookies`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            atatus.stopDurationVital('cookie_upload');

            if (data.success) {
                atatus.succeedOperation('cookie_upload');
                atatus.envLogger.info('Cookie upload successful', { filesCount: cookieFiles.length });
                atatus.addAction('cookie-upload-success', { count: cookieFiles.length });
                atatus.addFeatureFlagEvaluation('is_logged_in', true);
                setIsLoggedIn(true);
                setCookieFiles([]);
                if (fileInputRef.current) {
                    fileInputRef.current.value = "";
                }
                notifications.show(data.message || "Cookies uploaded successfully!", {
                    severity: "success",
                });
                logEvent(analytics, "cookie_upload_success");
            } else {
                atatus.failOperation('cookie_upload', data.message || 'Failed to upload cookies.');
                setUploadError(data.message || 'Failed to upload cookies.');
                notifications.show("Failed to upload cookies.", {
                    severity: "error",
                });
                if (data.error) {
                    console.error('Failed to upload cookies:', data.error);
                    atatus.addError(new Error(data.error), { response: data, tags: ['cookie_upload_failed'] });
                    atatus.envLogger.error('Failed to upload cookies', { response: data });
                }
                logEvent(analytics, "cookie_upload_failed");
            }
        } catch (error) {
            atatus.stopDurationVital('cookie_upload');
            atatus.failOperation('cookie_upload', error.message);
            setUploadError("An error occurred while uploading cookies. Try again.");
            notifications.show("Failed to upload cookies.", {
                severity: "error",
            });
            atatus.addError(error, { tags: ['cookie_upload_error'] });
            atatus.envLogger.error('Cookie upload error', { error: error.message });
            logEvent(analytics, "cookie_upload_error");
        } finally {
            setUploadLoading(false);
        }
    };

    const handleAddAccount = () => {
        setAddAccountError("");
        setAddAccountLoading(true);

        atatus.addAction('add-account-triggered');
        atatus.startOperation('add_account');
        atatus.startDurationVital('add_account');
        logEvent(analytics, "add_account_start");

        fetch(`${hostAddress}/environment/profiles/add_account`, {
            method: "POST",
        })
            .then((response) => response.json())
            .then((data) => {
                atatus.stopDurationVital('add_account');
                if (data.success) {
                    atatus.succeedOperation('add_account');
                    atatus.envLogger.info('Google account added successfully');
                    atatus.addAction('add-account-success');
                    notifications.show(data.message || "Google account added successfully!", {
                        severity: "success",
                    });
                    logEvent(analytics, "add_account_success");
                } else {
                    atatus.failOperation('add_account', data.message || 'Failed to add account.');
                    setAddAccountError(data.message || 'Failed to add account.');
                    notifications.show("Failed to add account.", {
                        severity: "error",
                    });
                    if (data.error) {
                        console.error('Failed to add account:', data.error);
                        atatus.addError(new Error(data.error), { response: data, tags: ['add_account_failed'] });
                        atatus.envLogger.error('Failed to add account', { response: data });
                    }
                    logEvent(analytics, "add_account_failed");
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('add_account');
                atatus.failOperation('add_account', error.message);
                setAddAccountError("An error occurred while adding account. Try again.");
                notifications.show("Failed to add account.", {
                    severity: "error",
                });
                atatus.addError(error, { tags: ['add_account_error'] });
                atatus.envLogger.error('Add account error', { error: error.message });
                logEvent(analytics, "add_account_error");
            })
            .finally(() => {
                setAddAccountLoading(false);
            });
    };

    return (
        <div className="create-profiles-container">
            <div className="section-header">
                <Cookie className="section-logo" size={20} color={colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Login with Google</h3>
            </div>

            <div className="section-content">
                <Alert
                    severity={isLoggedIn ? "success" : "info"}
                    sx={{
                        borderRadius: 'var(--border-radius)',
                        marginTop: '1rem',
                    }}
                >
                    {isLoggedIn
                        ? "You have already logged in. Click the button below to login again with a Google account."
                        : "Click the button below to open a browser window and log in to your Google account. Your session cookies will be saved for future use."
                    }
                </Alert>
            </div>

            <div className="section-action">
                <Button
                    variant="contained"
                    color="primary"
                    className="create-profiles-button"
                    disabled={loading}
                    data-atatus-action-name="btn-cookie-login"
                    startIcon={loading ? <RefreshCw size={20} className="spin" /> : <LogIn size={20} />}
                    sx={{
                        ...btnProps,
                        marginTop: "1rem",
                    }}
                    onClick={handleCookieLogin}
                >
                    {loading
                        ? "Opening Browser..."
                        : isLoggedIn
                            ? "Login Again with Google"
                            : "Login with Google"
                    }
                </Button>

                <ErrorText errorText={errorText} />

                {isLoggedIn && (
                    <>
                        <Button
                            variant="outlined"
                            color="primary"
                            className="create-profiles-button"
                            disabled={addAccountLoading}
                            data-atatus-action-name="btn-add-account"
                            startIcon={addAccountLoading ? <RefreshCw size={20} className="spin" /> : <UserPlus size={20} />}
                            sx={{
                                ...btnProps,
                                marginTop: "0.75rem",
                            }}
                            onClick={handleAddAccount}
                        >
                            {addAccountLoading
                                ? "Opening Browser..."
                                : "Add Another Google Account"
                            }
                        </Button>
                        <ErrorText errorText={addAccountError} />
                    </>
                )}
            </div>

            {/* OR Divider */}
            <Divider sx={{ margin: '1.5rem 0' }}>
                <Typography
                    variant="body2"
                    sx={{
                        color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        px: 2
                    }}
                >
                    or
                </Typography>
            </Divider>

            {/* Login with Cookie Files */}
            <div className="section-header">
                <Upload className="section-logo" size={20} color={colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)"} />
                <h3 className={`section-title ${colorScheme}-text`}>Login with Cookie Files</h3>
            </div>

            <div className="section-content">
                <Alert
                    severity="info"
                    sx={{
                        borderRadius: 'var(--border-radius)',
                        marginTop: '1rem',
                    }}
                >
                    Upload your cookie files (JSON or Netscape format). You can select multiple files.
                </Alert>
            </div>

            <div className="section-action" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <input
                    type="file"
                    ref={fileInputRef}
                    multiple
                    accept=".json,.txt"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    id="cookie-file-input"
                />
                <label htmlFor="cookie-file-input">
                    <Button
                        variant="outlined"
                        component="span"
                        data-atatus-action-name="btn-select-cookie-files"
                        startIcon={<FileUp size={20} />}
                        sx={{
                            ...btnProps,
                            marginTop: "1rem",
                            width: '100%',
                        }}
                        disabled={uploadLoading}
                    >
                        {cookieFiles.length > 0
                            ? `${cookieFiles.length} file(s) selected`
                            : "Select Cookie Files"
                        }
                    </Button>
                </label>

                <Button
                    variant="contained"
                    color="primary"
                    data-atatus-action-name="btn-submit-cookies"
                    startIcon={uploadLoading ? <RefreshCw size={20} className="spin" /> : <Upload size={20} />}
                    sx={{
                        ...btnProps,
                    }}
                    disabled={uploadLoading || cookieFiles.length === 0}
                    onClick={handleCookieUpload}
                >
                    {uploadLoading ? "Submitting..." : "Submit Cookies"}
                </Button>

                <ErrorText errorText={uploadError} />
            </div>
        </div>
    );
};

export default CookieLogin;
