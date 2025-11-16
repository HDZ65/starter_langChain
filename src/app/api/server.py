"""API HTTP avec FastAPI pour l'agent météo.

Usage:
    uvicorn app.api.server:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.weather_agent import WeatherResponse, ask_weather

app = FastAPI(
    title="LangChain Weather Agent API",
    description="API pour interroger l'agent météo",
    version="0.1.0",
)


class WeatherRequest(BaseModel):
    """Modèle de requête pour l'endpoint météo."""

    question: str
    user_id: str = "1"


@app.get("/")
def read_root() -> dict[str, str]:
    """Endpoint racine."""
    return {
        "message": "LangChain Weather Agent API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.post("/weather", response_model=WeatherResponse)
def get_weather(request: WeatherRequest) -> WeatherResponse:
    """
    Interroge l'agent météo avec une question.

    Args:
        request: Question et identifiant utilisateur

    Returns:
        WeatherResponse: Réponse structurée de l'agent
    """
    response = ask_weather(question=request.question, user_id=request.user_id)
    return response


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
