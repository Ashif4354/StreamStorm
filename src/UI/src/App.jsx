import { useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';

import "./App.css";
import { useSocket } from './context/SocketContext';
import { useAppState } from './context/AppStateContext';
import Header from "./Components/Sections/Header/Header";
import Footer from "./Components/Sections/Footer/Footer";
import Main from "./Components/Sections/Main/Main";
import { MAX_LOGS } from './lib/Constants';
import * as atatus from './lib/atatus';

const App = () => {

    const { colorScheme } = useColorScheme();
    const { socket, socketConnected } = useSocket();
    const appState = useAppState();

    useEffect(() => {
        if (colorScheme) {
            atatus.setGlobalContextProperty('colorScheme', colorScheme);
            atatus.addFeatureFlagEvaluation('color_scheme', colorScheme);
        }
    }, [colorScheme]);

    useEffect(() => {
        if (!socket || !socket.connected || !socketConnected) return;

        socket.on("log", (data) => {
            appState.setLogs(prevLogs => {
                const newLogs = [...prevLogs, data];
                if (newLogs.length > MAX_LOGS) {
                    newLogs.shift();
                }
                return newLogs;
            });
        });

        return () => {
            socket.off("log");
        };
    }, [socket, socketConnected]);

    return (
        <div className={`main-container main-container-${colorScheme}`}>
            <Header />
            <Main />
            <Footer />
        </div>
    );
};

export default App;
