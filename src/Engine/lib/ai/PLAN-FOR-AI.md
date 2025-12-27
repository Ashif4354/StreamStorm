# Development Plan: StreamStorm AI Module

## 1. Objective

This document outlines the architecture for a **modular and extensible AI engine** within the **StreamStorm** project.
The core design centers on the **Abstract Factory Pattern** to decouple the main application from specific AI model providers (e.g., **OpenAI**, **Ollama**).

This allows for easy swapping or addition of new providers without altering the core business logic. *Namma modular engineering, thala-level.*

---

## 2. File Structure

The AI module will be organized within the `src/Engine/StreamStorm/ai/` directory.

```
src/
└── Engine/
    └── StreamStorm/
        └── ai/
            ├── __init__.py
            ├── Base.py
            ├── ResponseModels.py
            ├── PydanticAIModelFactory.py
            |── LangChainModelFactory.py
            |── LangChain.py
            └── PydanticAI.py
```

---

## 3. Component Breakdown

Detailed plan for each file below 👇

---

### 3.1. `src/Engine/StreamStorm/ai/Base.py`

**Purpose:**
Defines the abstract base classes (interfaces) for all provider and factory implementations.
This ensures that any new provider adheres to a consistent API contract.

```python
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
```

---

### 3.2. `src/Engine/StreamStorm/ai/ResponseModels.py`

**Purpose:**
Defines the **Pydantic models** used to structure and validate the outputs from the AI.
This ensures predictable data structures for tasks like **message generation** and **channel naming**.

```python
# src/Engine/StreamStorm/ai/ResponseModels.py

class Messages(BaseModel):
    """
    A Pydantic model to structure generated messages.
    (Schema to be defined based on requirements)
    """
    pass

class ChannelNames(BaseModel):
    """
    A Pydantic model to structure generated channel names.
    (Schema to be defined based on requirements)
    """
    pass
```

---

### 3.3.1 `src/Engine/StreamStorm/ai/PydanticAIModelFactory.py`

**Purpose:**
Implements the concrete factory classes for each supported AI provider (**OpenAI**, **Ollama**).
Includes a `ModelFactory` to dynamically select the correct factory at runtime based on configuration.

```python
# src/Engine/StreamStorm/ai/PydanticAIModelFactory.py

from pydantic_ai.models.openai import OpenAIChatModel
# Assuming provider implementations exist
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.ollama import OllamaProvider
# Assuming AIBase contains the ModelFactory definition
from .AIBase import ModelFactory 

class OpenAIModel(ModelBase):
    def create_model(self, model_name):
        provider = OpenAIProvider()
        return OpenAIChatModel(model_name, provider=provider)

class OllamaModel(ModelBase):
    def create_model(self):
        provider = OllamaProvider(base_url="http://localhost:11434")
        return OpenAIChatModel("llama3", provider=provider)


class ModelFactory:
    """Returns the right factory based on provider name."""

    factories = {
        "openai": OpenAIModel(),
        "ollama": OllamaModel(),
    }

    @staticmethod
    def get_model(provider_name: str) -> ModelFactory:
        provider_name = provider_name.lower()
        if provider_name not in ModelFactory.factories:
            raise ValueError(f"Unsupported provider: {provider_name}")
        provider = ModelFactory.factories[provider_name]
        return provider.create_model()
```

---

### 3.3.2 `src/Engine/StreamStorm/ai/LangChainModelFactory.py`

**Purpose:**
Implements the concrete factory classes for each supported AI provider (**OpenAI**, **Ollama**).
Includes a `ModelFactory` to dynamically select the correct factory at runtime based on configuration.

```python
# src/Engine/StreamStorm/ai/PydanticAI.py
## Implement this yourself
````

---

### 3.4.1 `src/Engine/StreamStorm/ai/PydanticAI.py`

**Purpose:**
Main service class for the AI module.
It initializes with the desired provider and provides high-level methods for business logic like generating messages and channel names.

```python
# src/Engine/StreamStorm/ai/PydanticAI.py

class PydanticAI(AIBase):
    def __init__(self, provider_name: str, model_name: str = None):
        """
        Initializes the AI service with a specific provider.
        """
        # Logic to use ModelFactory to get a factory
        # and create a model instance
        model = ModelFactory.get_model(provider_name)
        self.agent = Agent(model)

    def generate_random_messages(self, count: int):
        """
        Generates a list of random messages.
        """
        # Will use the initialized model and the Messages response model
        pass

    def generate_channel_names(self, topic: str):
        """
        Generates suggested channel names based on a topic.
        """
        # Will use the initialized model and the ChannelNames response model
        pass
```

---

### 3.4.2 `src/Engine/StreamStorm/ai/LangChain.py`

**Purpose:**
Main service class for the AI module.
It initializes with the desired provider and provides high-level methods for business logic like generating messages and channel names.

```python
# src/Engine/StreamStorm/ai/LangChain.py

class LangChain(AIBase):
    def __init__(self, provider_name: str, model_name: str = None):
        """
        Initializes the AI service with a specific provider.
        """
        # Logic to use ModelFactory to get a factory
        # and create a model instance
        pass

    def generate_random_messages(self, count: int):
        """
        Generates a list of random messages.
        """
        # Will use the initialized model and the Messages response model
        pass

    def generate_channel_names(self, topic: str):
        """
        Generates suggested channel names based on a topic.
        """
        # Will use the initialized model and the ChannelNames response model
        pass
```

---

## 4. The AI class will be used by StreamStorm in the following ways

```python
from Engine.StreamStorm.ai.AI import LangChain

# Instantiate the AI service with the desired provider
ai = LangChain(provider_name="openai", model_name="gpt-4o-mini")
# (or)
ai = PydanticAI(provider_name="openai", model_name="gpt-4o-mini")
#  You can create a factory this switching as well

# Generate some random messages
messages = ai.generate_random_messages(count=5)
print("Generated Messages:", messages)

# Generate channel names based on a topic
channel_names = ai.generate_channel_names(topic="AI development")
print("Suggested Channel Names:", channel_names)
```

**End of Document.**
