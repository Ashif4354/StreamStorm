import { DialogsProvider } from '@toolpad/core/useDialogs';
import { NotificationsProvider, } from '@toolpad/core/useNotifications';


import { StormDataProvider } from "../context/StormDataContext";
import { SystemInfoProvider } from "../context/SystemInfoContext";
import { CustomMUIPropsProvider } from "../context/CustomMUIPropsContext";
import { SocketProvider } from '../context/Socket';


const AppProviders = ({ children }) => {

    return (
        <CustomMUIPropsProvider>
            <DialogsProvider>
                <NotificationsProvider slotProps={{
                    snackbar: {
                        anchorOrigin: { vertical: 'bottom', horizontal: 'left' },
                        autoHideDuration: 2500,
                    },
                }}>
                    <SocketProvider>
                        <StormDataProvider>
                            <SystemInfoProvider>
                                {children}
                            </SystemInfoProvider>
                        </StormDataProvider>
                    </SocketProvider>
                </NotificationsProvider>
            </DialogsProvider>
        </CustomMUIPropsProvider>
    )
}

export default AppProviders;