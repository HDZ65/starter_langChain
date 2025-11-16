"""Tests pour les graphes LangGraph personnalisés."""

import pytest
from langchain_core.messages import HumanMessage

from app.graphs.research_agent import build_research_graph, run_research
from app.graphs.simple_agent import build_simple_graph, run_simple_agent
from app.graphs.supervisor import build_supervisor_graph, run_supervisor
from app.tools.weather import get_weather_for_location


def test_simple_graph_builds() -> None:
    """Vérifie que le graphe simple se construit correctement."""
    graph = build_simple_graph()
    assert graph is not None


def test_simple_graph_with_tools() -> None:
    """Vérifie que le graphe simple fonctionne avec des outils."""
    tools = [get_weather_for_location]
    graph = build_simple_graph(tools=tools)

    result = graph.invoke(
        {"messages": [HumanMessage(content="Quel temps fait-il à Paris ?")]},
        config={"configurable": {"thread_id": "test_simple"}},
    )

    assert "messages" in result
    assert len(result["messages"]) > 0


def test_run_simple_agent() -> None:
    """Vérifie que run_simple_agent retourne une réponse."""
    response = run_simple_agent(
        "Bonjour, comment ça va ?", tools=None, thread_id="test_run"
    )

    assert isinstance(response, str)
    assert len(response) > 0


def test_research_graph_builds() -> None:
    """Vérifie que le graphe de recherche se construit."""
    graph = build_research_graph()
    assert graph is not None


def test_run_research() -> None:
    """Vérifie que run_research retourne des résultats."""
    result = run_research("Test question", thread_id="test_research")

    assert "answer" in result
    assert "queries" in result
    assert "notes_count" in result
    assert isinstance(result["answer"], str)
    assert isinstance(result["queries"], list)


def test_supervisor_graph_builds() -> None:
    """Vérifie que le graphe superviseur se construit."""
    graph = build_supervisor_graph()
    assert graph is not None


def test_run_supervisor() -> None:
    """Vérifie que run_supervisor retourne des résultats."""
    result = run_supervisor("Tâche de test", thread_id="test_supervisor")

    assert "final_result" in result
    assert "all_results" in result
    assert "agents_used" in result
    assert isinstance(result["agents_used"], list)
