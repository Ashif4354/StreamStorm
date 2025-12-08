import * as atatus from "atatus-spa"

const fetchStatus = async (formControls) => {
    fetch(`${formControls.hostAddress}/engine-status`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        formControls.setStormInProgress(data.storm_in_progress);
        formControls.setEngineVersion(data.version);
    })
    .catch((error) => {
        atatus.notify(error, {}, ['status_fetch_error']);
    });
}


export default fetchStatus;