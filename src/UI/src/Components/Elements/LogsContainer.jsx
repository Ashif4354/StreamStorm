import { useEffect, useRef } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';

import { useAppState } from '../../context/AppStateContext';
import Log from './Log';

const LogsContainer = () => {
    const { logs } = useAppState();
    const scrollRef = useRef(null);

    useEffect(() => {
        const element = scrollRef.current;
        if (element) {
            element.scrollTop = element.scrollHeight;
        }
    }, [logs]);

    return (
        <Box
            ref={scrollRef}
            sx={{
                height: '100%',
                // overflow: 'scroll',
                p: 2,
                "&.MuiBox-root": {
                    padding: "0",
                }
            }}
        >
            <Stack
                sx={{
                    overflow: 'scroll',
                }}
            >
                {
                    logs.map((log, index) => (
                        <Log key={index} log={log} />
                    ))
                }
            </Stack>
        </Box>
    );
};

export default LogsContainer;