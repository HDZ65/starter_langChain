"""Module de gestion des subagents pour délégation de tâches.

Les subagents permettent de :
- Déléguer du travail complexe pour garder le contexte principal propre
- Créer des agents spécialisés pour différents domaines
- Isoler les résultats intermédiaires
"""

from app.subagents.base import SubAgent, SubAgentResult
from app.subagents.coordinator import build_coordinator_agent, delegate_task
from app.subagents.registry import get_subagent, list_subagents, register_subagent

__all__ = [
    "SubAgent",
    "SubAgentResult",
    "build_coordinator_agent",
    "delegate_task",
    "get_subagent",
    "list_subagents",
    "register_subagent",
]
