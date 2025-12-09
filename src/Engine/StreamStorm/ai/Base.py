"""
Base module defining abstract interfaces for the AI system.

This module contains the abstract base classes that define the contracts
for all AI provider implementations and model factories.
"""

from abc import ABC, abstractmethod
from typing import Any
from logging import getLogger, Logger


logger: Logger = getLogger(f"streamstorm.ai.{__name__}")


class AIBase(ABC):
    """
    Abstract base class for AI provider implementations.
    
    All AI service implementations (PydanticAI, LangChain, etc.) must inherit
    from this class and implement all abstract methods.
    """
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Any:
        """
        Main generation method for raw AI output.
        
        Args:
            prompt: The input prompt for the AI model
            **kwargs: Additional arguments for the generation
            
        Returns:
            The raw AI response
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    @abstractmethod
    async def generate_messages(self, prompt: str, count: int = 10) -> list[str]:
        """
        Generate a list of messages based on the prompt.
        
        This method is specifically designed for generating chat messages
        that can be used in StreamStorm's spam functionality.
        
        Args:
            prompt: Description or context for the type of messages to generate
            count: Number of messages to generate (default: 10)
            
        Returns:
            A list of generated message strings
        """
        raise NotImplementedError("Subclasses must implement generate_messages()")
    
    @abstractmethod
    async def generate_channel_names(self, topic: str, count: int = 5) -> list[str]:
        """
        Generate YouTube channel name suggestions based on a topic.
        
        Args:
            topic: The topic or theme for channel names
            count: Number of channel names to generate (default: 5)
            
        Returns:
            A list of suggested channel names
        """
        raise NotImplementedError("Subclasses must implement generate_channel_names()")


class ModelBase(ABC):
    """
    Abstract factory interface for creating AI model instances.
    
    Each AI provider (OpenAI, Anthropic, Google) should have its own
    ModelBase implementation that knows how to create model instances
    for that specific provider.
    """
    
    @abstractmethod
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create and return an AI model instance.
        
        Args:
            model_name: The name/identifier of the model to create
            api_key: API key for authentication
            base_url: Optional custom base URL for the API endpoint
            
        Returns:
            A configured model instance ready for use
        """
        raise NotImplementedError("Subclasses must implement create_model()")


class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    
    def __init__(self, message: str, provider: str | None = None, original_error: Exception | None = None):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.provider:
            return f"[{self.provider}] {self.message}"
        return self.message


class AIConfigurationError(AIServiceError):
    """Exception raised when AI service is not properly configured."""
    pass


class AIGenerationError(AIServiceError):
    """Exception raised when AI generation fails."""
    pass


__all__: list[str] = [
    "AIBase",
    "ModelBase", 
    "AIServiceError",
    "AIConfigurationError",
    "AIGenerationError"
]
