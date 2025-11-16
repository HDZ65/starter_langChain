"""Interface CLI pour l'agent MCP générique."""

import sys

from app.agents.mcp_agent import ask_mcp_agent


def main() -> None:
    """Point d'entrée principal de la CLI MCP."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.mcp_cli \"Votre question\" [--thread-id THREAD_ID]")
        print('Exemple: python -m app.mcp_cli "Liste les fichiers dans /tmp"')
        print(
            'Exemple avec thread: python -m app.mcp_cli "Quelle est la suite ?" --thread-id my_session'
        )
        print("\nNote: Assurez-vous de configurer les serveurs MCP dans mcp_servers.json")
        sys.exit(1)

    question = sys.argv[1]
    thread_id = "default"

    # Parse optional --thread-id argument
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--thread-id" and i + 1 < len(sys.argv):
            thread_id = sys.argv[i + 1]

    print(f"Question: {question}")
    print(f"Thread ID: {thread_id}")
    print("-" * 60)

    try:
        response = ask_mcp_agent(question, thread_id=thread_id)
        print(f"\n📊 Status: {response.status}")
        print(f"\n💬 Réponse:\n{response.text}")
    except ValueError as e:
        print(f"⚠️  Configuration MCP manquante: {e}")
        print("\n💡 Pour configurer MCP:")
        print("   1. cp mcp_servers.example.json mcp_servers.json")
        print("   2. Éditez mcp_servers.json pour activer les serveurs souhaités")
        print("   3. Voir MCP_SETUP.md pour plus de détails")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
