"""Client MCP pour charger et gérer les serveurs MCP."""

import asyncio
from typing import Any

from langchain_core.tools import BaseTool
from langchain_mcp_adapters import MultiServerMCPClient, load_mcp_tools
from mcp import StdioServerParameters

from app.mcp.config import get_default_mcp_servers, load_mcp_servers_config
from app.settings import settings


class MCPClient:
    """Client pour gérer les connexions aux serveurs MCP."""

    def __init__(self, config_path: str | None = None) -> None:
        """
        Initialise le client MCP.

        Args:
            config_path: Chemin optionnel vers un fichier de configuration JSON
        """
        self._client: MultiServerMCPClient | None = None
        self._tools: list[BaseTool] = []
        self._config_path = config_path

    async def _initialize(self) -> None:
        """Initialise la connexion aux serveurs MCP de manière asynchrone."""
        if self._client is not None:
            return

        # Charger la configuration des serveurs MCP
        if self._config_path:
            servers = load_mcp_servers_config(self._config_path)
        else:
            # Essayer de charger depuis mcp_servers.json, sinon utiliser la config par défaut
            try:
                servers = load_mcp_servers_config()
            except Exception:
                servers = get_default_mcp_servers()

        # Si aucun serveur n'est configuré, ne pas initialiser
        if not servers:
            self._tools = []
            return

        # Créer le client multi-serveurs
        self._client = MultiServerMCPClient(servers)

        # Démarrer les sessions et charger les outils
        async with self._client as session:
            self._tools = await load_mcp_tools(session)

    def get_tools(self) -> list[BaseTool]:
        """
        Récupère les outils MCP disponibles.

        Returns:
            list[BaseTool]: Liste des outils LangChain chargés depuis MCP
        """
        # Exécuter l'initialisation si nécessaire
        if not self._tools:
            asyncio.run(self._initialize())

        return self._tools

    async def get_tools_async(self) -> list[BaseTool]:
        """
        Récupère les outils MCP disponibles de manière asynchrone.

        Returns:
            list[BaseTool]: Liste des outils LangChain chargés depuis MCP
        """
        await self._initialize()
        return self._tools


# Instance globale du client MCP
_mcp_client = MCPClient()


def get_mcp_tools() -> list[BaseTool]:
    """
    Fonction helper pour récupérer les outils MCP.

    Returns:
        list[BaseTool]: Liste des outils MCP disponibles
    """
    return _mcp_client.get_tools()


async def get_mcp_tools_async() -> list[BaseTool]:
    """
    Fonction helper asynchrone pour récupérer les outils MCP.

    Returns:
        list[BaseTool]: Liste des outils MCP disponibles
    """
    return await _mcp_client.get_tools_async()
