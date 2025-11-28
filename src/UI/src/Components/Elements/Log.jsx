import { useColorScheme } from "@mui/material";

const Log = ({ log }) => {
    const { colorScheme } = useColorScheme();
    const levelColor = log.level === 'INFO' ? 'var(--log-info)' : 'var(--log-error)';


    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'row',
                gap: '0.5rem',
                marginBottom: '0.25rem',
                fontFamily: 'ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,Liberation Mono,Courier New,monospace',
                fontSize: '0.875rem'
            }}
        >
            <span style={{
                color: colorScheme === 'light' ? 'var(--slight-dark-text)' : 'var(--slight-light-text)'
            }}>
                [{log.time}]
            </span>
            <span style={{ color: levelColor }}>[{log.level}]</span>
            <span style={{
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                color: colorScheme === 'light' ? 'var(--dark-text)' : 'var(--light-text)'
            }}>
                {log.message}
            </span>
        </div>
    );
}

export default Log;