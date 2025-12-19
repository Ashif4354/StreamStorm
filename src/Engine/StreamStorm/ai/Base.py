from abc import ABC, abstractmethod

class AIBase(ABC):
    """
    Abstract base class for an AI provider.
    """
    @abstractmethod
    def __generate(self):
        """
        Main generation method to be implemented by concrete providers.
        """
        pass
    
    @abstractmethod
    def generate_messages(self):
        """
        Generates a list of random messages.
        """
        pass

    @abstractmethod
    def generate_channels(self):
        """
        Generates a list of random channel names.
        """
        pass

class ModelBase(ABC):
    """
    Abstract interface for creating AI models.
    """
    @abstractmethod
    def create_model(self):
        """
        Model method to be implemented by concrete factories.
        """
        pass