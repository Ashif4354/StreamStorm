import { useColorScheme } from '@mui/material/styles';
import { Info } from 'lucide-react';
import { Alert } from '@mui/material';

const GeneralSettings = () => {
    const { colorScheme } = useColorScheme();

    return (
        <div className="settings-section">
            <h3 className={`settings-section-title ${colorScheme}-text`}>General</h3>
            <p className={`settings-section-description settings-section-description-${colorScheme}`}>
                General application settings.
            </p>

            <Alert
                severity="info"
                icon={<Info size={16} />}
                sx={{
                    marginTop: '1rem',
                    borderRadius: 'var(--border-radius)',
                }}
            >
                More settings coming soon. This section is under development.
            </Alert>
        </div>
    );
};

export default GeneralSettings;
