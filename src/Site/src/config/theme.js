"use client"
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
    colorSchemes: {
        light: {
            palette: {
                primary: {
                    main: '#b41d1d',
                },
                // ...other tokens
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