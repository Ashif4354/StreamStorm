from pydantic import BaseModel,Field
from typing import List

class Messages(BaseModel):
    """
    A Pydantic model to structure generated messages.
    (Schema to be defined based on requirements)
    """
    messages: List[str] = Field(..., description="List of generated messages", min_length=1)
    

class ChannelNames(BaseModel):
    """
    A Pydantic model to structure generated channel names.
    (Schema to be defined based on requirements)
    """
    channels: List[str] = Field(..., description="List of generated channel names", min_length=1)