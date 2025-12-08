/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box } from '@mui/material';
import { Users } from 'lucide-react';

import './ManageProfiles.css';
import CreateProfiles from './Sections/CreateProfiles';
import DeleteAllProfiles from './Sections/DeleteAllProfiles';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import CreateChannels from './Sections/CreateChannels';

const ManageProfiles = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();

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
                            Create Youtube channels and manage your temp browser profiles for the Storm
                        </span>
                    </div>
                </div>

                <CreateChannels />
                <Divider sx={{ margin: '2rem 0' }} />
                <CreateProfiles />

                <Divider sx={{ margin: '2rem 0' }} />

                <DeleteAllProfiles />
            </Box>
        </Modal>
    );
};

export default ManageProfiles;