import { createContext, useEffect, useMemo, useContext } from 'react';
import { useColorScheme } from '@mui/material';
import { useLocalStorageState } from '@toolpad/core/useLocalStorageState';


const CustomMUIPropsContext = createContext();

const CustomMUIPropsProvider = ({ children }) => {

    const { colorScheme, setColorScheme } = useColorScheme();
    const [defaultColorScheme] = useLocalStorageState('theme', 'dark');

    const getCustomMUIProps = (colorScheme) => ({
        btnProps: {
            width: "100%",
            marginTop: "0.5rem",
            backgroundColor: colorScheme === 'light' ? "var(--light-btn-bg)" : "var(--dark-gray)",
            color: colorScheme === 'light' ? "var(--dark-text)" : "var(--light-text)",
            borderRadius: "var(--border-radius)",
            '&:hover': {
                backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--bright-red)",
                color: "var(--light-text)",
                boxShadow: "none",
            },
            '&:disabled': {
                backgroundColor: colorScheme === 'light' ? "var(--light-surface)" : "var(--dark-gray)",
                color: "gray",
            },
            height: "40px",
            boxShadow: "none",
            fontWeight: "500",
            textTransform: "none",
            justifyContent: "center",
            alignItems: "center",
            border: colorScheme === 'light' ? "1px solid var(--light-border)" : "1px solid #333333",
        },

        cardProps: {
            borderRadius: "var(--border-radius)",
            backgroundColor: colorScheme === 'light' ? "var(--light-card-bg)" : "var(--light-gray)",
            backgroundImage: "none"
        },

        inputProps: {
            '& .MuiInputBase-root.MuiOutlinedInput-root': {
                backgroundColor: colorScheme === 'light' ? "var(--light-surface)" : "var(--dark-gray)",
                borderRadius: "var(--border-radius)",
            },
            "& .MuiOutlinedInput-notchedOutline": {
                borderColor: colorScheme === 'light' ? "var(--light-border)" : "#333333",
            }
        },

        modalProps: {
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: "fit-content",
            bgcolor: colorScheme === 'light' ? 'var(--light-card-bg)' : 'var(--light-gray)',
            boxShadow: 24,
            borderRadius: 'var(--border-radius)',
            padding: '2rem',
            overflow: 'auto',
            '@media (max-width: 800px)': {
                width: '70%',
            },
            '@media (max-width: 460px)': {
                height: '90%',
                padding: '2rem 2rem 2rem 2rem',
                margin: 'auto',
            }
        }
    });

    useEffect(() => {
        setColorScheme(defaultColorScheme);
    }, [setColorScheme, defaultColorScheme]);

    const MUIProps = useMemo(() => getCustomMUIProps(colorScheme), [colorScheme]);

    return (
        <CustomMUIPropsContext.Provider value={MUIProps}>
            {children}
        </CustomMUIPropsContext.Provider>
    );
};

const useCustomMUIProps = () => {
    return useContext(CustomMUIPropsContext);
};

export { CustomMUIPropsProvider, useCustomMUIProps };