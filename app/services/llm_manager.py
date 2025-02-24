import os
from typing import Dict

from dotenv import load_dotenv

from app.services.llm_service.gemini_llm_service import GeminiLlmService
from app.services.llm_service.groq_llm_service import GroqLlmService
from app.services.llm_service.open_ai_llm_service import OpenAILLMService

load_dotenv()

class LLMManager:
    _models: Dict[str, object] = {
        "openai": OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY")),
        "gemini": GeminiLlmService(api_key=os.getenv("GEMINI_API_KEY")),
        "groq": GroqLlmService(api_key=os.getenv("GROQ_API_KEY")),
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
