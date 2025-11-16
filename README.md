# LangChain Starter v1

Projet starter moderne utilisant **LangChain v1** avec un exemple d'agent météo.

## 🚀 Fonctionnalités

- ✅ **LangChain v1** avec les nouvelles APIs (`init_chat_model`, `create_agent`, `@tool`)
- ✅ **Agent météo** d'exemple avec outils et mémoire
- ✅ **Structure modulaire** : config, models, prompts, tools, agents, memory
- ✅ **Interfaces multiples** : CLI et API HTTP (FastAPI)
- ✅ **Gestion de la mémoire** avec checkpointer LangGraph
- ✅ **Configuration** avec Pydantic Settings
- ✅ **Tests** avec pytest
- ✅ **Python 3.10+**

## 📁 Structure du projet

```
langchain-starter/
├─ src/app/
│  ├─ settings.py           # Configuration avec pydantic-settings
│  ├─ llm/
│  │  ├─ models.py          # Initialisation des modèles (init_chat_model)
│  │  └─ prompts.py         # Prompts système
│  ├─ tools/
│  │  └─ weather.py         # Outils météo avec @tool
│  ├─ agents/
│  │  └─ weather_agent.py   # Agent météo avec create_agent
│  ├─ memory/
│  │  └─ base_memory.py     # Checkpointer (MemorySaver)
│  ├─ cli.py                # Interface CLI
│  └─ api/
│     └─ server.py          # API FastAPI
├─ tests/
│  └─ test_weather_agent.py # Tests
├─ .env.example
├─ pyproject.toml
└─ README.md
```

## 🛠️ Installation

### 1. Cloner et installer les dépendances

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -e .

# Pour le développement
pip install -e ".[dev]"
```

### 2. Configuration

Copier `.env.example` vers `.env` et configurer vos clés API :

```bash
cp .env.example .env
```

Éditer `.env` :

```env
OPENAI_API_KEY=votre_clé_openai
MODEL_NAME=gpt-4o-mini
```

## 💻 Usage

### Interface CLI

```bash
# Question simple
python -m app.cli "Quel temps fait-il aujourd'hui ?"

# Avec un user_id spécifique
python -m app.cli "Météo du jour ?" --user-id demo
```

### API HTTP

Lancer le serveur FastAPI :

```bash
uvicorn app.api.server:app --reload
```

Ensuite, accéder à :
- API : http://localhost:8000
- Documentation interactive : http://localhost:8000/docs

Exemple de requête :

```bash
curl -X POST "http://localhost:8000/weather" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quel temps fait-il ?", "user_id": "1"}'
```

## 🧪 Tests

```bash
# Lancer les tests
pytest

# Avec coverage
pytest --cov=app tests/

# Tests verbeux
pytest -v
```

## 🏗️ Architecture

### Agent météo

L'agent météo utilise :
- **Modèle** : GPT-4o-mini (configurable)
- **Outils** :
  - `get_weather_for_location(city)` : Obtient la météo pour une ville
  - `get_user_location(runtime)` : Récupère la localisation de l'utilisateur
- **Mémoire** : MemorySaver pour conserver le contexte conversationnel
- **Contexte** : Dataclass `Context` avec `user_id`
- **Réponse structurée** : `WeatherResponse` avec `text` et `location`

### Nouvelles APIs LangChain v1

- `init_chat_model()` : Initialisation unifiée des modèles
- `create_agent()` : Création d'agents avec outils, prompts et mémoire
- `@tool` : Décorateur pour créer des outils
- `ToolRuntime[Context]` : Accès au contexte dans les outils
- `response_format` : Réponses structurées avec dataclasses

## 🔧 Développement

### Linting et formatage

```bash
# Ruff (linting + formatting)
ruff check .
ruff format .

# MyPy (type checking)
mypy src/
```

### Ajouter un nouvel agent

1. Créer les outils dans `src/app/tools/`
2. Définir le prompt dans `src/app/llm/prompts.py`
3. Créer l'agent dans `src/app/agents/`
4. Ajouter des tests dans `tests/`

## 📚 Documentation LangChain

- [LangChain v1 Docs](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain OpenAI](https://python.langchain.com/docs/integrations/platforms/openai)

## 📝 License

MIT
