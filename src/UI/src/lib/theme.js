import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
    colorSchemes: {
        light: {
            palette: {
                primary: {
                    main: '#6366f1',
                },
                background: {
                    default: '#f8fafc',
                    paper: '#ffffff',
                },
            },
        },
        dark: {
            palette: {
                primary: {
                    main: '#dc2828',
                }
            },
        },
    },
    typography: {
        fontFamily: "'Inter', sans-serif"
    },
});