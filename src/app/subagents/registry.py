"""Registre des subagents disponibles."""

from typing import Dict

from app.subagents.base import SubAgent

# Registre global des subagents
_SUBAGENTS_REGISTRY: Dict[str, SubAgent] = {}


def register_subagent(subagent: SubAgent) -> None:
    """
    Enregistre un subagent dans le registre global.

    Args:
        subagent: SubAgent à enregistrer

    Raises:
        ValueError: Si un subagent avec ce nom existe déjà
    """
    if subagent.name in _SUBAGENTS_REGISTRY:
        raise ValueError(f"SubAgent '{subagent.name}' is already registered")

    _SUBAGENTS_REGISTRY[subagent.name] = subagent


def get_subagent(name: str) -> SubAgent | None:
    """
    Récupère un subagent par son nom.

    Args:
        name: Nom du subagent

    Returns:
        SubAgent si trouvé, None sinon
    """
    return _SUBAGENTS_REGISTRY.get(name)


def list_subagents() -> list[SubAgent]:
    """
    Liste tous les subagents enregistrés.

    Returns:
        Liste de tous les subagents
    """
    return list(_SUBAGENTS_REGISTRY.values())


def unregister_subagent(name: str) -> bool:
    """
    Supprime un subagent du registre.

    Args:
        name: Nom du subagent à supprimer

    Returns:
        True si supprimé, False si non trouvé
    """
    if name in _SUBAGENTS_REGISTRY:
        del _SUBAGENTS_REGISTRY[name]
        return True
    return False


def clear_registry() -> None:
    """Vide le registre de tous les subagents."""
    _SUBAGENTS_REGISTRY.clear()


def get_subagents_descriptions() -> str:
    """
    Retourne une description formatée de tous les subagents.

    Returns:
        String avec la liste des subagents et leurs descriptions
    """
    if not _SUBAGENTS_REGISTRY:
        return "Aucun subagent disponible."

    descriptions = ["Subagents disponibles :\n"]
    for name, subagent in _SUBAGENTS_REGISTRY.items():
        descriptions.append(f"- {name}: {subagent.description}")

    return "\n".join(descriptions)
