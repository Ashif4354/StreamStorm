import { useColorScheme } from '@mui/material/styles';
import { Button, Box } from '@mui/material';

import SettingContainer from './SettingContainer';

/**
 * Button setting component with bordered container.
 * 
 * @param {string} title - Setting title
 * @param {string} description - Setting description
 * @param {string} buttonText - Text displayed on button
 * @param {function} onClick - Click handler
 * @param {React.ReactNode} startIcon - Optional start icon
 * @param {boolean} loading - Loading state
 * @param {boolean} disabled - Disabled state
 * @param {string} variant - Button variant (contained, outlined, text)
 */
const ButtonSetting = ({
    title,
    description,
    buttonText,
    onClick,
    startIcon,
    loading = false,
    disabled = false,
    variant = 'contained'
}) => {
    const { colorScheme } = useColorScheme();

    return (
        <SettingContainer title={title} description={description}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mt: 1 }}>
                <Button
                    variant={variant}
                    onClick={onClick}
                    disabled={disabled || loading}
                    startIcon={startIcon}
                    sx={{
                        backgroundColor: variant === 'contained'
                            ? (colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)')
                            : 'transparent',
                        color: variant === 'contained'
                            ? 'white'
                            : (colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)'),
                        borderColor: variant === 'outlined'
                            ? (colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)')
                            : undefined,
                        '&:hover': {
                            backgroundColor: variant === 'contained'
                                ? (colorScheme === 'dark' ? 'var(--bright-red-2-hover)' : 'var(--dark-red-2-hover)')
                                : 'rgba(255,255,255,0.05)',
                        },
                        '&.Mui-disabled': {
                            backgroundColor: colorScheme === 'dark' ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)',
                        },
                        textTransform: 'none',
                        borderRadius: 'var(--border-radius)',
                    }}
                >
                    {loading ? 'Loading...' : buttonText}
                </Button>
            </Box>
        </SettingContainer>
    );
};

export default ButtonSetting;
