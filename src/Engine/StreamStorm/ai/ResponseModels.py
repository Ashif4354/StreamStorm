from pydantic import BaseModel,Field
from typing import List

class AIResponse(BaseModel):
    """
    A Pydantic model to structure generated messages.
    (Schema to be defined based on requirements)
    """
    values: List[str] = Field(..., description="List of generated messages", min_length=1)
    

