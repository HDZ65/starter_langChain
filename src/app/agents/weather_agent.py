"""Agent météo utilisant LangChain v1 et LangGraph."""

from dataclasses import dataclass

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_agent

from app.llm.models import get_default_model
from app.llm.prompts import SYSTEM_PROMPT_WEATHER
from app.memory.base_memory import get_default_checkpointer
from app.tools.weather import Context, get_user_location, get_weather_for_location


@dataclass
class WeatherResponse:
    """Format de réponse structurée de l'agent météo."""

    text: str
    location: str | None = None


def build_weather_agent(use_mcp: bool = False, additional_tools: list[BaseTool] | None = None):
    """
    Construit l'agent météo avec ses outils et sa configuration.

    Args:
        use_mcp: Si True, charge et inclut les outils MCP disponibles
        additional_tools: Liste optionnelle d'outils supplémentaires à ajouter

    Returns:
        Agent LangGraph configuré
    """
    model = get_default_model()
    checkpointer = get_default_checkpointer()

    # Outils de base pour la météo
    tools = [get_weather_for_location, get_user_location]

    # Ajouter les outils MCP si demandé
    if use_mcp:
        try:
            from app.mcp import get_mcp_tools

            mcp_tools = get_mcp_tools()
            tools.extend(mcp_tools)
        except Exception as e:
            # Ignorer silencieusement si MCP n'est pas disponible
            pass

    # Ajouter les outils supplémentaires
    if additional_tools:
        tools.extend(additional_tools)

    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer,
        system_prompt=SYSTEM_PROMPT_WEATHER,
        context_schema=Context,
        response_format=WeatherResponse,
    )

    return agent


def ask_weather(
    question: str, user_id: str = "1", use_mcp: bool = False
) -> WeatherResponse:
    """
    Pose une question à l'agent météo.

    Args:
        question: Question de l'utilisateur
        user_id: Identifiant de l'utilisateur
        use_mcp: Si True, utilise les outils MCP disponibles

    Returns:
        WeatherResponse: Réponse structurée avec la météo
    """
    agent = build_weather_agent(use_mcp=use_mcp)

    # Configuration avec thread_id pour la mémoire
    config = {
        "configurable": {
            "thread_id": f"user_{user_id}",
        }
    }

    # Contexte utilisateur
    context = Context(user_id=user_id)

    # Invocation de l'agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
        context=context,
    )

    return result["structured_response"]
