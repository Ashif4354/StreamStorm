import { useMediaQuery } from '@mui/material';
import { analytics } from '@/config/firebase';
import { logEvent } from 'firebase/analytics';
import { usePathname } from 'next/navigation';

const NavBar = ({ orientation, onClose }) => {

    const isSmallScreen = useMediaQuery('(max-width: 700px)')
    const pathname = usePathname();

    const handleLinkClick = (name) => {
        onClose();
        logEvent(analytics, 'nav_link_click', {
            link_name: name,
        });
    }    

    return (
        <>
            {pathname === '/' ? (
                <nav className={`navbar navbar-${orientation}`}>

                    <a href="/#overview" onClick={() => handleLinkClick('overview')} className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Overview</a>
                    <a href="/#features" onClick={() => handleLinkClick('features')} className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Features</a>
                    <a href="/#disclaimer" onClick={() => handleLinkClick('disclaimer')} className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Disclaimer</a>
                    <a href="https://discord.gg/wbeqxfzbAr" target="_blank" rel="noopener noreferrer" className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Discord</a> 
                    <a href="/instructions" onClick={() => handleLinkClick('instructions')} className={`navbar-item navbar-item-${isSmallScreen ? 'small' : 'large'}`}>Instructions</a>
                </nav>

            ) : null}
        </>
    )
}

export default NavBar;