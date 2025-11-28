import * as atatus from "atatus-spa"

const fetchConfig = async (appState) => {
    fetch(`${appState.hostAddress}/config`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        appState.setEngineVersion(data.version);
        appState.setLogFilePath(data.log_file_path);
    })
    .catch((error) => {
        atatus.notify(error, {}, ['status_fetch_error']);
    });
}


export default fetchConfig;