from os import environ
from os.path import join, exists
from json import load
from typing import Optional
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from psutil import virtual_memory
from platformdirs import user_data_dir
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from waitress import serve

# from multiprocessing import Manager
# from multiprocessing.managers import SyncManager

from lib.StreamStorm import StreamStorm
from lib.Profiles import Profiles
from Engine.StreamStorm.api.Validation import (
    Validate,
    StormData,
    ProfileData,
    ChangeMessagesData,
    ChangeSlowModeData,
    StartMoreChannelsData,
    GetChannelsData,
)


app: Flask = Flask(__name__)
CORS(app)

# manager: SyncManager = Manager()
# shared_data: dict = manager.dict()

storm_controls_endpoints: list[str] = [
    "/pause",
    "/resume",
    "/change_messages",
    "/start_storm_dont_wait",
    "/change_slow_mode",
    "/start_more_channels",
]


@app.before_request
def before_request() -> Optional[Response]:
    if request.method == "POST":
        if request.path in (
            "/storm",
            "/create_profiles",
            "/delete_all_profiles",
        ):
            if environ.get("BUSY") == "1":
                return jsonify(
                    {
                        "success": False,
                        "message": f"Engine is Busy: {environ['BUSY_REASON']}",
                    }
                )

        if request.path in storm_controls_endpoints:
            if StreamStorm.ss_instance is None:
                return jsonify(
                    {
                        "success": False,
                        "message": "No storm is running. Start a storm first.",
                    }
                )

    if request.method == "GET":
        if request.path in storm_controls_endpoints:
            if StreamStorm.ss_instance is None:
                return jsonify(
                    {
                        "success": False,
                        "message": "No storm is running. Start a storm first.",
                    }
                )


@app.route("/storm", methods=["POST"])
def storm() -> Response:
    if StreamStorm.ss_instance is not None:
        return jsonify(
            {
                "success": False,
                "message": "A storm is already running. Stop the current storm before starting a new one.",
            }
        )

    StreamStorm.each_channel_instances = []

    try:
        validated_data: dict = Validate(request.json, StormData)

        StreamStormObj: StreamStorm = StreamStorm(
            validated_data["video_url"],
            validated_data["chat_url"],
            validated_data["messages"],
            (validated_data["subscribe"], validated_data["subscribe_and_wait"]),
            validated_data["subscribe_and_wait_time"],
            validated_data["slow_mode"],
            validated_data["channels"],
            validated_data["browser"],
            validated_data["background"],
        )

        StreamStormObj.ready_event.clear()  # Clear the ready event to ensure it will be only set when all instances are ready
        StreamStormObj.pause_event.set()  # Set the pause event to allow storming to start immediately

        environ.update({"BUSY": "1", "BUSY_REASON": "Storming in progress"})

        StreamStormObj.start()

        return jsonify({"success": True, "message": "Started"})

    except Exception as e:
        environ.update({"BUSY": "0"})
        return jsonify({"success": False, "message": str(e)})


@app.route("/stop", methods=["POST"])
def stop() -> Response:
    def close_browser(instance: StreamStorm) -> None:
        try:
            if instance.driver:
                instance.driver.close()
        except Exception:
            pass

    with ThreadPoolExecutor() as executor:
        executor.map(close_browser, StreamStorm.each_channel_instances)

    StreamStorm.ss_instance = None

    try:
        StreamStorm.ss_instance.pause_event.set()  # Ensure the pause event is set to allow next storms
    except Exception as _:
        pass

    environ.update({"BUSY": "0"})

    return jsonify({"success": True, "message": "Stopped"})


@app.route("/pause", methods=["POST"])
def pause() -> Response:
    StreamStorm.ss_instance.pause_event.clear()  # Clear the pause event to pause storming

    return jsonify({"success": True, "message": "Paused"})


@app.route("/resume", methods=["POST"])
def resume() -> Response:
    StreamStorm.ss_instance.pause_event.set()  # Set the pause event to resume storming

    return jsonify({"success": True, "message": "Resumed"})


@app.route("/change_messages", methods=["POST"])
def change_messages() -> Response:
    try:
        validated_data: dict = Validate(request.json, ChangeMessagesData)

        StreamStorm.ss_instance.messages = validated_data["messages"]

        return jsonify({"success": True, "message": "Messages changed successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/start_storm_dont_wait", methods=["POST"])
def start_storm_dont_wait() -> Response:
    StreamStorm.ss_instance.ready_event.set()  # Set the event to signal that don't wait for the remaining instances to be ready, and start storming immediately.

    return jsonify(
        {
            "success": True,
            "message": "Storm started without waiting for all instances to be ready",
        }
    )


@app.route("/change_slow_mode", methods=["POST"])
def change_slow_mode() -> Response:
    try:
        validated_data: dict = Validate(request.json, ChangeSlowModeData)

        if not StreamStorm.ss_instance.ready_event.is_set():
            return jsonify(
                {
                    "success": False,
                    "message": "Cannot change slow mode before the storm starts",
                }
            )

        StreamStorm.ss_instance.slow_mode = validated_data["slow_mode"]

        return jsonify({"success": True, "message": "Slow mode changed successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/start_more_channels", methods=["POST"])
def start_more_channels() -> Response:
    
    if not StreamStorm.ss_instance.ready_event.is_set():
        return jsonify(
            {
                "success": False,
                "message": "Cannot start more channels before the storm starts",
            }
        )

    try:
        validated_data: dict = Validate(request.json, StartMoreChannelsData)
        StreamStorm.ss_instance.start_more_channels(validated_data["channels"])

        return jsonify(
            {"success": True, "message": "Started more channels successfully"}
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/get_channels_data", methods=["POST"])
def get_channels_data() -> Response:
    # channels: dict[str, dict[str, str]] = StreamStorm.ss_instance.all_channels    
    
    try:
        validated_data: dict = Validate(request.json, GetChannelsData)
        
        mode: str = validated_data["mode"]
        
        if mode == "add" and StreamStorm.ss_instance is None:
            return jsonify(
                {
                    "success": False,
                    "message": "No storm is running. Start a storm first.",
                }
            )
            
        browser_dir: str = validated_data["browser"]
        
        app_data_dir: str = user_data_dir("StreamStorm", "DarkGlance")
        config_json_path: str = join(app_data_dir, browser_dir, "config.json")

        if not exists(config_json_path):
            return jsonify(
                {"success": False, "message": "Configuration file not found, create profiles first"}
            )

        with open(config_json_path, "r") as file:
            data: dict = load(file)
        
        response_data: dict = {}
        
        if mode == "new":
            response_data["channels"] = data["channels"]
            response_data["activeChannels"] = []

        elif mode == "add":
            active_channels: list[str] = StreamStorm.ss_instance.get_active_channels()
            
            response_data["channels"] = data["channels"]
            response_data["activeChannels"] = active_channels
            
        response_data.update({"success": True})

        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})



@app.route("/create_profiles", methods=["POST"])
def create_profiles() -> Response:
    try:
        environ.update({"BUSY": "1", "BUSY_REASON": "Creating profiles"})

        validated_data: dict = Validate(request.json, ProfileData)

        profiles: Profiles = Profiles(validated_data["browser_class"])
        profiles.create_profiles(validated_data["count"])

        return jsonify({"success": True, "message": "Profiles created"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        environ.update({"BUSY": "0"})


@app.route("/delete_all_profiles", methods=["POST"])
def delete_all_profiles() -> Response:
    try:
        environ.update({"BUSY": "1", "BUSY_REASON": "Deleting profiles"})

        validated_data: dict = Validate(request.json, ProfileData)

        profiles: Profiles = Profiles(validated_data["browser_class"])
        profiles.delete_all_temp_profiles()

        return jsonify({"success": True, "message": "Profiles deleted"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        environ.update({"BUSY": "0"})


@app.route("/get_ram_info", methods=["GET"])
def get_ram_info() -> Response:
    return jsonify(
        {
            "free": virtual_memory().available / (1024**3),
            "total": virtual_memory().total / (1024**3),
        }
    )


def serve_flask_app() -> None:
    """
    Run the Flask application.
    This function is used to run the Flask app in a separate thread.
    """
    serve(app, host="0.0.0.0", port=5000)


def run_flask_app() -> None:
    """
    Run the Flask application.
    This function is used to run the Flask app in a separate thread.
    """
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    from dgupdater import check_update

    check_update()
    from os import kill, getpid
    from signal import SIGTERM
    from os.path import dirname, abspath, join
    from webview import create_window, start

    environ["rammap_path"] = join(dirname(abspath(__file__)), "RAMMap.exe")

    Thread(target=serve_flask_app, daemon=True).start()
    # run_flask_app()

    try:
        create_window(
            title="StreamStorm",
            url="https://streamstorm-ui.web.app/",
            width=1300,
            height=900,
            confirm_close=True,
        )

        start()
    finally:
        # Ensure the Flask app is stopped when the webview is closed
        kill(getpid(), SIGTERM)
