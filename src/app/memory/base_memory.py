"""Gestion de la mémoire avec checkpointers."""

from langgraph.checkpoint.memory import MemorySaver


def get_default_checkpointer() -> MemorySaver:
    """
    Retourne le checkpointer par défaut pour sauvegarder l'état des conversations.

    Returns:
        MemorySaver: Checkpointer en mémoire
    """
    return MemorySaver()
