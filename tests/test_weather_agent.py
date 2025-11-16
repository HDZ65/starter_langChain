"""Tests pour l'agent météo."""

import pytest

from app.agents.weather_agent import ask_weather


def test_ask_weather_returns_response() -> None:
    """Vérifie que ask_weather retourne une réponse non vide."""
    response = ask_weather("Quel temps fait-il ?", user_id="test")

    assert response.text is not None
    assert isinstance(response.text, str)
    assert len(response.text) > 0


def test_ask_weather_with_different_user() -> None:
    """Vérifie que l'agent fonctionne avec différents user_id."""
    response = ask_weather("Météo du jour ?", user_id="demo")

    assert response.text is not None
    assert isinstance(response.text, str)


def test_weather_response_structure() -> None:
    """Vérifie la structure de la réponse."""
    response = ask_weather("Quel temps fait-il à Paris ?", user_id="1")

    assert hasattr(response, "text")
    assert hasattr(response, "location")
    assert isinstance(response.text, str)
