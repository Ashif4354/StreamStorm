import { useMediaQuery } from '@mui/material';
import { analytics } from '@/config/firebase';
import { safeLogEvent as logEvent } from '../config/safeAnalytics.js';
import { usePathname } from 'next/navigation';
import * as atatus from '@/config/atatus';

const NavBar = ({ orientation, onClose }) => {

    const isSmallScreen = useMediaQuery('(max-width: 700px)')
    const pathname = usePathname();

    const handleLinkClick = (name) => {
        if (typeof onClose === 'function') onClose();
        logEvent(analytics, 'nav_link_click', {
            link_name: name,
        });
        atatus.addAction('site-nav-link-clicked', { link: name, orientation });
        atatus.navLogger.info(`Site navigation link clicked: ${name}`, { link: name, orientation });
    }    

    return (
        <>
            {pathname === '/' ? (
                <nav className={`navbar navbar-${orientation}`}>

                    <a href="/#overview" onClick={() => handleLinkClick('overview')} data-atatus-action-name="nav-overview" className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Overview</a>
                    <a href="/#features" onClick={() => handleLinkClick('features')} data-atatus-action-name="nav-features" className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Features</a>
                    <a href="/#disclaimer" onClick={() => handleLinkClick('disclaimer')} data-atatus-action-name="nav-disclaimer" className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Disclaimer</a>
                    <a href="https://discord.gg/wbeqxfzbAr" target="_blank" rel="noopener noreferrer" onClick={() => handleLinkClick('discord')} data-atatus-action-name="nav-discord" className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Discord</a> 
                    <a href="/instructions" onClick={() => handleLinkClick('instructions')} data-atatus-action-name="nav-instructions" className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Instructions</a>
                </nav>

            ) : null}
        </>
    )
}

export default NavBar;
