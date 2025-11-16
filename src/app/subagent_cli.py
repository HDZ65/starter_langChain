"""Interface CLI pour tester les subagents et la délégation."""

import sys

from app.subagents.coordinator import delegate_task
from app.subagents.registry import clear_registry, list_subagents, register_subagent
from app.subagents.specialized import get_default_subagents


def main() -> None:
    """Point d'entrée principal de la CLI pour les subagents."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.subagent_cli \"Votre tâche\"")
        print("\nExemples :")
        print('  python -m app.subagent_cli "Recherche sur l\'IA quantique"')
        print('  python -m app.subagent_cli "Crée une fonction Python pour trier une liste"')
        print('  python -m app.subagent_cli "Analyse les tendances du marché tech"')
        print("\nNote: Le coordinateur choisira automatiquement le meilleur subagent")
        print("      ou traitera la tâche directement si elle est simple.")
        sys.exit(1)

    task = sys.argv[1]

    print("=" * 70)
    print("🤖 SYSTÈME DE DÉLÉGATION AVEC SUBAGENTS")
    print("=" * 70)
    print(f"\n📋 Tâche : {task}\n")

    # Enregistrer les subagents par défaut
    clear_registry()
    for subagent in get_default_subagents():
        register_subagent(subagent)

    # Afficher les subagents disponibles
    print("🔧 Subagents disponibles :")
    for subagent in list_subagents():
        print(f"  • {subagent.name}: {subagent.description[:80]}...")

    print("\n" + "=" * 70)
    print("⚙️  Analyse et délégation en cours...\n")
    print("=" * 70 + "\n")

    try:
        result = delegate_task(task, thread_id="cli_session")

        print("✅ RÉSULTAT :\n")
        print(result)
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
