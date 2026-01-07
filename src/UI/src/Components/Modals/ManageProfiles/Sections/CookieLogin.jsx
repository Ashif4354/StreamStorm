import { useState, useRef } from 'react';
import { Cookie, RefreshCw, LogIn, Upload, FileUp } from 'lucide-react';
import { Button, useColorScheme, Alert, Divider, Typography } from '@mui/material';
import { useNotifications } from '@toolpad/core/useNotifications';
import { logEvent } from 'firebase/analytics';

import * as atatus from 'atatus-spa';

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

    const handleCookieLogin = () => {
        setErrorText("");
        setLoading(true);

        logEvent(analytics, "cookie_login_start");

        fetch(`${hostAddress}/environment/profiles/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    setIsLoggedIn(true);
                    notifications.show("Logged in successfully! Cookies saved.", {
                        severity: "success",
                    });
                    logEvent(analytics, "cookie_login_success");
                } else {
                    setErrorText(data.message || "An error occurred during login.");
                    notifications.show("Failed to login.", {
                        severity: "error",
                    });
                    logEvent(analytics, "cookie_login_failed");
                }
            })
            .catch((error) => {
                setErrorText("An error occurred during login. Try again.");
                notifications.show("Failed to login.", {
                    severity: "error",
                });
                atatus.notify(error, {}, ['cookie_login_error']);
                logEvent(analytics, "cookie_login_error");
            })
            .finally(() => {
                setLoading(false);
            })
    }

    const handleFileChange = (e) => {
        const files = Array.from(e.target.files);
        setCookieFiles(files);
        setUploadError("");
    };

    const handleCookieUpload = async () => {
        if (cookieFiles.length === 0) {
            setUploadError("Please select at least one cookie file.");
            return;
        }

        setUploadError("");
        setUploadLoading(true);

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

            if (data.success) {
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
                setUploadError(data.message || "Failed to upload cookies.");
                notifications.show("Failed to upload cookies.", {
                    severity: "error",
                });
                logEvent(analytics, "cookie_upload_failed");
            }
        } catch (error) {
            setUploadError("An error occurred while uploading cookies. Try again.");
            notifications.show("Failed to upload cookies.", {
                severity: "error",
            });
            atatus.notify(error, {}, ['cookie_upload_error']);
            logEvent(analytics, "cookie_upload_error");
        } finally {
            setUploadLoading(false);
        }
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
