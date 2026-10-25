/* eslint-disable react/prop-types */
import { useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import { Modal, Box } from '@mui/material';
import { SlidersHorizontal } from 'lucide-react';

import '../Modals.css';
import CloseButton from '../../Elements/CloseButton';
import { useCustomMUIProps } from '../../../context/CustomMUIPropsContext';
import ConfigData from './ConfigData';
import { useStormData } from '../../../context/StormDataContext';
import * as atatus from '../../../lib/atatus';

const ViewConfig = (props) => {

    const { open, setOpen } = props;
    const { modalProps } = useCustomMUIProps();
    const { colorScheme } = useColorScheme();
    const formControls = useStormData();

    useEffect(() => {
        if (open) {
            atatus.setViewName('/modal/view-config');
            atatus.setViewContext({ modal: 'view-config' });
            atatus.addAction('modal-opened', { modal: 'view-config' });
        }
    }, [open]);

    const modalCloseHandler = () => {
        atatus.addAction('modal-closed', { modal: 'view-config' });
        setOpen(false);
    };

    return (
        <Modal open={open} onClose={modalCloseHandler}>
            <Box sx={{
                ...modalProps,
                minWidth: '40vw',
                "@media (max-width: 400px)": {
                    minWidth: '80vw',
                    marginTop: '1rem',
                    maxHeight: '70vh'

                }
            }}>
                <div className='modal-header-container'>
                    <CloseButton onClick={modalCloseHandler} />
                    <div className={`modal-heading ${colorScheme}-text`}>
                        <SlidersHorizontal className='profile-icon' />
                        Storm Configurations
                    </div>
                    <div className="modal-header-description-container">
                        <span className={`modal-header-description modal-header-description-${colorScheme}`}>
                            View the configurations used for this storm session.
                        </span>
                    </div>
                </div>
                <ConfigData formControls={formControls}/>
            </Box>
        </Modal>
    );
};

export default ViewConfig;
