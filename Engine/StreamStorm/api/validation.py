from typing import Self, Optional
from warnings import deprecated
from pydantic import BaseModel, field_validator, model_validator, StrictInt
from logging import getLogger, Logger

logger: Logger = getLogger("fastapi." + __name__)

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
        raise Exception(f"Error in {errors[0]['loc'][0]} : {errors[0]['msg']}")

class StormData(BaseModel):
    video_url: str
    chat_url: str
    messages: list[str]
    subscribe: bool
    subscribe_and_wait: bool
    subscribe_and_wait_time: int
    slow_mode: int
    channels: list[int]
    background: bool

    @field_validator("video_url")
    def validate_video_url(cls, value: str) -> str:
        if not value.startswith("https://www.youtube.com/watch?v="):
            raise ValueError("Invalid video url")
        
        if value.split("https://www.youtube.com/watch?v=")[1] == "":
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
        
        value = [ msg.strip('"[],') for msg in value ]
        
        return value

    @field_validator("subscribe_and_wait_time")
    def validate_subscribe_and_wait_time(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Subscribe and wait time cannot be negative")
        
        return value

    @field_validator("slow_mode")
    def validate_slow_mode(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Slow mode cannot be negative")
        
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
    
    @model_validator(mode = 'before')
    def before_validator(self) -> Self:
        return self
    
    
    @model_validator(mode = 'after')
    def validate_data(self) -> Self:
        if self.video_url.replace("watch", "live_chat") != self.chat_url:
            raise ValueError("Invalid video URL")
        
        self.channels = list(set(self.channels)) # Remove duplicates
        
        return self


class ProfileData(BaseModel):
    count: StrictInt = 1
    
    @field_validator("count")
    def validate_count(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("count cannot be negative")
        
        return value
    
    
class ChangeMessagesData(BaseModel):
    messages: list[str]
    
    @field_validator("messages")
    def validate_messages(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Messages cannot be empty")
        
        value = [ msg.strip('"[],') for msg in value ]
        
        return value
    
class ChangeSlowModeData(BaseModel):
    slow_mode: int
    
    @field_validator("slow_mode")
    def validate_slow_mode(cls, value: int) -> int:
        if not isinstance(value, int):
            raise ValueError("Slow mode must be an integer")
        
        if value < 1:
            raise ValueError("Slow mode must be at least 1")

        return value

class StartMoreChannelsData(BaseModel):
    channels: list[int]

    @field_validator("channels")
    def validate_channels(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("Channels cannot be empty")

        return value
    
    @model_validator(mode='after')
    def validate_data(self) -> Self:

        self.channels = list(set(self.channels)) # Remove duplicates
        return self
    
    
class GetChannelsData(BaseModel):
    mode: str

    @field_validator("mode")
    def validate_mode(cls, value: str) -> str:
        if value not in ["new", "add"]:
            raise ValueError("Invalid mode")
        
        return value
    
    
__all__ : list[str] = [
    "StormData",
    "ProfileData",
    "ChangeMessagesData",
    "ChangeSlowModeData",
    "StartMoreChannelsData",
    "GetChannelsData",
    "Validate"
]