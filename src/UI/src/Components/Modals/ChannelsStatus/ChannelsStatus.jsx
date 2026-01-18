/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box } from '@mui/material';
import { Antenna } from 'lucide-react';

import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import ChannelCard from './ChannelCard';
import { useAppState } from '../../../context/AppStateContext';

const ChannelsStatus = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const appState = useAppState();

    const modalCloseHandler = () => {
        setOpen(false);
    }
    
    const sortChannelByStatus = (a, b) => {
        return b.status - a.status;
    }

    return (
        <Modal open={open} onClose={modalCloseHandler}>
            <Box
                sx={{
                    ...modalProps,
                    minWidth: '290px',
                    maxHeight: '50vh',
                    "&.MuiBox-root": {
                        overflowX: "visible",
                        overflowY: "hidden",
                        // paddingRight: "3rem",
                    }
                }}
            >
                <div className='modal-header-container'>
                    <CloseButton onClick={modalCloseHandler} />
                    <div className={`modal-heading ${colorScheme}-text`}>
                        <Antenna className='profile-icon' />
                        Channels Status
                    </div>
                    <div className="modal-header-description-container">
                        <span className={`modal-header-description modal-header-description-${colorScheme}`}>
                            Live status of all channels in the system.
                        </span>
                    </div>


                </div>
                <div style={{
                    maxHeight: '400px',
                    overflowY: 'scroll',
                    // overflowX: 'visible',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '.4rem',
                    minHeight: 0,
                    width: '100%',
                }}>
                    {
                        Object.keys(appState.allChannels).sort((a, b) => sortChannelByStatus(appState.allChannels[a], appState.allChannels[b])).map((channelId) => (
                            <div key={channelId} style={{ flexShrink: 0 }}>
                                <ChannelCard id={channelId} channel={appState.allChannels[channelId]} />
                            </div>
                        )
                        )
                    }
                </div>


            </Box>
        </Modal>
    );
};

export default ChannelsStatus;