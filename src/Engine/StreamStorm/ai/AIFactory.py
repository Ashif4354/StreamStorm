"""
AI Factory Module - Main entry point for creating AI services.

This module provides the AIFactory class that serves as the single entry point
for creating AI service instances. It supports switching between different
AI frameworks (PydanticAI, LangChain) and providers (OpenAI, Anthropic, Google).
"""

from typing import Literal
from logging import getLogger, Logger

from .Base import AIBase, AIConfigurationError
from .PydanticAI import PydanticAIService
from .LangChain import LangChainService


logger: Logger = getLogger(f"streamstorm.ai.{__name__}")


# Type aliases
FrameworkType = Literal["pydantic", "langchain"]
ProviderType = Literal["openai", "anthropic", "google", "ollama"]


class AIFactory:
    """
    Factory for creating AI service instances.
    
    This factory provides a unified interface for creating AI services
    regardless of the underlying framework or provider. It handles
    the complexity of selecting and configuring the right components.
    
    Example usage:
        # Create a PydanticAI service with OpenAI
        ai = AIFactory.create(
            framework="pydantic",
            provider="openai",
            model="gpt-4o-mini",
            api_key="sk-..."
        )
        
        # Generate messages
        messages = await ai.generate_messages("Gaming stream comments", count=10)
        
        # Or use LangChain instead
        ai = AIFactory.create(
            framework="langchain",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="sk-ant-..."
        )
    """
    
    _framework_classes: dict[str, type[AIBase]] = {
        "pydantic": PydanticAIService,
        "langchain": LangChainService,
    }
    
    @classmethod
    def create(
        cls,
        framework: FrameworkType = "pydantic",
        provider: ProviderType = "openai",
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None
    ) -> AIBase:
        """
        Create and return an AI service instance.
        
        Args:
            framework: The AI framework to use ('pydantic' or 'langchain')
            provider: The AI provider ('openai', 'anthropic', 'google', 'ollama')
            model: The model name to use
            api_key: API key for the provider (required except for ollama)
            base_url: Optional custom base URL for the API
            
        Returns:
            Configured AIBase instance ready for use
            
        Raises:
            AIConfigurationError: If configuration is invalid or missing
            
        Example:
            ```python
            ai = AIFactory.create(
                framework="pydantic",
                provider="openai",
                model="gpt-4o-mini",
                api_key="sk-..."
            )
            messages = await ai.generate_messages("Fun gaming comments")
            ```
        """
        # Validate framework
        framework = framework.lower()
        if framework not in cls._framework_classes:
            supported = ", ".join(cls._framework_classes.keys())
            raise AIConfigurationError(
                f"Unsupported framework: {framework}. Supported frameworks: {supported}"
            )
        
        # Validate provider
        provider = provider.lower()
        valid_providers = {"openai", "anthropic", "google", "ollama"}
        if provider not in valid_providers:
            raise AIConfigurationError(
                f"Unsupported provider: {provider}. Supported providers: {', '.join(valid_providers)}"
            )
        
        # Validate API key (not required for ollama)
        if provider != "ollama" and not api_key:
            raise AIConfigurationError(
                f"API key is required for provider: {provider}",
                provider=provider
            )
        
        logger.info(f"Creating AI service: framework={framework}, provider={provider}, model={model}")
        
        # Get the service class and instantiate
        service_class = cls._framework_classes[framework]
        
        service = service_class(
            provider_name=provider,
            model_name=model,
            api_key=api_key or "",
            base_url=base_url
        )
        
        logger.info(f"Successfully created {framework} AI service with {provider} provider")
        return service
    
    @classmethod
    def get_supported_frameworks(cls) -> list[str]:
        """Return list of supported AI frameworks."""
        return list(cls._framework_classes.keys())
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Return list of supported AI providers."""
        return ["openai", "anthropic", "google", "ollama"]
    
    @classmethod
    def get_default_models(cls) -> dict[str, str]:
        """Return default model names for each provider."""
        return {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-sonnet-20241022",
            "google": "gemini-1.5-flash",
            "ollama": "llama3"
        }


# Convenience function for quick service creation
async def create_ai_service(
    provider: str,
    model: str,
    api_key: str,
    base_url: str | None = None,
    framework: str = "pydantic"
) -> AIBase:
    """
    Convenience function to create an AI service.
    
    This is a simple wrapper around AIFactory.create() for
    quick service creation.
    
    Args:
        provider: AI provider name
        model: Model name
        api_key: API key
        base_url: Optional base URL
        framework: Framework to use (default: pydantic)
        
    Returns:
        Configured AI service instance
    """
    return AIFactory.create(
        framework=framework,
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )


__all__: list[str] = [
    "AIFactory",
    "create_ai_service",
    "FrameworkType",
    "ProviderType"
]
