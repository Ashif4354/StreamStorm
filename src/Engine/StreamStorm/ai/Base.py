# src/Engine/StreamStorm/ai/Base.py

class AIBase:
    """
    Abstract base class for an AI provider.
    """
    def generate(self):
        """
        Main generation method to be implemented by concrete providers.
        """
        raise NotImplementedError

    def generate_messages(self):
        """
        Generates a list of random messages.
        """
        raise NotImplementedError

    def generate_channels(self):
        """
        Generates a list of random channel names.
        """
        raise NotImplementedError

class ModelBase:
    """
    Abstract interface for creating AI models.
    """
    def create_model(self):
        """
        Model method to be implemented by concrete factories.
        """
        raise NotImplementedError