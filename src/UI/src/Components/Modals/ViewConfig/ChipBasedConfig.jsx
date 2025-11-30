import { useColorScheme, Chip } from "@mui/material";

const ChipBasedConfig = (props) => {
    const { icon, title, disabled, value } = props
    const { colorScheme } = useColorScheme();

    const chipColor = disabled ? "default" : "success";
    const chipText = disabled ? "Disabled" : value;

    return (
        <div className='text-based-config-container'>
            <div
                className='text-based-config-icon-container'
                style={{
                    color: colorScheme === "dark" ? "var(--slight-light-text)" : "var(--slight-dark-text)",
                }}
            >
                {icon}
            </div>

            <div
                className='text-based-config-title-container'
                style={{
                    color: colorScheme === "dark" ? "var(--slight-light-text)" : "var(--slight-dark-text)",
                    fontSize: '0.875rem',
                    flex: 1
                }}
            >
                {title}
            </div>

            <Chip
                sx={{
                    width: '120px',
                    // marginRight: channel.status === 3 ? '0' : '1rem',
                }}
                variant="outlined"
                size="small"
                color={chipColor}
                label={chipText}
                icon={null}
            />

        </div>
    );
}

export default ChipBasedConfig;