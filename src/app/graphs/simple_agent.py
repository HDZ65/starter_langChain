"""Graphe LangGraph simple avec agent conversationnel.

Exemple d'utilisation de StateGraph pour créer un agent avec :
- Node de réflexion
- Node d'action avec outils
- Conditions pour continuer ou terminer
"""

from typing import Literal

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.graphs.base import AgentState
from app.llm.models import get_default_model
from app.memory.base_memory import get_default_checkpointer


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Détermine si l'agent doit continuer avec des outils ou terminer.

    Args:
        state: État actuel du graphe

    Returns:
        "tools" si des outils doivent être appelés, "end" sinon
    """
    messages = state["messages"]
    last_message = messages[-1]

    # Si le dernier message a des tool_calls, continuer avec les outils
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


def call_model(state: AgentState) -> AgentState:
    """
    Node qui appelle le modèle LLM.

    Args:
        state: État actuel

    Returns:
        État mis à jour avec la réponse du modèle
    """
    messages = state["messages"]
    model = get_default_model()

    # Bind tools to model if available in state
    response = model.invoke(messages)

    return {"messages": [response]}


def build_simple_graph(tools: list[BaseTool] | None = None) -> StateGraph:
    """
    Construit un graphe LangGraph simple avec agent et outils.

    Architecture du graphe :
        START -> agent -> [should_continue] -> tools -> agent -> END
                                            -> END

    Args:
        tools: Liste optionnelle d'outils à donner à l'agent

    Returns:
        StateGraph compilé et prêt à être utilisé

    Exemple:
        >>> from app.tools.weather import get_weather_for_location
        >>> graph = build_simple_graph(tools=[get_weather_for_location])
        >>> result = graph.invoke(
        ...     {"messages": [HumanMessage(content="Quel temps fait-il à Paris ?")]},
        ...     config={"configurable": {"thread_id": "1"}}
        ... )
        >>> print(result["messages"][-1].content)
    """
    # Créer le graphe
    workflow = StateGraph(AgentState)

    # Définir le node pour l'agent
    model = get_default_model()
    if tools:
        model = model.bind_tools(tools)

    def agent_node(state: AgentState) -> AgentState:
        """Node agent qui appelle le modèle."""
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    # Ajouter les nodes
    workflow.add_node("agent", agent_node)

    if tools:
        # Créer le node pour les outils
        tool_node = ToolNode(tools)
        workflow.add_node("tools", tool_node)

        # Définir les edges
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END,
            },
        )
        workflow.add_edge("tools", "agent")
    else:
        # Pas d'outils, juste un agent simple
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)

    # Compiler avec checkpointer pour la mémoire
    checkpointer = get_default_checkpointer()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def run_simple_agent(
    question: str, tools: list[BaseTool] | None = None, thread_id: str = "default"
) -> str:
    """
    Exécute un agent simple avec une question.

    Args:
        question: Question de l'utilisateur
        tools: Outils optionnels pour l'agent
        thread_id: ID du thread pour la mémoire conversationnelle

    Returns:
        Réponse de l'agent
    """
    graph = build_simple_graph(tools=tools)

    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    return result["messages"][-1].content
