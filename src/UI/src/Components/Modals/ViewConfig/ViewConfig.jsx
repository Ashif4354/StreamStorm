/* eslint-disable react/prop-types */
import { useColorScheme } from '@mui/material/styles';
import { Divider, Modal, Box } from '@mui/material';
import { SlidersHorizontal } from 'lucide-react';

import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';

const ViewConfig = (props) => {

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
                        <SlidersHorizontal className='profile-icon' />
                         View Configurations
                    </div>
                    <div className="modal-header-description-container">
                        <span className={`modal-header-description modal-header-description-${colorScheme}`}>
                            View the configurations used for this storm session.
                        </span>
                    </div>
                </div>

            </Box>
        </Modal>
    );
};

export default ViewConfig;