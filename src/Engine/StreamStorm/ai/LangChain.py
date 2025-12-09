"""
LangChain Service Implementation.

This module provides the main AI service class using the LangChain framework.
It implements the AIBase interface and provides methods for generating
messages and channel names using structured outputs.
"""

from typing import Any
from logging import getLogger, Logger

from .Base import AIBase, AIGenerationError, AIConfigurationError
from .ResponseModels import GeneratedMessages, GeneratedChannelNames
from .LangChainModelFactory import LangChainModelFactory


logger: Logger = getLogger(f"streamstorm.ai.{__name__}")


# System prompts for different generation tasks
MESSAGE_GENERATION_SYSTEM_PROMPT = """You are a creative assistant that generates authentic-sounding chat messages for YouTube live streams.

Your task is to generate messages that:
1. Sound natural and human-like
2. Are appropriate for a live stream chat
3. Vary in length and style (some short, some longer)
4. Include emojis occasionally but not excessively
5. Express enthusiasm, support, or casual commentary
6. Avoid spam-like or promotional content
7. Never include offensive, hateful, or inappropriate content

Generate diverse messages that could come from different viewers."""


CHANNEL_NAME_GENERATION_SYSTEM_PROMPT = """You are a creative assistant that generates catchy YouTube channel names.

Your task is to generate channel names that:
1. Are memorable and unique
2. Relate to the given topic or theme
3. Are appropriate for YouTube
4. Are not too long (3-4 words maximum)
5. Include creative wordplay when appropriate
6. Sound professional yet engaging
7. Would appeal to the target audience

Generate diverse names with different styles."""


class LangChainService(AIBase):
    """
    AI service implementation using LangChain framework.
    
    This service uses LangChain's with_structured_output to ensure
    consistent and validated responses from the AI model.
    """
    
    def __init__(
        self, 
        provider_name: str,
        model_name: str,
        api_key: str,
        base_url: str | None = None
    ):
        """
        Initialize the LangChain service.
        
        Args:
            provider_name: Name of the AI provider ('openai', 'anthropic', 'google')
            model_name: Name of the model to use
            api_key: API key for the provider
            base_url: Optional custom base URL
        """
        self.provider_name = provider_name
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self._model = None
        
        logger.info(f"Initializing LangChain service with provider: {provider_name}, model: {model_name}")
    
    def _get_model(self) -> Any:
        """Lazy-load and cache the model instance."""
        if self._model is None:
            self._model = LangChainModelFactory.get_model(
                provider_name=self.provider_name,
                model_name=self.model_name,
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._model
    
    async def generate(self, prompt: str, **kwargs) -> Any:
        """
        Generate raw AI output for a given prompt.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional arguments
            
        Returns:
            Raw AI response content
        """
        try:
            from langchain_core.messages import HumanMessage
            
            model = self._get_model()
            
            result = await model.ainvoke([HumanMessage(content=prompt)])
            return result.content
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise AIGenerationError(
                f"Failed to generate response: {str(e)}",
                provider=self.provider_name,
                original_error=e
            )
    
    async def generate_messages(self, prompt: str, count: int = 10) -> list[str]:
        """
        Generate chat messages using structured output.
        
        Args:
            prompt: Context or theme for the messages
            count: Number of messages to generate
            
        Returns:
            List of generated message strings
        """
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            model = self._get_model()
            
            # Create structured output chain
            structured_model = model.with_structured_output(GeneratedMessages)
            
            # Construct the messages
            messages = [
                SystemMessage(content=MESSAGE_GENERATION_SYSTEM_PROMPT),
                HumanMessage(content=f"""Generate exactly {count} unique chat messages based on the following context:

{prompt}

Requirements:
- Generate exactly {count} messages
- Each message should be different in style and length
- Messages should be appropriate for YouTube live stream chat
- Include some messages with emojis and some without
- Keep messages between 2-50 words""")
            ]

            logger.info(f"Generating {count} messages with prompt: {prompt[:50]}...")
            
            result = await structured_model.ainvoke(messages)
            generated_messages = result.messages
            
            logger.info(f"Successfully generated {len(generated_messages)} messages")
            return generated_messages
            
        except ImportError as e:
            logger.error("LangChain packages not installed")
            raise AIConfigurationError(
                "LangChain packages are not installed",
                provider=self.provider_name,
                original_error=e
            )
        except Exception as e:
            logger.error(f"Message generation failed: {e}")
            raise AIGenerationError(
                f"Failed to generate messages: {str(e)}",
                provider=self.provider_name,
                original_error=e
            )
    
    async def generate_channel_names(self, topic: str, count: int = 5) -> list[str]:
        """
        Generate YouTube channel name suggestions.
        
        Args:
            topic: Topic or theme for the channel names
            count: Number of names to generate
            
        Returns:
            List of suggested channel names
        """
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            model = self._get_model()
            
            # Create structured output chain
            structured_model = model.with_structured_output(GeneratedChannelNames)
            
            # Construct the messages
            messages = [
                SystemMessage(content=CHANNEL_NAME_GENERATION_SYSTEM_PROMPT),
                HumanMessage(content=f"""Generate exactly {count} unique YouTube channel name suggestions for the following topic:

Topic: {topic}

Requirements:
- Generate exactly {count} channel names
- Names should be catchy and memorable
- Keep names to 3-4 words maximum
- Names should relate to the topic
- Include variety (some playful, some professional)""")
            ]

            logger.info(f"Generating {count} channel names for topic: {topic}")
            
            result = await structured_model.ainvoke(messages)
            channel_names = result.channel_names
            
            logger.info(f"Successfully generated {len(channel_names)} channel names")
            return channel_names
            
        except ImportError as e:
            logger.error("LangChain packages not installed")
            raise AIConfigurationError(
                "LangChain packages are not installed",
                provider=self.provider_name,
                original_error=e
            )
        except Exception as e:
            logger.error(f"Channel name generation failed: {e}")
            raise AIGenerationError(
                f"Failed to generate channel names: {str(e)}",
                provider=self.provider_name,
                original_error=e
            )


__all__: list[str] = [
    "LangChainService",
    "MESSAGE_GENERATION_SYSTEM_PROMPT",
    "CHANNEL_NAME_GENERATION_SYSTEM_PROMPT"
]
