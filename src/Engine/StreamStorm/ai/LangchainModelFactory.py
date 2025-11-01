from langchain_openai.chat_models import ChatOpenAI
from langchain_ollama.chat_models import ChatOllama
from .Base import ModelBase


class OpenAIModel(ModelBase):
    def create_model(self, model_name: str, api_key: str):
        model = ChatOpenAI(model=model_name, api_key=api_key)
        return model
    
    
class OllamaModel(ModelBase):
    def create_model(self, model_name: str):
        model = ChatOllama(model=model_name)
        return model


class ModelFactory:
    
    factories = {
        "openai": OpenAIModel(),
        "ollama": OllamaModel()
    }
    
    
    
    @staticmethod
    def get_model(provider_name: str, **kwargs):
        provider_name = provider_name.lower()
        if provider_name not in ModelFactory.factories:
            raise ValueError(f"Unsupported provider: {provider_name}")
        provider = ModelFactory.factories[provider_name]
        return provider.create_model(**kwargs)