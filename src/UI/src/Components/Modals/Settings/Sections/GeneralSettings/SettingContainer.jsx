import { useColorScheme } from '@mui/material/styles';
import { Box, Typography } from '@mui/material';

/**
 * Base container for all setting components.
 * Provides bordered container with title and description.
 * 
 * @param {string} title - Setting title
 * @param {string} description - Setting description
 * @param {React.ReactNode} children - Action component (radio/switch/dropdown/etc)
 */
const SettingContainer = ({ title, description, children }) => {
    const { colorScheme } = useColorScheme();
    const borderColor = colorScheme === 'dark' ? '#333333' : 'var(--light-border)';

    return (
        <Box
            sx={{
                border: `1px solid ${borderColor}`,
                borderRadius: 'var(--border-radius)',
                p: 2,
            }}
        >
            <Box sx={{ mb: 1.5 }}>
                <Typography
                    variant="subtitle1"
                    sx={{
                        fontWeight: 600,
                        color: colorScheme === 'dark' ? 'var(--light-text)' : 'var(--dark-text)',
                    }}
                >
                    {title}
                </Typography>
                <Typography
                    variant="body2"
                    sx={{
                        color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        mt: 0.5,
                    }}
                >
                    {description}
                </Typography>
            </Box>
            {children}
        </Box>
    );
};

export default SettingContainer;
