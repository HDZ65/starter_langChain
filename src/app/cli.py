"""Interface CLI pour l'agent météo."""

import sys

from app.agents.weather_agent import ask_weather


def main() -> None:
    """Point d'entrée principal de la CLI."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli \"Votre question\" [--user-id USER_ID]")
        print('Exemple: python -m app.cli "Quel temps fait-il aujourd\'hui ?"')
        sys.exit(1)

    question = sys.argv[1]
    user_id = "1"

    # Parse optional --user-id argument
    if len(sys.argv) >= 4 and sys.argv[2] == "--user-id":
        user_id = sys.argv[3]

    print(f"Question: {question}")
    print(f"User ID: {user_id}")
    print("-" * 60)

    try:
        response = ask_weather(question, user_id=user_id)
        print(f"\n📍 Localisation: {response.location or 'Non spécifiée'}")
        print(f"\n💬 Réponse:\n{response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
