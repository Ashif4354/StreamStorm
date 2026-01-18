import { useColorScheme } from '@mui/material/styles';
import { TextField, Box } from '@mui/material';

import SettingContainer from './SettingContainer';

/**
 * TextField setting component with bordered container.
 * 
 * @param {string} title - Setting title
 * @param {string} description - Setting description
 * @param {string} value - Current input value
 * @param {function} onChange - Change handler (receives event)
 * @param {string} placeholder - Optional placeholder text
 * @param {string} type - Input type (text, number, password, etc)
 */
const TextFieldSetting = ({ title, description, value, onChange, placeholder, type = 'text' }) => {
    const { colorScheme } = useColorScheme();
    const borderColor = colorScheme === 'dark' ? '#333333' : 'var(--light-border)';

    return (
        <SettingContainer title={title} description={description}>
            <TextField
                fullWidth
                size="small"
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                sx={{
                    mt: 1,
                    '& .MuiOutlinedInput-root': {
                        color: colorScheme === 'dark' ? 'var(--light-text)' : 'var(--dark-text)',
                        '& fieldset': {
                            borderColor: borderColor,
                        },
                        '&:hover fieldset': {
                            borderColor: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        },
                        '&.Mui-focused fieldset': {
                            borderColor: colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)',
                        },
                    },
                    '& .MuiInputBase-input::placeholder': {
                        color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        opacity: 0.7,
                    },
                }}
            />
        </SettingContainer>
    );
};

export default TextFieldSetting;
