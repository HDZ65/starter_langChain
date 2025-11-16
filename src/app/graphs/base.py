"""Classes de base pour les états des graphes LangGraph."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """État de base pour un agent simple."""

    messages: Annotated[list, add_messages]
    """Liste des messages de la conversation."""


class ResearchState(TypedDict):
    """État pour un agent de recherche multi-étapes."""

    messages: Annotated[list, add_messages]
    """Liste des messages."""

    question: str
    """Question initiale de l'utilisateur."""

    research_notes: list[str]
    """Notes de recherche collectées."""

    search_queries: list[str]
    """Requêtes de recherche générées."""

    final_answer: str
    """Réponse finale synthétisée."""

    step: str
    """Étape actuelle du workflow."""


class SupervisorState(TypedDict):
    """État pour un système multi-agents avec superviseur."""

    messages: Annotated[list, add_messages]
    """Liste des messages."""

    next_agent: str
    """Prochain agent à exécuter."""

    task_description: str
    """Description de la tâche."""

    results: dict[str, str]
    """Résultats de chaque agent."""
