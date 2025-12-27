from typing import Any
from json import loads
from asyncio import to_thread

from ...utils.SystemInfoEmitter import get_system_metrics
from ...settings import settings


async def get_system_metrics_resource() -> dict[str, Any]:
    """
    Get real-time system usage metrics as JSON.
    
    Returns:
        JSON string containing:
        - cpu_percent: Current CPU usage percentage
        - ram_percent: Current RAM usage percentage
        - used_ram_gb: Used RAM in GB
        - free_ram_percent: Free RAM percentage
        - free_ram_gb: Free RAM in GB
        - free_ram_mb: Free RAM in MB
    """
    # get_system_metrics uses psutil which is blocking
    return await to_thread(get_system_metrics)


async def get_system_settings() -> dict[str, Any]:
    """
    Get current application settings as JSON.
    
    Returns:
        JSON containing all application settings from the
        Pydantic Settings model (version, env, host, port, os,
        app_data_dir, and any other configured settings).
    """

    settings_ = settings.model_copy()
    settings_.ai.providers.anthropic.apiKey = "<REDACTED>"
    settings_.ai.providers.openai.apiKey = "<REDACTED>"
    settings_.ai.providers.google.apiKey = "<REDACTED>"
    settings_.saved_settings.ai.providers.anthropic.apiKey = "<REDACTED>"
    settings_.saved_settings.ai.providers.openai.apiKey = "<REDACTED>"
    settings_.saved_settings.ai.providers.google.apiKey = "<REDACTED>"
    final_settings = loads(settings_.model_dump_json())

    return final_settings


__all__: list[str] = [
    "get_system_metrics_resource",
    "get_system_settings"
]
