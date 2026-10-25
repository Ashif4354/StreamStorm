import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@mui/material/styles';

import * as atatus from './lib/atatus';
import App from './App.jsx';
import { theme } from "./lib/theme.js";
import AppProviders from './lib/AppProviders.jsx';
import AtatusErrorBoundary from './Components/Elements/AtatusErrorBoundary';

// Install transparent fetch payload observer & DOM input change listeners
atatus.installGlobalObservers();
atatus.addTiming('react_init_start');

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <AtatusErrorBoundary>
            <ThemeProvider theme={theme}>
                <AppProviders>
                    <App />
                </AppProviders>
            </ThemeProvider>
        </AtatusErrorBoundary>
    </StrictMode>
);

atatus.addTiming('react_root_mounted');
