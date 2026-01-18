import { useColorScheme } from '@mui/material/styles';
import { Select, MenuItem, FormControl, Box } from '@mui/material';

import SettingContainer from './SettingContainer';

/**
 * Dropdown/Select setting component with bordered container.
 * 
 * @param {string} title - Setting title
 * @param {string} description - Setting description
 * @param {string} value - Current selected value
 * @param {function} onChange - Change handler (receives event)
 * @param {Array} options - Array of { value, label } or strings
 */
const DropdownSetting = ({ title, description, value, onChange, options }) => {
    const { colorScheme } = useColorScheme();
    const borderColor = colorScheme === 'dark' ? '#333333' : 'var(--light-border)';

    return (
        <SettingContainer title={title} description={description}>
            <FormControl fullWidth size="small" sx={{ mt: 1 }}>
                <Select
                    value={value}
                    onChange={onChange}
                    sx={{
                        color: colorScheme === 'dark' ? 'var(--light-text)' : 'var(--dark-text)',
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: borderColor,
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                            borderColor: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                            borderColor: colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)',
                        },
                        '& .MuiSvgIcon-root': {
                            color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        },
                    }}
                    MenuProps={{
                        PaperProps: {
                            sx: {
                                backgroundColor: colorScheme === 'dark' ? 'var(--light-gray)' : 'var(--light-card-bg)',
                                color: colorScheme === 'dark' ? 'var(--light-text)' : 'var(--dark-text)',
                            },
                        },
                    }}
                >
                    {options.map((option) => {
                        const optionValue = typeof option === 'string' ? option : option.value;
                        const optionLabel = typeof option === 'string' ? option : option.label;
                        return (
                            <MenuItem key={optionValue} value={optionValue}>
                                {optionLabel}
                            </MenuItem>
                        );
                    })}
                </Select>
            </FormControl>
        </SettingContainer>
    );
};

export default DropdownSetting;
