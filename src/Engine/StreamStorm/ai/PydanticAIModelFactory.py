"""
PydanticAI Model Factory Module.

This module implements the Abstract Factory pattern for creating AI models
using the PydanticAI framework. Supports OpenAI, Anthropic, and Google providers.
"""

from typing import Any, Literal
from logging import getLogger, Logger

from .Base import ModelBase, AIConfigurationError


logger: Logger = getLogger(f"streamstorm.ai.{__name__}")


class OpenAIModelFactory(ModelBase):
    """
    Factory for creating OpenAI models using PydanticAI.
    
    Supports custom base URLs for OpenAI-compatible APIs.
    """
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create an OpenAI model instance.
        
        Args:
            model_name: OpenAI model name (e.g., 'gpt-4o-mini', 'gpt-4')
            api_key: OpenAI API key
            base_url: Optional custom base URL (for Azure, local models, etc.)
            
        Returns:
            Configured OpenAI model for PydanticAI
        """
        try:
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openai import OpenAIProvider
            
            logger.debug(f"Creating OpenAI model: {model_name}")
            
            # Create provider with optional custom base URL
            if base_url:
                logger.debug(f"Using custom base URL: {base_url}")
                provider = OpenAIProvider(
                    api_key=api_key,
                    base_url=base_url
                )
            else:
                provider = OpenAIProvider(api_key=api_key)
            
            model = OpenAIModel(model_name, provider=provider)
            logger.info(f"Successfully created OpenAI model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("pydantic-ai package not installed")
            raise AIConfigurationError(
                "pydantic-ai package is not installed. Install it with: pip install pydantic-ai",
                provider="openai",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create OpenAI model: {e}")
            raise AIConfigurationError(
                f"Failed to create OpenAI model: {str(e)}",
                provider="openai",
                original_error=e
            )


class AnthropicModelFactory(ModelBase):
    """
    Factory for creating Anthropic Claude models using PydanticAI.
    """
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create an Anthropic model instance.
        
        Args:
            model_name: Anthropic model name (e.g., 'claude-3-opus-20240229')
            api_key: Anthropic API key
            base_url: Not used for Anthropic, included for interface compatibility
            
        Returns:
            Configured Anthropic model for PydanticAI
        """
        try:
            from pydantic_ai.models.anthropic import AnthropicModel
            from pydantic_ai.providers.anthropic import AnthropicProvider
            
            logger.debug(f"Creating Anthropic model: {model_name}")
            
            provider = AnthropicProvider(api_key=api_key)
            model = AnthropicModel(model_name, provider=provider)
            
            logger.info(f"Successfully created Anthropic model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("pydantic-ai package not installed")
            raise AIConfigurationError(
                "pydantic-ai package is not installed. Install it with: pip install pydantic-ai[anthropic]",
                provider="anthropic",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create Anthropic model: {e}")
            raise AIConfigurationError(
                f"Failed to create Anthropic model: {str(e)}",
                provider="anthropic",
                original_error=e
            )


class GoogleModelFactory(ModelBase):
    """
    Factory for creating Google Gemini models using PydanticAI.
    """
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create a Google Gemini model instance.
        
        Args:
            model_name: Google model name (e.g., 'gemini-1.5-pro', 'gemini-1.5-flash')
            api_key: Google API key
            base_url: Not used for Google, included for interface compatibility
            
        Returns:
            Configured Google model for PydanticAI
        """
        try:
            from pydantic_ai.models.gemini import GeminiModel
            from pydantic_ai.providers.google_gla import GoogleGLAProvider
            
            logger.debug(f"Creating Google Gemini model: {model_name}")
            
            provider = GoogleGLAProvider(api_key=api_key)
            model = GeminiModel(model_name, provider=provider)
            
            logger.info(f"Successfully created Google model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("pydantic-ai package not installed")
            raise AIConfigurationError(
                "pydantic-ai package is not installed. Install it with: pip install pydantic-ai[google]",
                provider="google",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create Google model: {e}")
            raise AIConfigurationError(
                f"Failed to create Google model: {str(e)}",
                provider="google",
                original_error=e
            )


class OllamaModelFactory(ModelBase):
    """
    Factory for creating Ollama (local) models using PydanticAI.
    
    Ollama uses OpenAI-compatible API, so we leverage OpenAI model with custom base URL.
    """
    
    def __init__(self, default_base_url: str = "http://localhost:11434/v1"):
        self.default_base_url = default_base_url
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str = "ollama",  # Ollama doesn't require API key
        base_url: str | None = None
    ) -> Any:
        """
        Create an Ollama model instance.
        
        Args:
            model_name: Ollama model name (e.g., 'llama3', 'mistral', 'codellama')
            api_key: Not required for Ollama, defaults to 'ollama'
            base_url: Ollama API base URL (defaults to localhost:11434)
            
        Returns:
            Configured Ollama model (via OpenAI compatibility)
        """
        try:
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openai import OpenAIProvider
            
            effective_base_url = base_url or self.default_base_url
            logger.debug(f"Creating Ollama model: {model_name} at {effective_base_url}")
            
            provider = OpenAIProvider(
                api_key=api_key or "ollama",
                base_url=effective_base_url
            )
            model = OpenAIModel(model_name, provider=provider)
            
            logger.info(f"Successfully created Ollama model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("pydantic-ai package not installed")
            raise AIConfigurationError(
                "pydantic-ai package is not installed",
                provider="ollama",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create Ollama model: {e}")
            raise AIConfigurationError(
                f"Failed to create Ollama model: {str(e)}",
                provider="ollama",
                original_error=e
            )


# Type alias for supported PydanticAI providers
PydanticAIProviderType = Literal["openai", "anthropic", "google", "ollama"]


class PydanticModelFactory:
    """
    Main factory class for creating PydanticAI models.
    
    Uses the correct provider factory based on the provider name.
    """
    
    _factories: dict[str, ModelBase] = {
        "openai": OpenAIModelFactory(),
        "anthropic": AnthropicModelFactory(),
        "google": GoogleModelFactory(),
        "ollama": OllamaModelFactory(),
    }
    
    @classmethod
    def get_model(
        cls,
        provider_name: PydanticAIProviderType,
        model_name: str,
        api_key: str,
        base_url: str | None = None
    ) -> Any:
        """
        Get a model instance for the specified provider.
        
        Args:
            provider_name: Name of the AI provider ('openai', 'anthropic', 'google', 'ollama')
            model_name: Name of the model to create
            api_key: API key for the provider
            base_url: Optional custom base URL
            
        Returns:
            Configured model instance
            
        Raises:
            AIConfigurationError: If provider is not supported or configuration fails
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._factories:
            supported = ", ".join(cls._factories.keys())
            raise AIConfigurationError(
                f"Unsupported provider: {provider_name}. Supported providers: {supported}",
                provider=provider_name
            )
        
        factory = cls._factories[provider_name]
        return factory.create_model(model_name, api_key, base_url)
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Return list of supported provider names."""
        return list(cls._factories.keys())


__all__: list[str] = [
    "OpenAIModelFactory",
    "AnthropicModelFactory",
    "GoogleModelFactory",
    "OllamaModelFactory",
    "PydanticModelFactory",
    "PydanticAIProviderType"
]
