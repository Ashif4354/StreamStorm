import { useEffect } from 'react';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import NavBar from './NavBar';
import CloseButton from './CloseButton';
import * as atatus from '@/config/atatus';

const DrawerComponent = ({ open, onClose }) => {

    useEffect(() => {
        if (open) {
            atatus.addAction('site-drawer-opened');
            atatus.uiLogger.debug('Site mobile navigation drawer opened');
        }
    }, [open]);

    const handleClose = () => {
        atatus.addAction('site-drawer-closed');
        atatus.uiLogger.debug('Site mobile navigation drawer closed');
        if (typeof onClose === 'function') onClose();
    };

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={handleClose}
        >
            <CloseButton onClick={handleClose} />
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
                <NavBar orientation="vertical" onClose={handleClose} />


            </Box>
        </Drawer>
    )
}

export default DrawerComponent;
