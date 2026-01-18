/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box } from '@mui/material';
import { Users } from 'lucide-react';

import '../Modals.css';
import CreateProfiles from './Sections/CreateProfiles';
import CookieLogin from './Sections/CookieLogin';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import CreateChannels from './Sections/CreateChannels';
import { useAppState } from '../../../context/AppStateContext';

const ManageProfiles = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const { loginMethod } = useAppState();

    const modalCloseHandler = () => {
        setOpen(false);
    }

    return (
        <Modal open={open} onClose={modalCloseHandler}>
            <Box sx={modalProps}>
                <div className='modal-header-container'>
                    <CloseButton onClick={modalCloseHandler} />
                    <div className={`modal-heading ${colorScheme}-text`}>
                        <Users className='profile-icon' />
                        Manage Environment
                    </div>
                    <div className="modal-header-description-container">
                        <span className={`modal-header-description modal-header-description-${colorScheme}`}>
                            {loginMethod === 'cookies'
                                ? 'Login to Google and create YouTube channels for the Storm'
                                : 'Create YouTube channels and manage your temp browser profiles for the Storm'
                            }                        
                        </span>
                    </div>
                </div>

                {loginMethod === 'cookies' ? (
                    <CookieLogin />
                ) : (
                    <CreateProfiles />
                )}

                <Divider sx={{ margin: '2rem 0' }} />

                <CreateChannels />
            </Box>
        </Modal>
    );
};

export default ManageProfiles;