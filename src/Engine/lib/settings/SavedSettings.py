
from typing import Optional

from pydantic import BaseModel, Field

# Default settings structure
"""
DEFAULT_SAVED_SETTINGS: dict = {
    "ai": {
        "providers": {
            "openai": {
                "apiKey": "",
                "model": "",
                "baseUrl": "https://api.openai.com/v1",
            },
            "anthropic": {
                "apiKey": "", 
                "model": "", 
                "baseUrl": None
            },
            "google": {
                "apiKey": "", 
                "model": "", 
                "baseUrl": None
            },
        },
        "defaultProvider": None,
        "defaultModel": None,
        "defaultBaseUrl": None,
    }
}
"""


class Provider(BaseModel):
    apiKey: str = ""
    model: str = ""
    baseUrl: Optional[str] = None


class AIProviders(BaseModel):
    openai: Provider = Field(
        default_factory=lambda: Provider(baseUrl="https://api.openai.com/v1")
    )
    anthropic: Provider = Field(default_factory=Provider)
    google: Provider = Field(default_factory=Provider)


class AISettings(BaseModel):
    providers: AIProviders = Field(default_factory=AIProviders)
    defaultProvider: Optional[str] = None
    defaultModel: Optional[str] = None
    defaultBaseUrl: Optional[str] = None


class SavedSettings(BaseModel):
    ai: AISettings = Field(default_factory=AISettings)


DEFAULT_SAVED_SETTINGS: dict = SavedSettings().model_dump()

__all__ = [
    "SavedSettings",
    "AISettings",
    "DEFAULT_SAVED_SETTINGS",
]