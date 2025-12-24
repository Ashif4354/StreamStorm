import * as atatus from "atatus-spa"

const fetchConfig = async (appState) => {
    fetch(`${appState.hostAddress}/config`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            appState.setEngineVersion(data.version);
            appState.setLogFilePath(data.log_file_path);
        } else {
            console.error("Failed to fetch config:", data.message);
            atatus.notify(data.message, {}, ['config_fetch_failed']);
        }
    })
    .catch((error) => {
        atatus.notify(error, {}, ['config_fetch_error']);
    });
}


export default fetchConfig;