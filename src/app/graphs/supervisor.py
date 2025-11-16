"""Pattern superviseur multi-agents avec LangGraph.

Le superviseur délègue les tâches à différents agents spécialisés :
- Recherche web
- Analyse de code
- Rédaction
- etc.
"""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from app.graphs.base import SupervisorState
from app.llm.models import get_default_model
from app.memory.base_memory import get_default_checkpointer


class RouterDecision(BaseModel):
    """Décision du superviseur sur le prochain agent."""

    next_agent: Literal["researcher", "coder", "writer", "FINISH"]
    """Nom du prochain agent à exécuter ou FINISH."""

    reasoning: str
    """Raisonnement derrière la décision."""


SUPERVISOR_PROMPT = """Tu es un superviseur qui délègue des tâches à des agents spécialisés.

Agents disponibles :
- researcher : Expert en recherche d'information et synthèse
- coder : Expert en programmation et analyse de code
- writer : Expert en rédaction et communication

Tâche actuelle : {task}

Historique des résultats :
{results}

Messages :
{messages}

Détermine quel agent doit travailler ensuite, ou si la tâche est terminée (FINISH).
"""


def supervisor_node(state: SupervisorState) -> SupervisorState:
    """
    Node superviseur qui décide quel agent exécuter ensuite.

    Args:
        state: État actuel

    Returns:
        État avec le prochain agent à exécuter
    """
    model = get_default_model()

    # Construire le prompt avec le contexte
    task = state.get("task_description", "")
    results = state.get("results", {})
    messages = state.get("messages", [])

    results_str = "\n".join([f"- {agent}: {result}" for agent, result in results.items()])
    if not results_str:
        results_str = "Aucun résultat pour le moment"

    messages_str = "\n".join(
        [
            f"- {msg.type if hasattr(msg, 'type') else 'message'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
            for msg in messages[-3:]
        ]
    )

    prompt = SUPERVISOR_PROMPT.format(
        task=task, results=results_str, messages=messages_str or "Aucun message"
    )

    # Utiliser structured output pour avoir une décision claire
    structured_llm = model.with_structured_output(RouterDecision)
    decision = structured_llm.invoke([HumanMessage(content=prompt)])

    return {
        "next_agent": decision.next_agent,
        "messages": state["messages"]
        + [
            SystemMessage(
                content=f"Superviseur : {decision.reasoning} -> {decision.next_agent}"
            )
        ],
    }


def researcher_node(state: SupervisorState) -> SupervisorState:
    """
    Agent de recherche.

    Args:
        state: État actuel

    Returns:
        État avec le résultat de la recherche
    """
    model = get_default_model()
    task = state.get("task_description", "")

    prompt = f"""Tu es un expert en recherche. Effectue une recherche sur :
{task}

Fournis un résumé concis des informations clés."""

    response = model.invoke([HumanMessage(content=prompt)])

    results = state.get("results", {})
    results["researcher"] = response.content

    return {
        "results": results,
        "messages": state["messages"] + [response],
    }


def coder_node(state: SupervisorState) -> SupervisorState:
    """
    Agent de programmation.

    Args:
        state: État actuel

    Returns:
        État avec le code généré
    """
    model = get_default_model()
    task = state.get("task_description", "")

    prompt = f"""Tu es un expert en programmation. Travaille sur :
{task}

Fournis du code Python propre et bien commenté si pertinent."""

    response = model.invoke([HumanMessage(content=prompt)])

    results = state.get("results", {})
    results["coder"] = response.content

    return {
        "results": results,
        "messages": state["messages"] + [response],
    }


def writer_node(state: SupervisorState) -> SupervisorState:
    """
    Agent de rédaction.

    Args:
        state: État actuel

    Returns:
        État avec le contenu rédigé
    """
    model = get_default_model()
    task = state.get("task_description", "")
    results = state.get("results", {})

    # Le writer synthétise les résultats des autres agents
    context = "\n\n".join([f"{agent}:\n{result}" for agent, result in results.items()])

    prompt = f"""Tu es un expert en rédaction. Synthétise ces informations :

Tâche : {task}

Informations collectées :
{context}

Rédige une réponse finale claire et bien structurée en français."""

    response = model.invoke([HumanMessage(content=prompt)])

    results["writer"] = response.content

    return {
        "results": results,
        "messages": state["messages"] + [response],
    }


def route_supervisor(state: SupervisorState) -> Literal["researcher", "coder", "writer", "end"]:
    """
    Détermine le prochain agent à exécuter.

    Args:
        state: État actuel

    Returns:
        Nom du prochain agent ou "end"
    """
    next_agent = state.get("next_agent", "FINISH")

    if next_agent == "FINISH":
        return "end"
    return next_agent


def build_supervisor_graph() -> StateGraph:
    """
    Construit un graphe multi-agents avec superviseur.

    Architecture :
        START -> supervisor -> [researcher | coder | writer] -> supervisor -> END

    Returns:
        StateGraph compilé

    Exemple:
        >>> graph = build_supervisor_graph()
        >>> result = graph.invoke({
        ...     "messages": [HumanMessage(content="Crée un exemple de FastAPI")],
        ...     "task_description": "Créer un exemple d'API REST avec FastAPI",
        ...     "next_agent": "",
        ...     "results": {}
        ... })
        >>> print(result["results"]["writer"])
    """
    workflow = StateGraph(SupervisorState)

    # Ajouter les nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("writer", writer_node)

    # Définir le flow
    workflow.set_entry_point("supervisor")

    # Le superviseur route vers les agents
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "coder": "coder",
            "writer": "writer",
            "end": END,
        },
    )

    # Tous les agents retournent au superviseur
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("coder", "supervisor")
    workflow.add_edge("writer", "supervisor")

    # Compiler avec checkpointer
    checkpointer = get_default_checkpointer()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def run_supervisor(task: str, thread_id: str = "supervisor") -> dict:
    """
    Exécute un workflow supervisé multi-agents.

    Args:
        task: Description de la tâche
        thread_id: ID du thread

    Returns:
        Dictionnaire avec les résultats de tous les agents
    """
    graph = build_supervisor_graph()

    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "messages": [HumanMessage(content=task)],
        "task_description": task,
        "next_agent": "",
        "results": {},
    }

    result = graph.invoke(initial_state, config=config)

    return {
        "final_result": result.get("results", {}).get("writer", ""),
        "all_results": result.get("results", {}),
        "agents_used": list(result.get("results", {}).keys()),
    }
