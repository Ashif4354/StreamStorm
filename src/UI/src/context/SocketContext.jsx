import { useEffect, useState, createContext, useContext } from 'react';
import { io } from "socket.io-client";

import { useAppState } from "./AppStateContext";
import * as atatus from '../lib/atatus';

const SocketContext = createContext();

const SocketProvider = ({ children }) => {

    const [socket, setSocket] = useState(null);
    const [socketConnected, setSocketConnected] = useState(false);
    const { hostAddress } = useAppState();

    useEffect(() => {

        if (!hostAddress) {
            console.warn("No host address provided for Socket.IO connection.");
            atatus.socketLogger.warn("No host address provided for Socket.IO connection");
            return;
        }

        atatus.startResource(hostAddress, { type: 'websocket' });
        const newSocket = io(hostAddress);
        setSocket(newSocket);

        newSocket.on("connect", () => {
            setSocketConnected(true);
            atatus.stopResource(hostAddress, { status: 200 });
            atatus.setGlobalContextProperty('socketConnected', true);
            atatus.addAction('socket-connected', { hostAddress, socketId: newSocket.id });
            atatus.socketLogger.info('Socket.IO connected to Engine', { hostAddress, socketId: newSocket.id });
        });

        newSocket.on("disconnect", (reason) => {
            setSocketConnected(false);
            atatus.setGlobalContextProperty('socketConnected', false);
            atatus.addAction('socket-disconnected', { hostAddress, reason });
            atatus.socketLogger.warn('Socket.IO disconnected', { hostAddress, reason });
        });

        newSocket.on("connect_error", (err) => {
            setSocketConnected(false);
            atatus.setGlobalContextProperty('socketConnected', false);
            atatus.addError(err, { tags: ['socket_connect_error'], hostAddress });
            atatus.socketLogger.error('Socket.IO connection error', { hostAddress }, err);
        });

        return () => {
            setSocketConnected(false);
            atatus.setGlobalContextProperty('socketConnected', false);
            newSocket.disconnect();
        };
    }, [hostAddress]);

    const values = {
        socket,
        socketConnected,
    };

    return (
        <SocketContext.Provider value={values}>
            {children}
        </SocketContext.Provider>
    );
};

const useSocket = () => {
    return useContext(SocketContext);
};

export { SocketProvider, useSocket };
