from typing import Self
from pathlib import Path
from warnings import deprecated
from pydantic import BaseModel, ConfigDict, field_validator, model_validator, StrictInt, Field, AliasChoices
from logging import getLogger, Logger

logger: Logger = getLogger(f"fastapi.{__name__}")

@deprecated("Not used anymore since migrated to FastAPI")
def Validate(data: dict, validator: BaseModel) -> dict:
    try:
        validated_data = validator(**data)
        return validated_data.model_dump()
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        errors: list = e.errors()
        if "ctx" in errors[0]:
            del errors[0]["ctx"]
        raise ValueError(f"Error in {errors[0]['loc'][0]} : {errors[0]['msg']}") from e

class StormData(BaseModel):
    
    model_config = ConfigDict(strict=True) 
    
    video_url: str = Field(
        ...,
        description="The YouTube video URL where the live chat storm will be performed. Must be in format 'https://www.youtube.com/watch?v=VIDEO_ID'. Required to identify the target live stream.",
        validation_alias=AliasChoices("video_url", "videoUrl")
    )
    chat_url: str = Field(
        ...,
        description="The YouTube live chat URL corresponding to the video. Must be in format 'https://www.youtube.com/live_chat?v=VIDEO_ID'. Must match the video_url's video ID.",
        validation_alias=AliasChoices("chat_url", "chatUrl")
    )
    messages: list[str] = Field(
        ...,
        description="List of messages to send in the YouTube live chat. Provide at least one message. Messages will be sent in rotation across all channels. Format: ['message1', 'message2', ...]."
    )
    subscribe: bool = Field(
        ...,
        description="Whether to subscribe to the channel before sending messages. Set to true if you want each profile to subscribe to the channel first. This is required only if some youtube channels need a subscription to allow sending messages in their live chat."
    )
    subscribe_and_wait: bool = Field(
        ...,
        description="Whether to wait after subscribing before starting to storm. Only applies if 'subscribe' is true. Set to true for a more natural behavior. This is required only if some youtube channels need a subscription and also wait for the given time before sending messages in their live chat.",
        validation_alias=AliasChoices("subscribe_and_wait", "subscribeAndWait")
    )
    subscribe_and_wait_time: StrictInt = Field(
        ...,
        ge=0,
        description="Time in seconds to wait after subscribing before starting to storm. Must be 0 or greater. Only applies if 'subscribe_and_wait' is true.",
        validation_alias=AliasChoices("subscribe_and_wait_time", "subscribeAndWaitTime")
    )
    slow_mode: int = Field(
        ...,
        ge=1,
        description="Delay in seconds between messages sent by each channel. Must be at least 1 second. Higher values reduce message rate but help avoid detection. Recommended: match YouTube's slow mode setting.",
        validation_alias=AliasChoices("slow_mode", "slowMode")
    )
    channels: list[int] = Field(
        ...,
        description="List of channel IDs (indices) to use for storming. Each ID refers to a pre-created YouTube channel profile. Format: [1, 2, 3, ...]. All IDs must be positive integers."
    )
    background: bool = Field(
        ...,
        description="Whether to run browser instances in headless/background mode. Set to true for invisible operation, false to see browser windows for debugging. Default: false",
    )

    @field_validator("video_url")
    def validate_video_url(cls, value: str) -> str:
        if not value.startswith("https://www.youtube.com/watch?v="):
            raise ValueError("Invalid video url")
        
        if " " in value:
            raise ValueError("Invalid video url")
                
        video_id: str = value.split("https://www.youtube.com/watch?v=")[1]
        video_id = video_id.split("&")[0]
        video_id = video_id.strip("/")
        
        if video_id == "":
            raise ValueError("Invalid video url")
        
        if len(video_id) != 11:
            raise ValueError("Invalid video url")
        
        return value

    @field_validator("chat_url")
    def validate_chat_url(cls, value: str) -> str:
        if not value.startswith("https://www.youtube.com/live_chat?v="):
            raise ValueError("Invalid chat url")
        
        return value
        
        
    @field_validator("messages")
    def validate_messages(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Messages cannot be empty")
        
        value = [ msg.strip('"\'[],') for msg in value ]
        
        return value


    
    @field_validator("channels")
    def validate_channels(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("Channels cannot be empty")
        
        if not all(isinstance(channel, int) for channel in value):
            raise ValueError("All channels must be integers")
        
        if any(channel <= 0 for channel in value):
            raise ValueError("Channel IDs must be positive integers")

        return value
    
    
    @model_validator(mode = 'after')
    def validate_data(self) -> Self:
        if self.video_url.replace("watch", "live_chat") != self.chat_url:
            raise ValueError("Invalid Video/Chat URL")
        
        self.channels = list(set(self.channels)) # Remove duplicates
        
        return self


class ProfileData(BaseModel):
    count: StrictInt = Field(
        ...,
        ge=1,
        description="Number of Chromium browser profiles to create. Must be a positive integer (1 or greater). Each profile represents a separate YouTube account that can be used for storming."
    )   
    
    
class ChangeMessagesData(BaseModel):
    messages: list[str] = Field(
        ...,
        description="New list of messages to use for the ongoing storm. Replaces the current message pool. Provide at least one message. Format: ['message1', 'message2', ...]. Messages will be sent in rotation."
    )
    
    @field_validator("messages")
    def validate_messages(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Messages cannot be empty")
        
        value = [ msg.strip('"[],') for msg in value ]
        
        return value
    
class ChangeSlowModeData(BaseModel):
    slow_mode: int = Field(
        ...,
        ge=1,
        description="New delay in seconds between messages for the ongoing storm. Must be at least 1 second. Adjusts the messages rate without restarting the storm. Lower values = faster rate, higher values = safer.",
        validation_alias=AliasChoices("slow_mode", "slowMode")
    )
    
    @field_validator("slow_mode")
    def validate_slow_mode(cls, value: int) -> int:
        
        if value < 1:
            raise ValueError("Slow mode must be at least 1")

        return value

class StartMoreChannelsData(BaseModel):
    channels: list[StrictInt] = Field(
        ...,
        description="List of additional channel IDs to add to the running storm. Each ID refers to a pre-created YouTube channel profile. Format: [4, 5, 6, ...]. All IDs must be positive integers and not already in use."
    )

    @field_validator("channels")
    def validate_channels(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("Channels cannot be empty")
        
        if not all(isinstance(channel, int) for channel in value):
            raise ValueError("All channels must be integers")
        
        if any(channel <= 0 for channel in value):
            raise ValueError("Channel IDs must be positive integers")

        return value
    
    @model_validator(mode='after')
    def validate_data(self) -> Self:

        self.channels = list(set(self.channels)) # Remove duplicates
        return self
    
    
class GetChannelsData(BaseModel):
    mode: str = Field(
        ...,
        description="Mode for fetching channel data. Use 'new' when starting a fresh storm (returns all available channels). Use 'add' when adding channels to an existing storm (returns available channels excluding active ones)."
    )

    @field_validator("mode")
    def validate_mode(cls, value: str) -> str:
        if value not in {"new", "add"}:
            raise ValueError("Invalid mode")
        
        return value
    
class CreateChannelsData(BaseModel):
    channels: list[dict[str, str]] = Field(
        ...,
        description="List of channel configurations to create. Each item must be an object with 'name' (channel name string) and 'uri' (path to logo image file). Format: [{'name': 'ChannelName', 'uri': '/path/to/logo.png'}, ...]. URI is required if logo_needed=true and random_logo=false."
    )
    logo_needed: bool = Field(
        ...,
        description="Whether to set profile pictures for the channels. Set to true to add logos, false to skip logo setup. Required for realistic-looking profiles.",
        validation_alias=AliasChoices("logo_needed", "logoNeeded")
    )
    random_logo: bool = Field(
        ...,
        description="Whether to use randomly generated logos instead of provided URIs. Only applies if logo_needed=true. Set to true for auto-generated logos, false to use the URIs provided in channels list.",
        validation_alias=AliasChoices("random_logo", "randomLogo")
    )
    
    @field_validator("channels")
    def validate_channels(cls, value: list) -> list[dict[str, str]]:
        if not value:
            raise ValueError("Channels cannot be empty")
        
        if not all(isinstance(channel, dict) for channel in value):
            raise ValueError("All channels must be a JS object")
        
        if any("name" not in channel or "uri" not in channel for channel in value):
            raise ValueError("All channels must have a name and logo")
        
        if any(channel["name"] == "" for channel in value):
            raise ValueError("All channels must have a name")
        
        return value
        
    @model_validator(mode='after')
    def validate_data(self) -> list[dict[str, str]]:  
        
        if self.logo_needed and not self.random_logo:
            if any(channel["uri"] == "" for channel in self.channels):
                raise ValueError("All channels must have a logo uri, since you have set Logo is needed")
            
            new_value: list = []
            
            for channel in self.channels:
                try:
                    path: Path = Path(channel["uri"]).resolve(strict=True)
                    new_value.append({"name": channel["name"], "uri": str(path)})
                    
                except FileNotFoundError as e:
                    logger.error(f"Logo file not found for {channel['name']}")
                    raise ValueError(f"Logo file not found for {channel['name']}") from e
                
                except Exception as e:
                    logger.error(f"Unexpected error while finding logo file: {e}")
                    raise ValueError(f"Logo file not found for {channel['name']}") from e
        
        
            self.channels = new_value
        
        return self
    

class VerifyChannelsDirectoryData(BaseModel):
    directory: str = Field(
        ...,
        description="Absolute path to a directory containing channel logo images. Directory must exist and contain only image files (PNG, JPG, JPEG). Each filename (without extension) will be used as the channel name. Format: 'C:/path/to/logos' or '/path/to/logos' (Follow OS specific path format supported by python)."
    )
    
    @field_validator("directory")
    def validate_directory(cls, value: str) -> str:
        path = Path(value)
        
        try:
            path.resolve(strict=True)
            return value
        
        except Exception as e:
            raise ValueError("Invalid directory") from e
        
        
class KillInstanceData(BaseModel):
    index: StrictInt = Field(
        ...,
        ge=0,
        description="Index of the storm instance to kill. Must be a non-negative integer matching an active instance. This is the same index used when the channel was started."
    )
    name: str = Field(
        ...,
        description="Name of the channel being killed. Used for logging and identification purposes. Should match the channel name associated with the instance index."
    )

class AIProviderKeyData(BaseModel):
    """Model for saving a single AI provider's configuration"""
    model_config = ConfigDict(strict=True)
    
    api_key: str = Field(
        ...,
        min_length=10,
        description="API key for authenticating with the AI provider. Must be at least 10 characters. Obtain from provider's dashboard. Required for AI message generation.",
        validation_alias=AliasChoices("api_key", "apiKey")
    )
    model: str = Field(
        ...,
        min_length=1,
        description="Name of the AI model to use for generation. Format depends on provider. Check provider documentation for available models."
    )
    base_url: str | None = Field(
        None,
        description="Optional custom base URL for API requests. Use for self-hosted models or API proxies. Must start with 'http://' or 'https://'. Leave empty/null for default provider URLs.",
        validation_alias=AliasChoices("base_url", "baseUrl")
    )
    
    @field_validator("api_key")
    def validate_api_key(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("API key cannot be empty")
        if len(value.strip()) < 10:
            raise ValueError("API key must be at least 10 characters")
        return value.strip()
    
    @field_validator("model")
    def validate_model(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("Model cannot be empty")
        return value.strip()
    
    @field_validator("base_url")
    def validate_base_url(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        # Basic URL validation
        if not value.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return value.strip()


class SetDefaultProviderData(BaseModel):
    """Model for setting the default AI provider with apiKey, model and optional baseUrl."""
    provider: str = Field(
        ...,
        description="ID of the AI provider to set as default. Must be one of: 'openai', 'anthropic', or 'google'. This provider will be used for all AI message and channel name generation."
    )
    api_key: str = Field(
        ...,
        min_length=10,
        description="API key for the selected provider. Must be at least 10 characters. Required for authentication. The key will be stored securely for future use.",
        validation_alias=AliasChoices("api_key", "apiKey")
    )
    model: str = Field(
        ...,
        min_length=1,
        description="Model name to use as default for AI generation. Must be a valid model for the selected provider."
    )
    base_url: str | None = Field(
        None,
        description="Optional custom API endpoint URL. Use for proxies or self-hosted models. Must start with 'http://' or 'https://'. Set to null to use the provider's default endpoint.",
        validation_alias=AliasChoices("base_url", "baseUrl")
    )
    
    @field_validator("provider")
    def validate_provider(cls, value: str) -> str:
        valid_providers = {"openai", "anthropic", "google"}
        if value not in valid_providers:
            raise ValueError(f"Provider must be one of: {', '.join(valid_providers)}")
        return value
    
    @field_validator("api_key")
    def validate_api_key(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("API key cannot be empty")
        if len(value.strip()) < 10:
            raise ValueError("API key must be at least 10 characters")
        return value.strip()
    
    @field_validator("model")
    def validate_model(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("Model cannot be empty")
        return value.strip()
    
    @field_validator("base_url")
    def validate_base_url(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return value.strip()


class GenerateMessagesRequest(BaseModel):
    """Model for AI message generation request"""
    prompt: str = Field(
        ...,
        min_length=1,
        description="Natural language prompt describing what messages or channel names to generate. Be specific about the topic, tone, quantity, and style. Example: 'Generate 10 enthusiastic messages about a gaming stream' or 'Create 5 tech-related YouTube channel names'."
    )
    
    @field_validator("prompt")
    def validate_prompt(cls, value: str) -> str:
        if not value or value.strip() == "":
            raise ValueError("Prompt cannot be empty")
        return value.strip()


class GeneralSettingsData(BaseModel):
    """Model for updating general application settings"""
    login_method: str = Field(
        ...,
        description="Login method to use - 'cookies' (faster, lower disk usage) or 'profiles' (persistent sessions, more disk space)"
    )
    
    @field_validator("login_method")
    def validate_login_method(cls, value: str) -> str:
        if value not in {"cookies", "profiles"}:
            raise ValueError("login_method must be 'cookies' or 'profiles'")
        return value


__all__ : list[str] = [
    "StormData",
    "ProfileData",
    "ChangeMessagesData",
    "ChangeSlowModeData",
    "StartMoreChannelsData",
    "GetChannelsData",
    "CreateChannelsData",
    "VerifyChannelsDirectoryData",
    "KillInstanceData",
    "AIProviderKeyData",
    "SetDefaultProviderData",
    "GenerateMessagesRequest",
    "GeneralSettingsData",
    "Validate"
]