from .LangchainModelFactory import ModelFactory
from .Base import AIBase

class LangchainAI(AIBase):
    def __init__(self, provider_name: str, model_name: str, api_key: str):
        
        if provider_name.lower() == "openai":
            self.model = ModelFactory.get_model(provider_name, model_name=model_name, api_key=api_key)
        elif provider_name.lower() == "ollama":
            self.model = ModelFactory.get_model(provider_name, model_name=model_name)
            
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
        
    def generate_messages(self,topic: str, count: int):
        prompt = (
                f"Generate {count} random short messages about {topic}. "
                "Return each message on a new line."
            )
        responses = self.model.invoke(prompt)
        return responses
    
    def generate_channels(self,count: int):
        prompt = (
                f"Generate {count} random short channel names related to streaming. "
                "Return each channel name on a new line."
        )
        responses = self.model.invoke(prompt)
        return responses
    
    
    
    
        