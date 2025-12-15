from .LangchainModelFactory import ModelFactory
from .Base import AIBase
from .ResponseModels import AIResponse

class LangchainAI(AIBase):
    def __init__(self, provider_name: str, model_name: str, api_key: str, base_url: str = None):
        
        if provider_name.lower() == "openai":
            base_model = ModelFactory.get_model(provider_name, model_name=model_name, api_key=api_key, base_url = base_url)

        elif provider_name.lower() == "google":
            base_model = ModelFactory.get_model(provider_name, model_name=model_name, api_key=api_key)

        elif provider_name.lower() == "anthropic":
            base_model = ModelFactory.get_model(provider_name, model_name=model_name, api_key=api_key)
            
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

        self.model = base_model.with_structured_output(AIResponse)
        
    def generate_messages(self, prompt : str):
        responses = self.model.invoke(prompt)
        return responses.values
    
    def generate_channels(self, prompt : str):
        responses = self.model.invoke(prompt) 
        return responses.values