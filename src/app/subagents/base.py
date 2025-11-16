"""Classes de base pour les subagents."""

from dataclasses import dataclass
from typing import Any, Callable

from langchain_core.tools import BaseTool


@dataclass
class SubAgent:
    """Définition d'un subagent spécialisé.

    Un subagent est un agent autonome qui peut être invoqué pour
    effectuer une tâche spécifique sans polluer le contexte principal.

    Attributes:
        name: Identifiant unique du subagent
        description: Description de ce que fait le subagent
        system_prompt: Instructions pour le subagent
        tools: Outils disponibles pour le subagent
        model_name: Nom du modèle à utiliser (optionnel)
        max_iterations: Nombre max d'itérations (défaut: 10)
        return_format: Format de retour attendu
    """

    name: str
    description: str
    system_prompt: str
    tools: list[BaseTool] | None = None
    model_name: str | None = None
    max_iterations: int = 10
    return_format: str = "concise_summary"

    def __post_init__(self) -> None:
        """Validation après initialisation."""
        if not self.name:
            raise ValueError("SubAgent name cannot be empty")
        if not self.description:
            raise ValueError("SubAgent description cannot be empty")
        if not self.system_prompt:
            raise ValueError("SubAgent system_prompt cannot be empty")


@dataclass
class SubAgentResult:
    """Résultat d'exécution d'un subagent.

    Attributes:
        subagent_name: Nom du subagent qui a produit ce résultat
        task: Tâche qui a été déléguée
        result: Résultat concis de l'exécution
        success: Si la tâche a réussi
        error: Message d'erreur si échec
        metadata: Métadonnées additionnelles (nombre d'étapes, etc.)
    """

    subagent_name: str
    task: str
    result: str
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def to_string(self) -> str:
        """Convertit le résultat en string formaté."""
        if not self.success:
            return f"❌ Erreur dans {self.subagent_name}: {self.error}"

        output = f"✅ Résultat de {self.subagent_name}:\n{self.result}"

        if self.metadata:
            steps = self.metadata.get("steps", 0)
            if steps:
                output += f"\n(Traité en {steps} étapes)"

        return output


@dataclass
class SubAgentTask:
    """Tâche à déléguer à un subagent.

    Attributes:
        subagent_name: Nom du subagent à utiliser
        task_description: Description détaillée de la tâche
        context: Contexte additionnel (optionnel)
    """

    subagent_name: str
    task_description: str
    context: dict[str, Any] | None = None
