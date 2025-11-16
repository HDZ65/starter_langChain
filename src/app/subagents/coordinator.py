"""Agent coordinateur qui délègue les tâches aux subagents."""

from typing import Annotated, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from app.llm.models import get_default_model
from app.memory.base_memory import get_default_checkpointer
from app.subagents.base import SubAgent, SubAgentResult, SubAgentTask
from app.subagents.registry import get_subagent, get_subagents_descriptions
from app.subagents.specialized import DEFAULT_SUBAGENTS, get_default_subagents


class CoordinatorState(BaseModel):
    """État du coordinateur."""

    messages: Annotated[list, add_messages]
    """Messages de la conversation."""

    current_task: str | None = None
    """Tâche actuelle à traiter."""

    delegated_tasks: list[SubAgentTask] = Field(default_factory=list)
    """Liste des tâches déléguées."""

    results: list[SubAgentResult] = Field(default_factory=list)
    """Résultats des subagents."""

    final_answer: str | None = None
    """Réponse finale synthétisée."""


class DelegationDecision(BaseModel):
    """Décision de délégation du coordinateur."""

    should_delegate: bool = Field(description="Si la tâche doit être déléguée à un subagent")
    subagent_name: str | None = Field(
        default=None, description="Nom du subagent à utiliser si délégation"
    )
    task_description: str | None = Field(
        default=None, description="Description de la tâche à déléguer"
    )
    reasoning: str = Field(description="Raisonnement de la décision")


def execute_subagent(subagent: SubAgent, task: str, user_id: str = "default") -> SubAgentResult:
    """
    Exécute un subagent avec une tâche donnée.

    Args:
        subagent: SubAgent à exécuter
        task: Description de la tâche
        user_id: ID utilisateur pour le thread

    Returns:
        SubAgentResult avec le résultat
    """
    try:
        # Construire un agent simple pour le subagent
        from app.graphs.simple_agent import build_simple_graph

        graph = build_simple_graph(tools=subagent.tools or [])

        # Créer le message système avec les instructions du subagent
        messages = [
            SystemMessage(content=subagent.system_prompt),
            HumanMessage(content=task),
        ]

        # Exécuter le subagent
        config = {"configurable": {"thread_id": f"subagent_{subagent.name}_{user_id}"}}

        result = graph.invoke({"messages": messages}, config=config)

        # Extraire le résultat
        final_message = result["messages"][-1]
        result_text = (
            final_message.content if hasattr(final_message, "content") else str(final_message)
        )

        return SubAgentResult(
            subagent_name=subagent.name,
            task=task,
            result=result_text,
            success=True,
            metadata={"steps": len(result["messages"])},
        )

    except Exception as e:
        return SubAgentResult(
            subagent_name=subagent.name,
            task=task,
            result="",
            success=False,
            error=str(e),
        )


@tool
def delegate_to_subagent(subagent_name: str, task: str) -> str:
    """
    Délègue une tâche à un subagent spécialisé.

    Args:
        subagent_name: Nom du subagent à utiliser
        task: Description de la tâche à effectuer

    Returns:
        Résultat concis de l'exécution du subagent
    """
    subagent = get_subagent(subagent_name)
    if not subagent:
        return f"❌ Erreur: Subagent '{subagent_name}' non trouvé."

    result = execute_subagent(subagent, task)
    return result.to_string()


def coordinator_decide(state: CoordinatorState) -> dict:
    """
    Node où le coordinateur décide s'il doit déléguer.

    Args:
        state: État actuel

    Returns:
        Mise à jour avec la décision
    """
    model = get_default_model()

    # Obtenir la liste des subagents disponibles
    subagents_desc = get_subagents_descriptions()

    prompt = f"""Tu es un coordinateur intelligent qui délègue des tâches à des subagents spécialisés.

{subagents_desc}

Tâche actuelle : {state.current_task or "Analyser le dernier message"}

Messages récents :
{state.messages[-3:] if state.messages else "Aucun"}

Décide si tu dois déléguer cette tâche à un subagent ou la traiter toi-même.
Critères de délégation :
- Tâche complexe nécessitant plusieurs étapes ? → Déléguer
- Besoin d'expertise spécifique ? → Déléguer
- Question simple et directe ? → Traiter soi-même

Si tu délègues, choisis le subagent le plus approprié."""

    # Utiliser structured output pour avoir une décision claire
    structured_llm = model.with_structured_output(DelegationDecision)
    decision = structured_llm.invoke([HumanMessage(content=prompt)])

    new_messages = [
        SystemMessage(content=f"Décision: {decision.reasoning} → {decision.subagent_name or 'self'}")
    ]

    return {"messages": new_messages}


def should_delegate(state: CoordinatorState) -> Literal["delegate", "answer_directly"]:
    """
    Détermine si on doit déléguer ou répondre directement.

    Args:
        state: État actuel

    Returns:
        "delegate" ou "answer_directly"
    """
    # Analyser le dernier message système pour la décision
    if state.messages:
        last_msg = state.messages[-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        if "→ self" in content:
            return "answer_directly"

    return "delegate"


def delegate_node(state: CoordinatorState) -> dict:
    """
    Node qui délègue au subagent approprié.

    Args:
        state: État actuel

    Returns:
        État avec le résultat du subagent
    """
    # Extraire le nom du subagent de la décision
    last_msg = state.messages[-1]
    content = last_msg.content if hasattr(last_msg, "content") else ""

    # Parser la décision (format: "... → subagent_name")
    subagent_name = None
    if "→" in content:
        parts = content.split("→")
        if len(parts) >= 2:
            subagent_name = parts[-1].strip()

    if not subagent_name or subagent_name == "self":
        return {"messages": [SystemMessage(content="Pas de délégation nécessaire")]}

    # Obtenir le subagent
    subagent = get_subagent(subagent_name)
    if not subagent:
        return {"messages": [SystemMessage(content=f"Subagent {subagent_name} non trouvé")]}

    # Exécuter le subagent
    task = state.current_task or "Traiter la demande utilisateur"
    result = execute_subagent(subagent, task)

    # Ajouter le résultat
    new_results = state.results.copy()
    new_results.append(result)

    return {"results": new_results, "messages": [SystemMessage(content=result.to_string())]}


def answer_directly_node(state: CoordinatorState) -> dict:
    """
    Node où le coordinateur répond directement.

    Args:
        state: État actuel

    Returns:
        État avec la réponse
    """
    model = get_default_model()

    # Répondre directement
    response = model.invoke(state.messages)

    return {"messages": [response], "final_answer": response.content}


def build_coordinator_agent() -> StateGraph:
    """
    Construit un agent coordinateur avec système de délégation.

    Architecture:
        START → decide → [should_delegate]
                           ├─ delegate → END
                           └─ answer_directly → END

    Returns:
        StateGraph compilé
    """
    workflow = StateGraph(CoordinatorState)

    # Ajouter les nodes
    workflow.add_node("decide", coordinator_decide)
    workflow.add_node("delegate", delegate_node)
    workflow.add_node("answer_directly", answer_directly_node)

    # Définir le flow
    workflow.set_entry_point("decide")
    workflow.add_conditional_edges(
        "decide",
        should_delegate,
        {
            "delegate": "delegate",
            "answer_directly": "answer_directly",
        },
    )
    workflow.add_edge("delegate", END)
    workflow.add_edge("answer_directly", END)

    # Compiler avec checkpointer
    checkpointer = get_default_checkpointer()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def delegate_task(
    task: str, available_subagents: list[SubAgent] | None = None, thread_id: str = "coordinator"
) -> str:
    """
    Délègue une tâche via le coordinateur.

    Args:
        task: Tâche à effectuer
        available_subagents: Subagents à utiliser (défaut: tous les subagents par défaut)
        thread_id: ID du thread pour la mémoire

    Returns:
        Résultat de la tâche (délégué ou traité directement)
    """
    # Enregistrer les subagents disponibles
    from app.subagents.registry import clear_registry, register_subagent

    clear_registry()

    subagents = available_subagents or get_default_subagents()
    for subagent in subagents:
        register_subagent(subagent)

    # Construire et exécuter le coordinateur
    graph = build_coordinator_agent()

    config = {"configurable": {"thread_id": thread_id}}

    initial_state = CoordinatorState(
        messages=[HumanMessage(content=task)], current_task=task, delegated_tasks=[], results=[]
    )

    result = graph.invoke(initial_state, config=config)

    # Retourner le résultat
    if result.get("final_answer"):
        return result["final_answer"]

    # Sinon retourner le dernier message
    if result.get("messages"):
        last_msg = result["messages"][-1]
        return last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    return "Aucun résultat"
