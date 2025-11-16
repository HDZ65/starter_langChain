"""Tests pour le système de subagents."""

import pytest

from app.subagents.base import SubAgent, SubAgentResult
from app.subagents.coordinator import delegate_task, execute_subagent
from app.subagents.registry import (
    clear_registry,
    get_subagent,
    list_subagents,
    register_subagent,
    unregister_subagent,
)
from app.subagents.specialized import (
    code_expert_subagent,
    get_default_subagents,
    quick_helper_subagent,
    research_subagent,
)


def test_subagent_creation() -> None:
    """Vérifie qu'on peut créer un SubAgent."""
    subagent = SubAgent(
        name="test-agent",
        description="Agent de test",
        system_prompt="Tu es un agent de test",
    )

    assert subagent.name == "test-agent"
    assert subagent.description == "Agent de test"
    assert subagent.max_iterations == 10


def test_subagent_validation() -> None:
    """Vérifie la validation des SubAgents."""
    with pytest.raises(ValueError):
        SubAgent(name="", description="Test", system_prompt="Test")

    with pytest.raises(ValueError):
        SubAgent(name="test", description="", system_prompt="Test")


def test_registry() -> None:
    """Vérifie le registre de subagents."""
    clear_registry()

    subagent = SubAgent(
        name="registry-test", description="Test", system_prompt="Test"
    )

    # Enregistrement
    register_subagent(subagent)
    assert len(list_subagents()) == 1

    # Récupération
    retrieved = get_subagent("registry-test")
    assert retrieved is not None
    assert retrieved.name == "registry-test"

    # Désenregistrement
    assert unregister_subagent("registry-test") is True
    assert len(list_subagents()) == 0


def test_default_subagents() -> None:
    """Vérifie que les subagents par défaut existent."""
    subagents = get_default_subagents()

    assert len(subagents) >= 4
    assert any(s.name == "research-specialist" for s in subagents)
    assert any(s.name == "code-expert" for s in subagents)
    assert any(s.name == "quick-helper" for s in subagents)


def test_execute_subagent() -> None:
    """Vérifie l'exécution d'un subagent."""
    result = execute_subagent(
        quick_helper_subagent, "Quelle est la capitale de la France ?", user_id="test"
    )

    assert isinstance(result, SubAgentResult)
    assert result.subagent_name == "quick-helper"
    assert result.task == "Quelle est la capitale de la France ?"
    assert len(result.result) > 0


def test_subagent_result_to_string() -> None:
    """Vérifie la conversion en string des résultats."""
    result = SubAgentResult(
        subagent_name="test",
        task="test task",
        result="Test result",
        success=True,
        metadata={"steps": 3},
    )

    string_result = result.to_string()
    assert "test" in string_result
    assert "Test result" in string_result
    assert "3 étapes" in string_result


def test_delegate_task() -> None:
    """Vérifie la délégation de tâches."""
    result = delegate_task(
        "Quelle est la capitale du Japon ?",
        available_subagents=[quick_helper_subagent],
        thread_id="test_delegate",
    )

    assert isinstance(result, str)
    assert len(result) > 0
