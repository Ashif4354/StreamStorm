import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import IconButton from '@mui/material/IconButton';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import MenuIcon from '@mui/icons-material/Menu';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import { Tornado } from 'lucide-react';
import { useLocalStorageState } from '@toolpad/core/useLocalStorageState';
import { logEvent } from 'firebase/analytics';

import TornadoDark from "../../../assets/tornado.png"
import { analytics } from '../../../config/firebase';
import CloseButton from '../../Elements/CloseButton';
import NavBar from './NavBar';

import './Header.css';


const Header = () => {
    const { colorScheme, setColorScheme } = useColorScheme();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [defaultColorScheme, setDefaultColorScheme] = useLocalStorageState('theme');

    const switchTheme = () => {
        const newColorScheme = colorScheme === 'light' ? 'dark' : 'light';
        setColorScheme(newColorScheme);
        setDefaultColorScheme(newColorScheme);
        logEvent(analytics, "theme_switch", { theme: newColorScheme });
    }

    return (
        <header className={`header header-${colorScheme}`}>
            <div className="menu-button-container">
                <IconButton
                    // className={`theme-toggle-button ${colorScheme}`}
                    onClick={() => setDrawerOpen(true)}
                >
                    <MenuIcon sx={{ color: "white" }} />

                </IconButton>

            </div>
            <div className="header-heading-container">
                {
                    colorScheme === 'light' ? (
                        <Tornado className="header-logo" color="white" />
                    ) : (
                        <img src={TornadoDark} alt="StreamStorm Logo" className="header-logo" />
                    )
                }
                <h1 className="header-logo-text">StreamStorm</h1>
            </div>

            <div className="theme-toggle">
                <IconButton
                    className={`theme-toggle-button ${colorScheme}`}
                    onClick={switchTheme}
                >
                    {colorScheme === 'light' ? <DarkModeIcon sx={{ color: "white" }} /> : <LightModeIcon />}
                </IconButton>
            </div>

            <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
                <Box
                    role="presentation"
                    sx={{
                        backgroundColor: 'var(--dark-gray)',
                        width: 150,
                        height: '100%',
                        padding: '2.5rem'
                    }}
                >
                    {/* <AppTitle /> */}
                    <span className="drawer-title">Menu</span>
                    <NavBar />


                </Box>
            </Drawer>
        </header>
    );
}

export default Header; 