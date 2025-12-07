import { useColorScheme } from '@mui/material/styles';
import { useLocalStorageState } from '@toolpad/core/useLocalStorageState';
import { logEvent } from 'firebase/analytics';
import { Sun, Moon } from 'lucide-react';

import { analytics } from '../../../../config/firebase';

const AppearanceSettings = () => {
    const { colorScheme, setColorScheme } = useColorScheme();
    const [, setDefaultColorScheme] = useLocalStorageState('theme');

    const handleThemeChange = (theme) => {
        setColorScheme(theme);
        setDefaultColorScheme(theme);
        logEvent(analytics, "theme_switch", { theme });
    };

    return (
        <div className="settings-section">
            <h3 className={`settings-section-title ${colorScheme}-text`}>Appearance</h3>
            <p className={`settings-section-description settings-section-description-${colorScheme}`}>
                Customize the look and feel of the application.
            </p>

            <div className="settings-section-content">
                <span className={`settings-label ${colorScheme}-text`}>Theme</span>
                <div className="theme-cards-container">
                    <div
                        className={`theme-card theme-card-light ${colorScheme === 'light' ? 'theme-card-active' : ''}`}
                        onClick={() => handleThemeChange('light')}
                    >
                        <div className="theme-card-preview theme-card-preview-light">
                            <div className="theme-preview-header"></div>
                            <div className="theme-preview-content">
                                <div className="theme-preview-sidebar"></div>
                                <div className="theme-preview-main"></div>
                            </div>
                        </div>
                        <div className="theme-card-label">
                            <Sun size={16} />
                            Light
                        </div>
                    </div>

                    <div
                        className={`theme-card theme-card-dark ${colorScheme === 'dark' ? 'theme-card-active' : ''}`}
                        onClick={() => handleThemeChange('dark')}
                    >
                        <div className="theme-card-preview theme-card-preview-dark">
                            <div className="theme-preview-header"></div>
                            <div className="theme-preview-content">
                                <div className="theme-preview-sidebar"></div>
                                <div className="theme-preview-main"></div>
                            </div>
                        </div>
                        <div className="theme-card-label">
                            <Moon size={16} />
                            Dark
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AppearanceSettings;
