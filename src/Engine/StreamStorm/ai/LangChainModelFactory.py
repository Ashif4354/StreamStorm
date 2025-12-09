"""
LangChain Model Factory Module.

This module implements the Abstract Factory pattern for creating AI models
using the LangChain framework. Supports OpenAI, Anthropic, and Google providers.
"""

from typing import Any, Literal
from logging import getLogger, Logger

from .Base import ModelBase, AIConfigurationError


logger: Logger = getLogger(f"streamstorm.ai.{__name__}")


class LangChainOpenAIFactory(ModelBase):
    """
    Factory for creating OpenAI models using LangChain.
    """
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create a LangChain ChatOpenAI model instance.
        
        Args:
            model_name: OpenAI model name (e.g., 'gpt-4o-mini', 'gpt-4')
            api_key: OpenAI API key
            base_url: Optional custom base URL
            
        Returns:
            Configured ChatOpenAI instance
        """
        try:
            from langchain_openai import ChatOpenAI
            
            logger.debug(f"Creating LangChain OpenAI model: {model_name}")
            
            kwargs = {
                "model": model_name,
                "api_key": api_key,
                "temperature": 0.7,
            }
            
            if base_url:
                kwargs["base_url"] = base_url
                logger.debug(f"Using custom base URL: {base_url}")
            
            model = ChatOpenAI(**kwargs)
            logger.info(f"Successfully created LangChain OpenAI model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("langchain-openai package not installed")
            raise AIConfigurationError(
                "langchain-openai package is not installed. Install it with: pip install langchain-openai",
                provider="openai",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create LangChain OpenAI model: {e}")
            raise AIConfigurationError(
                f"Failed to create LangChain OpenAI model: {str(e)}",
                provider="openai",
                original_error=e
            )


class LangChainAnthropicFactory(ModelBase):
    """
    Factory for creating Anthropic Claude models using LangChain.
    """
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create a LangChain ChatAnthropic model instance.
        
        Args:
            model_name: Anthropic model name (e.g., 'claude-3-opus-20240229')
            api_key: Anthropic API key
            base_url: Not used for Anthropic
            
        Returns:
            Configured ChatAnthropic instance
        """
        try:
            from langchain_anthropic import ChatAnthropic
            
            logger.debug(f"Creating LangChain Anthropic model: {model_name}")
            
            model = ChatAnthropic(
                model=model_name,
                api_key=api_key,
                temperature=0.7,
            )
            
            logger.info(f"Successfully created LangChain Anthropic model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("langchain-anthropic package not installed")
            raise AIConfigurationError(
                "langchain-anthropic package is not installed. Install it with: pip install langchain-anthropic",
                provider="anthropic",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create LangChain Anthropic model: {e}")
            raise AIConfigurationError(
                f"Failed to create LangChain Anthropic model: {str(e)}",
                provider="anthropic",
                original_error=e
            )


class LangChainGoogleFactory(ModelBase):
    """
    Factory for creating Google Gemini models using LangChain.
    """
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str, 
        base_url: str | None = None
    ) -> Any:
        """
        Create a LangChain ChatGoogleGenerativeAI model instance.
        
        Args:
            model_name: Google model name (e.g., 'gemini-1.5-pro')
            api_key: Google API key
            base_url: Not used for Google
            
        Returns:
            Configured ChatGoogleGenerativeAI instance
        """
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            logger.debug(f"Creating LangChain Google model: {model_name}")
            
            model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.7,
            )
            
            logger.info(f"Successfully created LangChain Google model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("langchain-google-genai package not installed")
            raise AIConfigurationError(
                "langchain-google-genai package is not installed. Install it with: pip install langchain-google-genai",
                provider="google",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create LangChain Google model: {e}")
            raise AIConfigurationError(
                f"Failed to create LangChain Google model: {str(e)}",
                provider="google",
                original_error=e
            )


class LangChainOllamaFactory(ModelBase):
    """
    Factory for creating Ollama models using LangChain.
    """
    
    def __init__(self, default_base_url: str = "http://localhost:11434"):
        self.default_base_url = default_base_url
    
    def create_model(
        self, 
        model_name: str, 
        api_key: str = "",  # Not needed for Ollama
        base_url: str | None = None
    ) -> Any:
        """
        Create a LangChain ChatOllama model instance.
        
        Args:
            model_name: Ollama model name (e.g., 'llama3', 'mistral')
            api_key: Not used for Ollama
            base_url: Ollama server URL
            
        Returns:
            Configured ChatOllama instance
        """
        try:
            from langchain_ollama import ChatOllama
            
            effective_base_url = base_url or self.default_base_url
            logger.debug(f"Creating LangChain Ollama model: {model_name} at {effective_base_url}")
            
            model = ChatOllama(
                model=model_name,
                base_url=effective_base_url,
                temperature=0.7,
            )
            
            logger.info(f"Successfully created LangChain Ollama model: {model_name}")
            return model
            
        except ImportError as e:
            logger.error("langchain-ollama package not installed")
            raise AIConfigurationError(
                "langchain-ollama package is not installed. Install it with: pip install langchain-ollama",
                provider="ollama",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Failed to create LangChain Ollama model: {e}")
            raise AIConfigurationError(
                f"Failed to create LangChain Ollama model: {str(e)}",
                provider="ollama",
                original_error=e
            )


# Type alias for supported LangChain providers
LangChainProviderType = Literal["openai", "anthropic", "google", "ollama"]


class LangChainModelFactory:
    """
    Main factory class for creating LangChain models.
    
    Uses the correct provider factory based on the provider name.
    """
    
    _factories: dict[str, ModelBase] = {
        "openai": LangChainOpenAIFactory(),
        "anthropic": LangChainAnthropicFactory(),
        "google": LangChainGoogleFactory(),
        "ollama": LangChainOllamaFactory(),
    }
    
    @classmethod
    def get_model(
        cls,
        provider_name: LangChainProviderType,
        model_name: str,
        api_key: str,
        base_url: str | None = None
    ) -> Any:
        """
        Get a LangChain model instance for the specified provider.
        
        Args:
            provider_name: Name of the AI provider
            model_name: Name of the model to create
            api_key: API key for the provider
            base_url: Optional custom base URL
            
        Returns:
            Configured LangChain model instance
            
        Raises:
            AIConfigurationError: If provider is not supported
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
    "LangChainOpenAIFactory",
    "LangChainAnthropicFactory",
    "LangChainGoogleFactory",
    "LangChainOllamaFactory",
    "LangChainModelFactory",
    "LangChainProviderType"
]
