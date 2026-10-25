/* eslint-disable react/prop-types */
import { useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Modal, Box } from '@mui/material';
import { Antenna } from 'lucide-react';

import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import ChannelCard from './ChannelCard';
import { useAppState } from '../../../context/AppStateContext';
import * as atatus from '../../../lib/atatus';

const ChannelsStatus = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const appState = useAppState();

    useEffect(() => {
        if (open) {
            atatus.setViewName('/modal/channels-status');
            atatus.setViewContext({ totalChannels: Object.keys(appState.allChannels || {}).length });
            atatus.addAction('channels-status-modal-opened', { totalChannels: Object.keys(appState.allChannels || {}).length });
        }
    }, [open, appState.allChannels]);

    const modalCloseHandler = () => {
        atatus.addAction('channels-status-modal-closed');
        setOpen(false);
    };
    
    const sortChannelByStatus = (a, b) => {
        return b.status - a.status;
    };

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
                        ))
                    }
                </div>

            </Box>
        </Modal>
    );
};

export default ChannelsStatus;
