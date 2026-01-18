import { useEffect, useState } from 'react';
import { createContext, useContext } from 'react';
import { io } from "socket.io-client";

import { useAppState } from "./AppStateContext";

const SocketContext = createContext();

const SocketProvider = ({ children }) => {

    const [socket, setSocket] = useState(null);
    const [socketConnected, setSocketConnected] = useState(false);
    const { hostAddress } = useAppState();

    useEffect(() => {

        if (!hostAddress) {
            console.warn("No host address provided for Socket.IO connection.");
            return;
        }

        const newSocket = io(hostAddress);
        setSocket(newSocket);

        newSocket.on("connect", () => {
            setSocketConnected(true);
        });

        return () => {
            setSocketConnected(false);
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