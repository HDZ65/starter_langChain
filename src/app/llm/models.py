"""Initialisation et configuration des modèles LLM."""

from langchain_core.language_models import BaseChatModel
from langchain_openai import init_chat_model

from app.settings import settings


def get_default_model() -> BaseChatModel:
    """
    Retourne le modèle de chat par défaut configuré.

    Returns:
        BaseChatModel: Modèle de chat LangChain configuré
    """
    model = init_chat_model(
        model=settings.model_name,
        model_provider="openai",
        temperature=0.7,
        max_tokens=1000,
        timeout=30.0,
        api_key=settings.openai_api_key,
    )
    return model
