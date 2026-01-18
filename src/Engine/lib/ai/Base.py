from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel
from pydantic_ai.models import Model


class AIBase(ABC):
    """
    Abstract base class for an AI provider.
    """

    @abstractmethod
    async def _generate(self, *args, **kwargs):
        """
        Main generation method to be implemented by concrete providers.
        """
        pass

    @abstractmethod
    async def generate_messages(self, prompt: str, *args, **kwargs) -> BaseModel:
        """
        Generates a list of random messages.
        """
        pass

    @abstractmethod
    async def generate_channels(self, prompt: str, *args, **kwargs) -> Any:
        """
        Generates a list of random channel names.
        """
        pass


class ModelBase(ABC):
    """
    Abstract interface for creating AI models.
    """

    @abstractmethod
    def create_model(self, model_name: str, api_key: str, *args, **kwargs) -> Model:
        """
        Model method to be implemented by concrete factories.
        """
        pass
