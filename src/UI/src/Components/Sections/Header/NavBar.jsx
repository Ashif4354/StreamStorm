import { useState } from 'react';
import { Settings } from 'lucide-react';
import SettingsModal from '../../Modals/Settings/Settings';


const NavBar = ({ colorScheme }) => {
    const [settingsOpen, setSettingsOpen] = useState(false);

    return (
        <div>
            <nav className={`navbar`}>
                <a
                    onClick={() => setSettingsOpen(true)}
                    className='navbar-item'
                    style={{ color: colorScheme === 'light' ? 'var(--slight-dark-text)' : 'var(--slight-light-text)' }}
                >
                    <Settings /> Settings
                </a>
                {/* Other navigation items go here */}
            </nav>
            <SettingsModal open={settingsOpen} setOpen={setSettingsOpen} />
        </div>
    )
}

export default NavBar;