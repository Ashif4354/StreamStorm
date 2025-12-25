from typing import Any

from ...utils.SystemInfoEmitter import get_system_metrics
from ...settings import settings


def get_system_metrics_resource() -> str:
    """
    Get real-time system usage metrics as JSON.
    
    Returns:
        JSON string containing:
        - cpu_percent: Current CPU usage percentage
        - ram_percent: Current RAM usage percentage
        - ram_gb: Used RAM in GB
        - free_ram_percent: Free RAM percentage
        - free_ram_gb: Free RAM in GB
        - free_ram_mb: Free RAM in MB
    """
    return get_system_metrics()


def get_system_settings() -> str:
    """
    Get current application settings as JSON.
    
    Returns:
        JSON string containing all application settings from the
        Pydantic Settings model (version, env, host, port, os,
        app_data_dir, and any other configured settings).
    """
    return settings.model_dump_json(indent=4)


__all__: list[str] = [
    "get_system_metrics_resource",
    "get_system_settings"
]
