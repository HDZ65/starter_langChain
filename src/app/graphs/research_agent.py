"""Agent de recherche multi-étapes avec LangGraph.

Workflow de recherche :
1. Analyser la question
2. Générer des requêtes de recherche
3. Effectuer les recherches
4. Synthétiser les résultats
5. Générer la réponse finale
"""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.graphs.base import ResearchState
from app.llm.models import get_default_model
from app.memory.base_memory import get_default_checkpointer


def analyze_question(state: ResearchState) -> ResearchState:
    """
    Analyse la question et initialise le workflow.

    Args:
        state: État actuel

    Returns:
        État mis à jour
    """
    question = state.get("question", "")

    if not question:
        # Extraire la question du dernier message
        messages = state.get("messages", [])
        if messages:
            question = messages[-1].content if hasattr(messages[-1], "content") else ""

    return {
        "question": question,
        "step": "generate_queries",
        "messages": state.get("messages", [])
        + [SystemMessage(content=f"Question analysée : {question}")],
    }


def generate_search_queries(state: ResearchState) -> ResearchState:
    """
    Génère des requêtes de recherche basées sur la question.

    Args:
        state: État actuel

    Returns:
        État avec les requêtes générées
    """
    model = get_default_model()
    question = state["question"]

    prompt = f"""Génère 3 requêtes de recherche pour répondre à cette question :
Question : {question}

Retourne uniquement les 3 requêtes, une par ligne, sans numérotation."""

    response = model.invoke([HumanMessage(content=prompt)])
    queries = [q.strip() for q in response.content.split("\n") if q.strip()][:3]

    return {
        "search_queries": queries,
        "step": "search",
        "messages": state["messages"]
        + [SystemMessage(content=f"Requêtes générées : {', '.join(queries)}")],
    }


def perform_research(state: ResearchState) -> ResearchState:
    """
    Effectue les recherches (simulation ici, peut être connecté à des vraies APIs).

    Args:
        state: État actuel

    Returns:
        État avec les notes de recherche
    """
    queries = state["search_queries"]

    # Simulation de recherche
    # En production, utiliser des outils MCP (Brave Search, etc.)
    research_notes = []
    for query in queries:
        note = f"Résultats simulés pour : {query}\n- Information 1\n- Information 2"
        research_notes.append(note)

    return {
        "research_notes": research_notes,
        "step": "synthesize",
        "messages": state["messages"]
        + [SystemMessage(content=f"{len(research_notes)} recherches effectuées")],
    }


def synthesize_answer(state: ResearchState) -> ResearchState:
    """
    Synthétise les notes de recherche en une réponse finale.

    Args:
        state: État actuel

    Returns:
        État avec la réponse finale
    """
    model = get_default_model()
    question = state["question"]
    notes = state["research_notes"]

    prompt = f"""Synthétise ces informations pour répondre à la question.

Question : {question}

Informations collectées :
{chr(10).join(notes)}

Fournis une réponse claire et concise en français."""

    response = model.invoke([HumanMessage(content=prompt)])
    final_answer = response.content

    return {
        "final_answer": final_answer,
        "step": "done",
        "messages": state["messages"] + [response],
    }


def route_next_step(state: ResearchState) -> Literal["generate_queries", "search", "synthesize", "end"]:
    """
    Détermine la prochaine étape du workflow.

    Args:
        state: État actuel

    Returns:
        Nom de la prochaine étape
    """
    step = state.get("step", "generate_queries")

    if step == "generate_queries":
        return "generate_queries"
    elif step == "search":
        return "search"
    elif step == "synthesize":
        return "synthesize"
    else:
        return "end"


def build_research_graph() -> StateGraph:
    """
    Construit un graphe de recherche multi-étapes.

    Architecture :
        START -> analyze -> generate_queries -> search -> synthesize -> END

    Returns:
        StateGraph compilé

    Exemple:
        >>> graph = build_research_graph()
        >>> result = graph.invoke(
        ...     {
        ...         "messages": [HumanMessage(content="Quelle est l'histoire de Python ?")],
        ...         "question": "",
        ...         "research_notes": [],
        ...         "search_queries": [],
        ...         "final_answer": "",
        ...         "step": "start"
        ...     }
        ... )
        >>> print(result["final_answer"])
    """
    workflow = StateGraph(ResearchState)

    # Ajouter les nodes
    workflow.add_node("analyze", analyze_question)
    workflow.add_node("generate_queries", generate_search_queries)
    workflow.add_node("search", perform_research)
    workflow.add_node("synthesize", synthesize_answer)

    # Définir le flow
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "generate_queries")
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "synthesize")
    workflow.add_edge("synthesize", END)

    # Compiler avec checkpointer
    checkpointer = get_default_checkpointer()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def run_research(question: str, thread_id: str = "research") -> dict:
    """
    Exécute un workflow de recherche complet.

    Args:
        question: Question de recherche
        thread_id: ID du thread

    Returns:
        Dictionnaire avec la réponse finale et les métadonnées
    """
    graph = build_research_graph()

    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "messages": [HumanMessage(content=question)],
        "question": question,
        "research_notes": [],
        "search_queries": [],
        "final_answer": "",
        "step": "start",
    }

    result = graph.invoke(initial_state, config=config)

    return {
        "answer": result.get("final_answer", ""),
        "queries": result.get("search_queries", []),
        "notes_count": len(result.get("research_notes", [])),
    }
