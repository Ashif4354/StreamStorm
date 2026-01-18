"""
These dependencies are required for the LangchainModelFactory class which is not added in `pyproject.toml`.

"langchain>=1.0.3",
"langchain-openai>=1.0.1",
"langchain-ollama>=1.0.0",
"langchain-community>=0.4.1",
"langchain-google-genai>=3.2.0",
"langchain-anthropic>=1.2.0",
"""

# from langchain_anthropic.chat_models import ChatAnthropic
# from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
# from langchain_openai.chat_models import ChatOpenAI

# from .Base import ModelBase


# class OpenAIModel(ModelBase):
#     def create_model(self, model_name: str, api_key: str, base_url: str):
#         model = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
#         return model


# class GoogleModel(ModelBase):
#     def create_model(self, model_name: str, api_key: str):
#         model = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
#         return model


# class AnthropicModel(ModelBase):
#     def create_model(self, model_name: str, api_key: str):
#         model = ChatAnthropic(model=model_name, api_key=api_key)
#         return model


# class ModelFactory:
#     factories = {
#         "openai": OpenAIModel(),
#         "google": GoogleModel(),
#         "anthropic": AnthropicModel(),
#     }

#     @staticmethod
#     def get_model(provider_name: str, **kwargs):
#         provider_name = provider_name.lower()

#         if provider_name not in ModelFactory.factories:
#             raise ValueError(f"Unsupported provider: {provider_name}")

#         provider = ModelFactory.factories[provider_name]
#         return provider.create_model(**kwargs)
