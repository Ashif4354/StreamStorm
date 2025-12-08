import { useEffect, useRef, useState } from 'react';
import { createContext, useContext } from 'react';
import { io } from "socket.io-client";

import { useLocalStorageState } from "@toolpad/core/useLocalStorageState";
import { DEFAULT_HOST_ADDRESS } from '../lib/Constants';


const SocketContext = createContext();

const SocketProvider = ({ children }) => {

    const [socket, setSocket] = useState(null);
    const [socketConnected, setSocketConnected] = useState(false);
    const [hostAddress] = useLocalStorageState("hostAddress", DEFAULT_HOST_ADDRESS);
    console.log("SocketProvider hostAddress:", hostAddress);

    useEffect(() => {

        if (!hostAddress) {
            console.warn("No host address provided for Socket.IO connection.");
            return;
        }

        const newSocket = io(hostAddress);
        setSocket(newSocket);

        newSocket.on("connect", () => {
            setSocketConnected(true);
            console.log("Connected to Socket.IO server with ID:", newSocket.id);
            console.log("Socket object:", newSocket);
        });

        // newSocket.on("system_info", (data) => {
        //     console.log("Received system_info:", data);
        // });

        return () => {
            console.log("Disconnecting from Socket.IO server...");
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