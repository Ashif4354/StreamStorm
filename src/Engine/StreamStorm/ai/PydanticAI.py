from pydantic_ai import Agent

from .PydanticAIModelFactory import ModelFactory
from .Base import AIBase
from .ResponseModels import AIResponse



class PydanticAI(AIBase):
    def __init__(self, provider_name: str, model_name: str, api_key: str, base_url: str = None):
        """
        Initializes the AI service with a specific provider.
        """
        self.model = ModelFactory.get_model(provider_name, model_name=model_name, api_key=api_key, base_url=base_url)
        # self.model = Agent(base_model, output_type=AIResponse)
        
        
    async def generate(self,agent, prompt : str ):
        responses = await agent.run(prompt)
        return responses.values
    
        
        
    async def generate_messages(self, prompt : str):
        new_prompt = prompt + "\n"
        agent = Agent(model=self.model, output_type=AIResponse)
        res = await self.generate(agent, new_prompt)
        return res
        
       
    async def generate_channels(self, prompt : str):
        new_prompt = prompt + "\n"
        agent = Agent(model=self.model, output_type=AIResponse)
        res = await self.generate(agent, new_prompt)
        return res 