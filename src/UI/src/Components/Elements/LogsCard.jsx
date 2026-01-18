import { CardHeader, Card } from "@mui/material";
import { useColorScheme } from '@mui/material/styles';
import { Terminal } from "lucide-react";

import LogsContainer from './LogsContainer';

const LogsCard = () => {
    const { colorScheme } = useColorScheme();

    return (
        <Card
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: "var(--border-radius)",
                backgroundColor: colorScheme === 'light' ? "var(--light-card-bg)" : "var(--gray)",
                backgroundImage: "none",
                overflow: 'hidden',
            }}
            className={`logs-box-container ${colorScheme}-bordered-container`}
        >
            <CardHeader
                title="Live Log Feed"
                avatar={<Terminal size={20} />}
                sx={{
                    padding: "1.5rem",
                    "& .MuiTypography-root": {
                        fontWeight: "bold",
                        fontSize: "1rem",
                        letterSpacing: "-0.025rem",
                    }
                }}
            />
            <div style={{ padding: "0 1.5rem 1.5rem 1.5rem", overflow: 'scroll', }}>
                <LogsContainer />
            </div>
        </Card >
    );
};

export default LogsCard;