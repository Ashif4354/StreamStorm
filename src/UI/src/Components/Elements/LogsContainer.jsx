import { useEffect, useRef } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';

import { useAppState } from '../../context/AppStateContext';
import Log from './Log';

const LogsContainer = () => {
    const { logs } = useAppState();
    const bottomRef = useRef(null);

    useEffect(() => {
        // Scroll to bottom when new logs arrive
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <Box
            sx={{
                height: '100%',
                p: 2,
                "&.MuiBox-root": {
                    padding: "0",
                }
            }}
        >
            <Stack>
                {
                    logs.map((log, index) => (
                        <Log key={index} log={log} />
                    ))
                }
                <div ref={bottomRef} />
            </Stack>
        </Box>
    );
};

export default LogsContainer;