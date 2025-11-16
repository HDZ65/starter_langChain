"""Interface CLI pour l'agent météo."""

import sys

from app.agents.weather_agent import ask_weather


def main() -> None:
    """Point d'entrée principal de la CLI."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli \"Votre question\" [--user-id USER_ID] [--use-mcp]")
        print('Exemple: python -m app.cli "Quel temps fait-il aujourd\'hui ?"')
        print('Exemple avec MCP: python -m app.cli "Quel temps fait-il ?" --use-mcp')
        sys.exit(1)

    question = sys.argv[1]
    user_id = "1"
    use_mcp = False

    # Parse optional arguments
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--user-id" and i + 1 < len(sys.argv):
            user_id = sys.argv[i + 1]
        elif sys.argv[i] == "--use-mcp":
            use_mcp = True

    print(f"Question: {question}")
    print(f"User ID: {user_id}")
    print(f"MCP activé: {use_mcp}")
    print("-" * 60)

    try:
        response = ask_weather(question, user_id=user_id, use_mcp=use_mcp)
        print(f"\n📍 Localisation: {response.location or 'Non spécifiée'}")
        print(f"\n💬 Réponse:\n{response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
