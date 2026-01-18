import { useColorScheme } from '@mui/material/styles';

import "./Main.css";
import Storm from "../../Cards/Storm/Storm";
import SystemInfo from "../../Cards/SystemInfo/SystemInfo";


const Main = () => {
    const { colorScheme } = useColorScheme();

    return (
        <main className={`main main-${colorScheme}`}>
            <Storm />
            <div className="left-cards-container">
                <SystemInfo />
            </div>
        </main>
    )
}

export default Main;