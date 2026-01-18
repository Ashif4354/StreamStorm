from typing import List

from pydantic import BaseModel, Field


class AIGeneratedMessages(BaseModel):
    """
    A Pydantic model to structure generated messages.
    (Schema to be defined based on requirements)
    """

    messages: List[str] = Field(..., description="List of generated messages")


class AIGeneratedChannels(BaseModel):
    """
    A Pydantic model to structure generated channels.
    (Schema to be defined based on requirements)
    """

    channel_names: List[str] = Field(..., description="List of generated channels")


__all__: list[str] = ["AIGeneratedMessages", "AIGeneratedChannels"]
