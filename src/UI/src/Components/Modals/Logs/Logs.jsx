/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box } from '@mui/material';
import { Users, Terminal } from 'lucide-react';

import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import LogsContainer from '../../Elements/LogsContainer';
import { useAppState } from '../../../context/AppStateContext';

const Logs = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const appState = useAppState();

    const modalCloseHandler = () => {
        setOpen(false);
    }

    return (
        <Modal open={open} onClose={modalCloseHandler}>
            <Box sx={{
                ...modalProps,
                minWidth: '200px',
                maxHeight: '50vh',
                "&.MuiBox-root": {
                    overflow: "hidden",
                }
            }}>
                <div>
                    <CloseButton onClick={modalCloseHandler} />
                    <div className={`modal-heading ${colorScheme}-text`}>
                        <Terminal className='profile-icon' />
                        Live Log Feed
                    </div>
                    <div className="modal-header-description-container">
                        <span className={`modal-header-description modal-header-description-${colorScheme}`}>
                            Complete logs for this session are being saved at:
                        </span>
                        <span className={`modal-header-description modal-header-description-${colorScheme}`}>
                            {appState.logFilePath}
                        </span>
                    </div>
                </div>

                <Divider sx={{ margin: '1rem 0' }} />
                <div style={{ maxHeight: '500px', overflowY: 'scroll' }}>
                    <LogsContainer />
                </div>
            </Box>
        </Modal>
    );
};

export default Logs;