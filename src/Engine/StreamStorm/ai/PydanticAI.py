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
        
        
    async def __generate(self,agent, prompt : str ):
        responses = await agent.run(prompt)
        return responses.output.values
    
        
        
    async def generate_messages(self, prompt : str):
        new_prompt = prompt + "\n"
        system_prompt = (
            "You are a YouTube comment generation assistant."
            "IMPORTANT RULES:"
            "1. Generate comments ONLY based on the user-provided input."
            "2. Do NOT add explanations — output comments only."
            "TASK:"
            "- Generate natural, human-like YouTube comments."
            "- Comments should feel authentic, casual, and platform-appropriate."
            "- Match the tone requested by the user (supportive, funny, neutral, critical, etc.)."
            "- Avoid spammy language, hashtags overload, or promotional phrases unless explicitly asked."
            "STYLE GUIDELINES:"
            "- Keep comments concise and engaging."
            "- Use simple language."
            "- Emojis are allowed but should be minimal and natural."
            "- Avoid repetition across multiple comments."

        )
        agent = Agent(model=self.model, output_type=AIResponse, system_prompt=system_prompt)
        res = await self.__generate(agent, new_prompt)
        return res
        
       
    async def generate_channels(self, prompt : str):
        new_prompt = prompt + "\n"
        system_prompt = (
            "You are a YouTube channel name generator.",
            "STRICT RULES:"
            " 2. Do NOT use existing or real channel names intentionally."
            " 3. Generate names ONLY based on user-provided context."
            " 4. Channel names must be 1 or 2 words ONLY."
            " 5. Do NOT exceed 2 words under any condition."
            " 6. Do NOT include numbers, symbols, or emojis unless explicitly asked."
            "NAMING STYLE:"
            "- Names should be short, catchy, and brand-friendly."
            "- Avoid generic or spammy words."
            "- Words must be easy to pronounce."
            "CASING:"
            "- If PascalCase is requested, capitalize each word (e.g., CodeSpark)."
            "- If not requested, use normal capitalization."
        )
        agent = Agent(model=self.model, output_type=AIResponse, system_prompt=system_prompt)
        res = await self.__generate(agent, new_prompt)
        return res 