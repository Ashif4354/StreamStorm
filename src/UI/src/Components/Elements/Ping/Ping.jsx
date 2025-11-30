import "./Ping.css";
import { useAppState } from "../../../context/AppStateContext";

const Ping = () => {

    const appState = useAppState();

    return (
        <div className="ping-container">
            {
                appState.stormStatus != "Paused" ? (
                    <div>
                        <div className="red-circle-for-ping" />
                        <div className="ping" />
                    </div>
                ) : (
                    <div className="yellow-circle" />
                )
            }
        </div>
    );
}

export default Ping;