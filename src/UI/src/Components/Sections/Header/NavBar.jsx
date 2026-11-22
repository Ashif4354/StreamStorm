/* eslint-disable react/prop-types */
import { useState } from 'react';
import { Settings, BookOpen, ExternalLink } from 'lucide-react';
import * as atatus from '../../../lib/atatus';
import SettingsModal from '../../Modals/Settings/Settings';


const NavBar = ({ colorScheme }) => {
    const [settingsOpen, setSettingsOpen] = useState(false);

    return (
        <div>
            <nav className={`navbar`}>
                <a
                    href="https://streamstorm.darkglance.in/instructions"
                    target="_blank"
                    rel="noopener noreferrer"
                    className='navbar-item'
                    data-atatus-action-name="link-navbar-instructions"
                    onClick={() => {
                        atatus.addAction("navbar-instructions-clicked");
                        atatus.uiLogger.info("User opened external instructions page from navbar");
                    }}
                    style={{ color: colorScheme === 'light' ? 'var(--slight-dark-text)' : 'var(--slight-light-text)' }}
                >
                    <BookOpen size={20}/> Instructions <ExternalLink size={14} />
                </a>
                <a
                    data-atatus-action-name="btn-navbar-settings"
                    onClick={() => {
                        atatus.addAction("navbar-settings-clicked");
                        setSettingsOpen(true);
                    }}
                    className='navbar-item'
                    style={{ color: colorScheme === 'light' ? 'var(--slight-dark-text)' : 'var(--slight-light-text)' }}
                >
                    <Settings size={20}/> Settings
                </a>
            </nav>
            <SettingsModal open={settingsOpen} setOpen={setSettingsOpen} />
        </div>
    );
};

export default NavBar;
