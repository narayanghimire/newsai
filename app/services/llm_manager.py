import os
from typing import Dict

from dotenv import load_dotenv
from app.services.llm_service.open_ai_llm_service import OpenAILLMService

load_dotenv()

class LLMManager:
    _models: Dict[str, object] = {
        "openai": OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY")),
    }

    _default_model = "openai"

    @classmethod
    def get_llm(cls, model_name: str = None):
        """
        Returns the selected LLM service. Defaults to OpenAI if not set.
        """
        return cls._models.get(model_name, cls._models[cls._default_model])

    @classmethod
    def list_available_models(cls):
        """
        Returns a list of available LLM models.
        """
        return list(cls._models.keys())
