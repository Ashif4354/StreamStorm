"""
StreamStorm AI Module.

This module provides a modular and extensible AI engine for StreamStorm,
following the Abstract Factory Pattern for easy provider switching.

Supported Frameworks:
- PydanticAI: Uses pydantic-ai for structured outputs
- LangChain: Uses LangChain for flexible AI interactions

Supported Providers:
- OpenAI: GPT models (gpt-4o, gpt-4o-mini, etc.)
- Anthropic: Claude models (claude-3-opus, claude-3-sonnet, etc.)
- Google: Gemini models (gemini-1.5-pro, gemini-1.5-flash, etc.)
- Ollama: Local models (llama3, mistral, etc.)

Usage Example:
    from StreamStorm.ai import AIFactory
    
    # Create an AI service
    ai = AIFactory.create(
        framework="pydantic",
        provider="openai",
        model="gpt-4o-mini",
        api_key="sk-..."
    )
    
    # Generate messages
    messages = await ai.generate_messages(
        prompt="Generate fun comments for a gaming stream",
        count=10
    )
    
    # Generate channel names
    channel_names = await ai.generate_channel_names(
        topic="Tech and Gaming",
        count=5
    )
"""

# Base classes and exceptions
from .Base import (
    AIBase,
    ModelBase,
    AIServiceError,
    AIConfigurationError,
    AIGenerationError
)

# Response models
from .ResponseModels import (
    GeneratedMessages,
    GeneratedChannelNames,
    MessageGenerationPrompt,
    ChannelNameGenerationPrompt
)

# Main factory
from .AIFactory import (
    AIFactory,
    create_ai_service,
    FrameworkType,
    ProviderType
)

# Service implementations
from .PydanticAI import PydanticAIService
from .LangChain import LangChainService

# Model factories
from .PydanticAIModelFactory import (
    PydanticModelFactory,
    OpenAIModelFactory,
    AnthropicModelFactory,
    GoogleModelFactory,
    OllamaModelFactory
)

from .LangChainModelFactory import (
    LangChainModelFactory,
    LangChainOpenAIFactory,
    LangChainAnthropicFactory,
    LangChainGoogleFactory,
    LangChainOllamaFactory
)


__all__: list[str] = [
    # Base classes
    "AIBase",
    "ModelBase",
    "AIServiceError",
    "AIConfigurationError",
    "AIGenerationError",
    
    # Response models
    "GeneratedMessages",
    "GeneratedChannelNames",
    "MessageGenerationPrompt",
    "ChannelNameGenerationPrompt",
    
    # Main factory
    "AIFactory",
    "create_ai_service",
    "FrameworkType",
    "ProviderType",
    
    # Service implementations
    "PydanticAIService",
    "LangChainService",
    
    # PydanticAI factories
    "PydanticModelFactory",
    "OpenAIModelFactory",
    "AnthropicModelFactory", 
    "GoogleModelFactory",
    "OllamaModelFactory",
    
    # LangChain factories
    "LangChainModelFactory",
    "LangChainOpenAIFactory",
    "LangChainAnthropicFactory",
    "LangChainGoogleFactory",
    "LangChainOllamaFactory",
]
