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
    
    video_url: str = Field(..., description="Video url", validation_alias=AliasChoices("video_url", "videoUrl"))
    chat_url: str = Field(... , description="Chat url", validation_alias=AliasChoices("chat_url", "chatUrl"))
    messages: list[str] = Field(..., description="Message list")
    subscribe: bool = Field(... , description="Subscribe flag")
    subscribe_and_wait: bool = Field(..., description="Subscribe and wait flag", validation_alias=AliasChoices("subscribe_and_wait", "subscribeAndWait"))
    subscribe_and_wait_time: StrictInt = Field(... , ge=0, description="Subscribe and wait time in seconds", validation_alias=AliasChoices("subscribe_and_wait_time", "subscribeAndWaitTime"))
    slow_mode: int = Field(... , ge=1, description="Slow mode time in seconds", validation_alias=AliasChoices("slow_mode", "slowMode"))
    channels: list[int] = Field(... , description="Channels")
    background: bool = Field(... , description="Background flag")

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
    count: StrictInt = Field(... , ge=1, description="Count must be an integer and at least 1")   
    
    
class ChangeMessagesData(BaseModel):
    messages: list[str] = Field(... , description="Message list")
    
    @field_validator("messages")
    def validate_messages(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Messages cannot be empty")
        
        value = [ msg.strip('"[],') for msg in value ]
        
        return value
    
class ChangeSlowModeData(BaseModel):
    slow_mode: int = Field(..., description="New slow mode value", ge=1, validation_alias=AliasChoices("slow_mode", "slowMode"))
    
    @field_validator("slow_mode")
    def validate_slow_mode(cls, value: int) -> int:
        
        if value < 1:
            raise ValueError("Slow mode must be at least 1")

        return value

class StartMoreChannelsData(BaseModel):
    channels: list[StrictInt] = Field(... , description="Channels")

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
    mode: str = Field(... , description="Mode")

    @field_validator("mode")
    def validate_mode(cls, value: str) -> str:
        if value not in {"new", "add"}:
            raise ValueError("Invalid mode")
        
        return value
    
class CreateChannelsData(BaseModel):
    channels: list[dict[str, str]] = Field(... , description="Channels data with name and logo uri")
    logo_needed: bool = Field(... , description="Logo needed flag", validation_alias=AliasChoices("logo_needed", "logoNeeded"))
    random_logo: bool = Field(... , description="Random logo flag", validation_alias=AliasChoices("random_logo", "randomLogo"))
    
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
    directory: str = Field(... , description="Directory")
    
    @field_validator("directory")
    def validate_directory(cls, value: str) -> str:
        path = Path(value)
        
        try:
            path.resolve(strict=True)
            return value
        
        except Exception as e:
            raise ValueError("Invalid directory") from e
        
        
    
__all__ : list[str] = [
    "StormData",
    "ProfileData",
    "ChangeMessagesData",
    "ChangeSlowModeData",
    "StartMoreChannelsData",
    "GetChannelsData",
    "CreateChannelsData",
    "VerifyChannelsDirectoryData",
    "Validate"
]