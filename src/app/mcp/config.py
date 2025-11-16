"""Configuration des serveurs MCP depuis un fichier JSON."""

import json
import os
from pathlib import Path
from typing import Any

from mcp import StdioServerParameters

from app.settings import settings


def load_mcp_servers_config(config_path: str | None = None) -> dict[str, StdioServerParameters]:
    """
    Charge la configuration des serveurs MCP depuis un fichier JSON.

    Args:
        config_path: Chemin vers le fichier de configuration JSON.
                     Si None, cherche mcp_servers.json à la racine du projet.

    Returns:
        dict[str, StdioServerParameters]: Dictionnaire des paramètres de serveurs MCP
    """
    if config_path is None:
        # Chercher à la racine du projet
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = str(project_root / "mcp_servers.json")

    if not os.path.exists(config_path):
        # Retourner une configuration vide si le fichier n'existe pas
        return {}

    with open(config_path, "r") as f:
        config = json.load(f)

    servers: dict[str, StdioServerParameters] = {}

    for server_name, server_config in config.get("mcpServers", {}).items():
        # Remplacer les variables d'environnement dans env
        env = server_config.get("env", {})
        resolved_env = {}
        for key, value in env.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                resolved_env[key] = os.getenv(env_var, "")
            else:
                resolved_env[key] = value

        servers[server_name] = StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"],
            env=resolved_env if resolved_env else None,
        )

    return servers


def get_default_mcp_servers() -> dict[str, StdioServerParameters]:
    """
    Retourne une configuration de serveurs MCP par défaut.

    Returns:
        dict[str, StdioServerParameters]: Configuration par défaut des serveurs
    """
    servers: dict[str, StdioServerParameters] = {}

    # Exemple: serveur filesystem (décommenter pour activer)
    # servers["filesystem"] = StdioServerParameters(
    #     command="npx",
    #     args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    # )

    # Si une clé GitHub est disponible, ajouter le serveur GitHub
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        servers["github"] = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": github_token},
        )

    # Si une clé Brave Search est disponible, ajouter le serveur
    brave_api_key = os.getenv("BRAVE_API_KEY")
    if brave_api_key:
        servers["brave-search"] = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": brave_api_key},
        )

    return servers
