"""Agent météo implémenté avec StateGraph personnalisé.

Version alternative de weather_agent.py qui utilise directement
StateGraph au lieu de create_agent() pour plus de contrôle.
"""

from dataclasses import dataclass
from typing import Annotated, Literal

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from app.llm.models import get_default_model
from app.llm.prompts import SYSTEM_PROMPT_WEATHER
from app.memory.base_memory import get_default_checkpointer
from app.tools.weather import Context, get_user_location, get_weather_for_location


class WeatherState(BaseModel):
    """État pour l'agent météo avec StateGraph."""

    messages: Annotated[list, add_messages]
    """Messages de la conversation."""

    user_id: str = "1"
    """ID de l'utilisateur."""

    location: str | None = None
    """Localisation détectée."""


@dataclass
class WeatherGraphResponse:
    """Réponse structurée de l'agent météo graph."""

    text: str
    location: str | None = None
    steps: int = 0


def should_continue_weather(state: WeatherState) -> Literal["tools", "end"]:
    """
    Détermine si l'agent doit utiliser des outils ou terminer.

    Args:
        state: État actuel

    Returns:
        "tools" pour continuer avec les outils, "end" pour terminer
    """
    messages = state.messages
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


def call_weather_model(state: WeatherState) -> dict:
    """
    Node qui appelle le modèle pour l'agent météo.

    Args:
        state: État actuel

    Returns:
        Mise à jour de l'état avec la réponse du modèle
    """
    model = get_default_model()

    # Bind les outils météo au modèle
    tools = [get_weather_for_location, get_user_location]
    model = model.bind_tools(tools)

    # Ajouter le prompt système si c'est le premier message
    messages = state.messages
    if len(messages) == 1:
        from langchain_core.messages import SystemMessage

        messages = [SystemMessage(content=SYSTEM_PROMPT_WEATHER)] + messages

    response = model.invoke(messages)

    return {"messages": [response]}


def extract_location(state: WeatherState) -> dict:
    """
    Extrait la localisation des messages si disponible.

    Args:
        state: État actuel

    Returns:
        Mise à jour avec la localisation
    """
    location = None

    # Chercher la localisation dans les messages
    for msg in reversed(state.messages):
        content = msg.content if hasattr(msg, "content") else ""
        if isinstance(content, str) and ("Paris" in content or "Lyon" in content):
            # Extraction simple, peut être améliorée
            for city in ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"]:
                if city in content:
                    location = city
                    break

    return {"location": location}


def build_weather_graph(use_mcp: bool = False) -> StateGraph:
    """
    Construit un graphe personnalisé pour l'agent météo.

    Architecture :
        START -> agent -> extract_location -> [should_continue]
                                                -> tools -> agent
                                                -> END

    Args:
        use_mcp: Si True, ajoute les outils MCP

    Returns:
        StateGraph compilé
    """
    workflow = StateGraph(WeatherState)

    # Définir les tools
    tools = [get_weather_for_location, get_user_location]

    if use_mcp:
        try:
            from app.mcp import get_mcp_tools

            mcp_tools = get_mcp_tools()
            tools.extend(mcp_tools)
        except Exception:
            pass

    # Créer le node pour les outils
    tool_node = ToolNode(tools)

    # Ajouter les nodes
    workflow.add_node("agent", call_weather_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("extract_location", extract_location)

    # Définir le flow
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "extract_location")
    workflow.add_conditional_edges(
        "extract_location",
        should_continue_weather,
        {
            "tools": "tools",
            "end": END,
        },
    )
    workflow.add_edge("tools", "agent")

    # Compiler avec checkpointer
    checkpointer = get_default_checkpointer()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def ask_weather_graph(
    question: str, user_id: str = "1", use_mcp: bool = False
) -> WeatherGraphResponse:
    """
    Pose une question à l'agent météo implémenté avec StateGraph.

    Args:
        question: Question de l'utilisateur
        user_id: ID de l'utilisateur
        use_mcp: Utiliser les outils MCP

    Returns:
        WeatherGraphResponse avec la réponse
    """
    graph = build_weather_graph(use_mcp=use_mcp)

    config = {"configurable": {"thread_id": f"weather_graph_{user_id}"}}

    initial_state = WeatherState(
        messages=[HumanMessage(content=question)], user_id=user_id, location=None
    )

    result = graph.invoke(initial_state, config=config)

    # Extraire la réponse finale
    final_message = result.messages[-1]
    text = final_message.content if hasattr(final_message, "content") else str(final_message)

    return WeatherGraphResponse(
        text=text, location=result.location, steps=len(result.messages)
    )
