from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import Model

from .Base import AIBase
from .PydanticAIModelFactory import ModelFactory
from .ResponseModels import AIGeneratedChannels, AIGeneratedMessages


class PydanticAI(AIBase):
    def __init__(
        self,
        provider_name: str,
        model_name: str,
        api_key: str,
        base_url: str | None = None,
    ):
        """
        Initializes the AI service with a specific provider.
        """
        self.model: Model = ModelFactory.get_model(
            provider_name, model_name=model_name, api_key=api_key, base_url=base_url
        )

    async def _generate(self, agent: Agent | None, prompt: str, *args, **kwargs) -> Any:
        if agent is None:
            raise RuntimeError("Agent creation failed")

        responses = await agent.run(prompt)
        return responses.output

    async def generate_messages(self, prompt: str, *args, **kwargs) -> list[str]:
        system_prompt = (
            "You are a YouTube livestream chat messages generation assistant. "
            "IMPORTANT RULES: "
            "1. Generate chats ONLY based on the user-provided input. "
            "2. Do NOT add explanations — output comments only. "
            "TASK: "
            "- Generate natural, human-like YouTube live chats. "
            "- Match the tone requested by the user (supportive, funny, neutral, critical, etc.). "
            "STYLE GUIDELINES: "
            "- Keep comments concise and engaging. "
            "- Use simple language. "
            "- Emojis are allowed but should be minimal and natural. "
            "- Avoid repetition across multiple comments. "
        )

        agent = Agent(
            model=self.model,
            output_type=AIGeneratedMessages,
            system_prompt=system_prompt,
        )

        try:
            responses = await self._generate(agent, prompt)
        except Exception as e:
            responses = AIGeneratedMessages(messages=[])

        return responses.messages

    async def generate_channels(self, prompt: str) -> list[str]:
        system_prompt = (
            "You are a YouTube channel names generator.",
            "STRICT RULES: "
            " 2. You can mix existing or real channel names as well. "
            " 3. Generate names ONLY based on user-provided context. "
            " 4. Channel names must be 1 or 2 words ONLY. "
            " 5. Do NOT exceed 2 words under any condition. "
            " 6. Do NOT include numbers, symbols, or emojis unless explicitly asked. "
            "NAMING STYLE: "
            "- Names should be short, catchy, and brand-friendly. "
            "- Avoid generic or spammy words. "
            "- Words must be easy to pronounce. "
            "",
        )

        agent = Agent(
            model=self.model,
            output_type=AIGeneratedChannels,
            system_prompt=system_prompt,
        )

        try:
            response = await self._generate(agent, prompt)
        except Exceptionas as e:
            response = AIGeneratedChannels(channel_names=[])

        return response.channel_names
