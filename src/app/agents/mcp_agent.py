"""Agent générique utilisant uniquement les outils MCP."""

from dataclasses import dataclass

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_agent

from app.llm.models import get_default_model
from app.memory.base_memory import get_default_checkpointer
from app.mcp import get_mcp_tools


@dataclass
class MCPResponse:
    """Format de réponse structurée de l'agent MCP."""

    text: str
    status: str = "success"


SYSTEM_PROMPT_MCP = """Tu es un assistant intelligent qui a accès à divers outils via MCP.

Ton rôle :
- Utiliser les outils disponibles pour accomplir les tâches demandées
- Répondre de manière précise et utile
- Expliquer clairement les actions entreprises

Ton comportement :
- Analyser la demande de l'utilisateur
- Choisir les bons outils pour répondre
- Fournir des résultats clairs et structurés
- Être proactif dans l'utilisation des outils
"""


def build_mcp_agent(additional_tools: list[BaseTool] | None = None):
    """
    Construit un agent générique utilisant les outils MCP.

    Args:
        additional_tools: Liste optionnelle d'outils supplémentaires à ajouter

    Returns:
        Agent LangGraph configuré avec les outils MCP
    """
    model = get_default_model()
    checkpointer = get_default_checkpointer()

    # Charger les outils MCP
    tools = get_mcp_tools()

    # Ajouter les outils supplémentaires si fournis
    if additional_tools:
        tools.extend(additional_tools)

    # Si aucun outil n'est disponible, lancer une erreur
    if not tools:
        raise ValueError(
            "Aucun outil MCP disponible. "
            "Veuillez configurer les serveurs MCP dans mcp_servers.json"
        )

    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer,
        system_prompt=SYSTEM_PROMPT_MCP,
        response_format=MCPResponse,
    )

    return agent


def ask_mcp_agent(question: str, thread_id: str = "default") -> MCPResponse:
    """
    Pose une question à l'agent MCP.

    Args:
        question: Question de l'utilisateur
        thread_id: Identifiant du thread de conversation

    Returns:
        MCPResponse: Réponse structurée de l'agent
    """
    agent = build_mcp_agent()

    # Configuration avec thread_id pour la mémoire
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # Invocation de l'agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )

    return result["structured_response"]
