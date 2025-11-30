import { useColorScheme } from "@mui/material";

const TextBasedConfig = (props) => {
    const { icon, title, value } = props
    const { colorScheme } = useColorScheme();

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
            <div
                className='text-based-config-value-container'
                style={{
                    color: colorScheme === "dark" ? "var(--light-text)" : "var(--dark-text)",
                    fontSize: '0.875rem'
                }}
            >
                {value}
            </div>
        </div>
    );
}

export default TextBasedConfig