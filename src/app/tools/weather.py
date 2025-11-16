"""Outils météo pour l'agent."""

from dataclasses import dataclass

from langchain_core.tools import tool
from langgraph.prebuilt.tool_runtime import ToolRuntime


@dataclass
class Context:
    """Contexte utilisateur pour les outils."""

    user_id: str


@tool
def get_weather_for_location(city: str) -> str:
    """
    Obtient la météo pour une ville donnée.

    Args:
        city: Nom de la ville

    Returns:
        str: Description de la météo
    """
    # Simulation de données météo
    weather_data = {
        "Paris": "Ensoleillé, 22°C, vent léger du nord",
        "Lyon": "Nuageux, 18°C, vent modéré",
        "Marseille": "Ensoleillé, 25°C, vent faible",
        "Toulouse": "Partiellement nuageux, 20°C",
        "Nice": "Ensoleillé, 24°C, brise marine",
    }

    if city in weather_data:
        return f"Météo à {city}: {weather_data[city]}"
    else:
        return f"Météo à {city}: Ensoleillé, 21°C (données simulées)"


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """
    Récupère la localisation de l'utilisateur depuis le contexte.

    Args:
        runtime: Runtime avec le contexte utilisateur

    Returns:
        str: Ville de l'utilisateur
    """
    # Simulation : on associe des villes aux user_ids
    user_locations = {
        "1": "Paris",
        "test": "Lyon",
        "demo": "Marseille",
    }

    user_id = runtime.context.user_id
    location = user_locations.get(user_id, "Paris")

    return f"L'utilisateur est situé à {location}"
