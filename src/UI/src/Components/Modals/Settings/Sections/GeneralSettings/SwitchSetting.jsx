import { useColorScheme } from '@mui/material/styles';
import { Switch, Box, Typography } from '@mui/material';

import SettingContainer from './SettingContainer';

/**
 * Switch/Toggle setting component with bordered container.
 * 
 * @param {string} title - Setting title
 * @param {string} description - Setting description
 * @param {boolean} checked - Current switch state
 * @param {function} onChange - Change handler (receives event)
 * @param {React.ReactNode} icon - Optional icon
 */
const SwitchSetting = ({ title, description, checked, onChange, icon }) => {
    const { colorScheme } = useColorScheme();

    return (
        <SettingContainer title={title} description={description}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {icon && (
                        <Box sx={{ color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)' }}>
                            {icon}
                        </Box>
                    )}
                </Box>
                <Switch
                    checked={checked}
                    onChange={onChange}
                    sx={{
                        '& .MuiSwitch-switchBase.Mui-checked': {
                            color: colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)',
                        },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                            backgroundColor: colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)',
                        },
                    }}
                />
            </Box>
        </SettingContainer>
    );
};

export default SwitchSetting;
