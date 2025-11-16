"""Interface CLI pour les graphes LangGraph personnalisés."""

import sys

from app.graphs.research_agent import run_research
from app.graphs.simple_agent import run_simple_agent
from app.graphs.supervisor import run_supervisor
from app.tools.weather import get_user_location, get_weather_for_location


def main() -> None:
    """Point d'entrée principal de la CLI pour les graphes."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.graph_cli <graph_type> \"Votre question\"")
        print("\nTypes de graphes disponibles :")
        print("  simple      - Agent simple avec outils")
        print("  research    - Workflow de recherche multi-étapes")
        print("  supervisor  - Multi-agents avec superviseur")
        print("\nExemples :")
        print('  python -m app.graph_cli simple "Quel temps fait-il à Paris ?"')
        print('  python -m app.graph_cli research "Quelle est l\'histoire de Python ?"')
        print('  python -m app.graph_cli supervisor "Crée un tutoriel FastAPI"')
        sys.exit(1)

    graph_type = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else ""

    if not question:
        print("❌ Erreur : Question manquante")
        sys.exit(1)

    print(f"Type de graphe : {graph_type}")
    print(f"Question : {question}")
    print("=" * 70)
    print()

    try:
        if graph_type == "simple":
            print("🤖 Exécution de l'agent simple avec outils météo...\n")
            tools = [get_weather_for_location, get_user_location]
            response = run_simple_agent(question, tools=tools, thread_id="simple_cli")
            print("💬 Réponse :")
            print(response)

        elif graph_type == "research":
            print("🔍 Exécution du workflow de recherche...\n")
            result = run_research(question, thread_id="research_cli")
            print("📋 Requêtes générées :")
            for i, query in enumerate(result["queries"], 1):
                print(f"  {i}. {query}")
            print(f"\n📊 Notes collectées : {result['notes_count']}")
            print("\n💬 Réponse finale :")
            print(result["answer"])

        elif graph_type == "supervisor":
            print("👥 Exécution du workflow multi-agents supervisé...\n")
            result = run_supervisor(question, thread_id="supervisor_cli")
            print("🔧 Agents utilisés :")
            for agent in result["agents_used"]:
                print(f"  - {agent}")
            print("\n💬 Résultat final :")
            print(result["final_result"])
            print("\n📝 Détails par agent :")
            for agent, content in result["all_results"].items():
                print(f"\n--- {agent.upper()} ---")
                print(content[:200] + "..." if len(content) > 200 else content)

        else:
            print(f"❌ Type de graphe inconnu : {graph_type}")
            print("Types valides : simple, research, supervisor")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
