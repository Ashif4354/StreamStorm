import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import { useColorScheme } from '@mui/material';

const InfoCard = ({ title, icon, text, color }) => {
    const { colorScheme } = useColorScheme();

    return (
        <Card
            sx={{
                height: 60,
                minWidth: 129,
                background: 'none',
                borderRadius: 'var(--border-radius)',
                padding: '0.25rem',
                flex: 1,
                "&.MuiCard-root": {
                    padding: '0.5rem 0.5rem 0.5rem 1rem',
                },
                "& .MuiCardContent-root": {
                    padding: '0',
                    height: '100%'
                },
            }}
            className={`${colorScheme}-bordered-container`}
        >
            <CardContent sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography sx={{ fontSize: 14 }} gutterBottom>
                        {title}
                    </Typography>
                    <Typography sx={{ fontSize: 14 }} color="text.secondary">
                        {icon}
                    </Typography>
                </div>
                <Typography sx={{ fontSize: 20, fontWeight: 700, margin: '0' }} color={color}>
                    {text}
                </Typography>
            </CardContent>
        </Card>
    );
}

export default InfoCard;