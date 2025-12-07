import { useState } from 'react';
import { useColorScheme } from '@mui/material/styles';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import { Tornado } from 'lucide-react';

import TornadoDark from "../../../assets/tornado.png"
import NavBar from './NavBar';

import './Header.css';


const Header = () => {
    const { colorScheme } = useColorScheme();
    const [drawerOpen, setDrawerOpen] = useState(false);

    return (
        <header className={`header header-${colorScheme}`}>
            <div className="menu-button-container">
                <IconButton
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
                    <span className="drawer-title">Menu</span>
                    <NavBar />


                </Box>
            </Drawer>
        </header>
    );
}

export default Header;