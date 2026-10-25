import { useEffect } from "react";
import "./Footer.css";
import { useColorScheme } from '@mui/material/styles';
import * as atatus from "../../../lib/atatus";
import { useAppState } from "../../../context/AppStateContext";

const Footer = () => {
    const { colorScheme } = useColorScheme();
    const appState = useAppState();

    useEffect(() => {
        if (appState.engineVersion) {
            atatus.setGlobalContextProperty("engineVersion", appState.engineVersion);
        }
        if (import.meta.env.VITE_APP_VERSION) {
            atatus.setGlobalContextProperty("uiVersion", import.meta.env.VITE_APP_VERSION);
        }
    }, [appState.engineVersion]);

    return (
        <footer className={`footer footer-${colorScheme} ${colorScheme}-bordered-container`}>
            <div className="footer-content">
                <p className="footer-text">Email: darkglance.developer@gmail.com for any queries.</p>
                <p className="footer-text">© {new Date().getFullYear()} StreamStorm. All rights reserved.</p>
                <div className="versions-text">
                    <p>UI Version: {import.meta.env.VITE_APP_VERSION}</p>
                    <p>Engine Version: {appState.engineVersion}</p>
                </div>
            </div>

        </footer>
    );
};

export default Footer;
