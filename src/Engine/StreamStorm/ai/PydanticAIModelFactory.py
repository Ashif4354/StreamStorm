from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.models.anthropic import AnthropicModel


from .Base import ModelBase


class OpenAI(ModelBase):
    def create_model(self, model_name: str, api_key: str, base_url: str):
        provider = OpenAIProvider(api_key, base_url)
        model = OpenAIModel(model_name=model_name, provider=provider)
        return model
    
class Google(ModelBase):
    def create_model(self, model_name: str, api_key: str, **kwargs):
        provider = GoogleProvider(api_key)
        model = GoogleModel(model_name=model_name, provider=provider)
        return model
    
class Anthropic(ModelBase):
    def create_model(self, model_name: str, api_key: str, **kwargs):
        provider = AnthropicProvider(api_key)
        model = AnthropicModel(model_name=model_name, provider=provider)
        return model
    
    
    
class ModelFactory:
    
    factories = {
        'openai': OpenAI(),
        'google': Google(),
        'anthropic': Anthropic()
    }
    
    @staticmethod
    def get_model(provider_name: str, **kwargs):
        provider_name = provider_name.lower()
        
        if provider_name not in ModelFactory.factories:
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        provider = ModelFactory.factories[provider_name]
        return provider.create_model(**kwargs)