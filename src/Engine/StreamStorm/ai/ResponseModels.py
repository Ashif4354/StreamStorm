"""
Response Models for AI-generated outputs.

This module contains Pydantic models used to structure and validate
the outputs from AI generation tasks. These models ensure consistent
data structures for message generation and channel naming.
"""

from pydantic import BaseModel, Field


class GeneratedMessages(BaseModel):
    """
    Pydantic model for AI-generated message responses.
    
    This model ensures that the AI returns a properly structured
    list of messages that can be directly used by StreamStorm.
    """
    messages: list[str] = Field(
        ...,
        description="List of generated messages for chat spam",
        min_length=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    "Great stream! 🎮",
                    "Love the content!",
                    "This is amazing!",
                    "Keep it up! 💪",
                    "Best streamer ever!"
                ]
            }
        }


class GeneratedChannelNames(BaseModel):
    """
    Pydantic model for AI-generated channel name suggestions.
    
    Each channel name should be unique, memorable, and appropriate
    for a YouTube channel.
    """
    channel_names: list[str] = Field(
        ...,
        description="List of suggested YouTube channel names",
        min_length=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_names": [
                    "TechWizard Gaming",
                    "ProGamer Elite",
                    "StreamMaster 2000",
                    "Gaming Galaxy",
                    "Epic Play Zone"
                ]
            }
        }


class MessageGenerationPrompt(BaseModel):
    """
    Helper model for constructing message generation prompts.
    Contains the system prompt and user context.
    """
    context: str = Field(
        ...,
        description="Context or theme for message generation"
    )
    count: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of messages to generate"
    )
    style: str = Field(
        default="casual",
        description="Style of messages (casual, enthusiastic, supportive, etc.)"
    )
    include_emojis: bool = Field(
        default=True,
        description="Whether to include emojis in messages"
    )


class ChannelNameGenerationPrompt(BaseModel):
    """
    Helper model for constructing channel name generation prompts.
    """
    topic: str = Field(
        ...,
        description="Topic or theme for channel names"
    )
    count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of channel names to generate"
    )
    style: str = Field(
        default="catchy",
        description="Style of names (catchy, professional, fun, etc.)"
    )


__all__: list[str] = [
    "GeneratedMessages",
    "GeneratedChannelNames",
    "MessageGenerationPrompt",
    "ChannelNameGenerationPrompt"
]
