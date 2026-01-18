import { useColorScheme } from '@mui/material/styles';
import { Box, Typography, RadioGroup, FormControlLabel, Radio } from '@mui/material';

import SettingContainer from './SettingContainer';

/**
 * Radio option component with icon, label and description.
 */
const RadioOption = ({ value, icon, label, description }) => {
    const { colorScheme } = useColorScheme();
    const hoverBgColor = colorScheme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)';

    return (
        <FormControlLabel
            value={value}
            control={
                <Radio
                    sx={{
                        color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                        '&.Mui-checked': {
                            color: colorScheme === 'dark' ? 'var(--bright-red)' : 'var(--dark-red)',
                        },
                    }}
                />
            }
            label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {icon}
                    <Box>
                        <Typography
                            variant="body1"
                            sx={{
                                fontWeight: 500,
                                color: colorScheme === 'dark' ? 'var(--light-text)' : 'var(--dark-text)',
                            }}
                        >
                            {label}
                        </Typography>
                        <Typography
                            variant="caption"
                            sx={{
                                color: colorScheme === 'dark' ? 'var(--slight-light-text)' : 'var(--slight-dark-text)',
                            }}
                        >
                            {description}
                        </Typography>
                    </Box>
                </Box>
            }
            sx={{
                m: 0,
                p: 1.5,
                borderRadius: 'var(--border-radius)',
                '&:hover': { backgroundColor: hoverBgColor },
            }}
        />
    );
};

/**
 * Radio setting component with bordered container.
 * 
 * @param {string} title - Setting title
 * @param {string} description - Setting description  
 * @param {string} value - Current selected value
 * @param {function} onChange - Change handler (receives event)
 * @param {Array} options - Array of { value, icon, label, description }
 */
const RadioSetting = ({ title, description, value, onChange, options }) => {
    return (
        <SettingContainer title={title} description={description}>
            <RadioGroup value={value} onChange={onChange}>
                {options?.map((option) => (
                    <RadioOption
                        key={option.value}
                        value={option.value}
                        icon={option.icon}
                        label={option.label}
                        description={option.description}
                    />
                ))}
            </RadioGroup>
        </SettingContainer>
    );
};

export default RadioSetting;
