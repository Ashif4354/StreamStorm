import { IconButton, Tooltip } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const CloseButton = ({ onClick }) => {

    return (
        <IconButton
            sx={{ position: 'absolute', right: '5px', top: '5px', '&:hover': { backgroundColor: '#ffffff10' } }}
            onClick={onClick}
            size="small"
        >
            <CloseIcon sx={{ color: "var(--gray-text)" }} />
        </IconButton>
    );
};

export default CloseButton;