import { useMemo } from "react";
import { DialogsProvider } from '@toolpad/core/useDialogs';
import { NotificationsProvider, } from '@toolpad/core/useNotifications';

import { CustomMUIPropsContext, CurrentBrowserContext } from './ContextAPI';
import { getCustomMUIProps } from "./CustomMUIProps";
import getBrowser from "./getBrowser";


const AppProviders = ({ children, theme }) => {

    const browser = useMemo(getBrowser, []);
    const MUIProps = useMemo(() => getCustomMUIProps(theme), [theme]);

    return (
        <CustomMUIPropsContext.Provider value={MUIProps}>
            <DialogsProvider>
                <NotificationsProvider slotProps={{
                    snackbar: {
                        anchorOrigin: { vertical: 'bottom', horizontal: 'left' },
                        autoHideDuration: 2500,
                    },
                }}>
                    <CurrentBrowserContext.Provider value={browser}>
                        {children}
                    </CurrentBrowserContext.Provider>

                </NotificationsProvider>
            </DialogsProvider>
        </CustomMUIPropsContext.Provider>
    )
}

export default AppProviders;