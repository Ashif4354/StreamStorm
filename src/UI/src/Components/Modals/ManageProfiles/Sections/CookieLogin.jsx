import { useState } from 'react';
import { Cookie, RefreshCw, LogIn } from 'lucide-react';
import { Button, useColorScheme, Alert } from '@mui/material';
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
                    setIsLoggedIn(true); // Update login state
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
        </div>
    );
};

export default CookieLogin;
