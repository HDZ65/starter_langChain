# LangChain Starter v1

Projet starter moderne utilisant **LangChain v1** avec un exemple d'agent météo.

## 🚀 Fonctionnalités

- ✅ **LangChain v1** avec les nouvelles APIs (`init_chat_model`, `create_agent`, `@tool`)
- ✅ **LangGraph** : Workflows personnalisés avec StateGraph (simple agent, research, supervisor)
- ✅ **Agent météo** d'exemple avec outils et mémoire
- ✅ **Support MCP (Model Context Protocol)** : Intégration avec des serveurs MCP pour étendre les capacités de l'agent
- ✅ **Structure modulaire** : config, models, prompts, tools, agents, memory, mcp, graphs
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
│  │  ├─ weather_agent.py   # Agent météo avec create_agent
│  │  ├─ weather_graph.py   # Agent météo avec StateGraph
│  │  └─ mcp_agent.py       # Agent MCP générique
│  ├─ graphs/
│  │  ├─ base.py            # États de base (AgentState, ResearchState, etc.)
│  │  ├─ simple_agent.py    # Graph simple avec agent et outils
│  │  ├─ research_agent.py  # Workflow de recherche multi-étapes
│  │  └─ supervisor.py      # Pattern superviseur multi-agents
│  ├─ memory/
│  │  └─ base_memory.py     # Checkpointer (MemorySaver)
│  ├─ mcp/
│  │  ├─ __init__.py        # Client MCP
│  │  └─ config.py          # Configuration serveurs MCP
│  ├─ cli.py                # Interface CLI agent météo
│  ├─ mcp_cli.py            # Interface CLI agent MCP
│  ├─ graph_cli.py          # Interface CLI graphes LangGraph
│  └─ api/
│     └─ server.py          # API FastAPI
├─ tests/
│  └─ test_weather_agent.py # Tests
├─ .env.example
├─ mcp_servers.example.json # Configuration serveurs MCP
├─ MCP_SETUP.md             # Guide de configuration MCP
├─ LANGGRAPH_GUIDE.md       # Guide complet LangGraph
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

# Avec les outils MCP activés
python -m app.cli "Quel temps fait-il ?" --use-mcp
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
# Requête simple
curl -X POST "http://localhost:8000/weather" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quel temps fait-il ?", "user_id": "1"}'

# Requête avec MCP activé
curl -X POST "http://localhost:8000/weather" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quel temps fait-il ?", "user_id": "1", "use_mcp": true}'
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

## 🔌 Model Context Protocol (MCP)

Ce projet supporte le **Model Context Protocol (MCP)** développé par Anthropic, qui permet d'étendre les capacités de l'agent avec des outils externes.

### Configuration rapide

1. **Copier le fichier de configuration exemple :**
   ```bash
   cp mcp_servers.example.json mcp_servers.json
   ```

2. **Éditer `mcp_servers.json`** pour activer les serveurs souhaités (filesystem, GitHub, Brave Search, etc.)

3. **Ajouter les clés API dans `.env` :**
   ```env
   GITHUB_TOKEN=ghp_your_token
   BRAVE_API_KEY=your_key
   ```

4. **Utiliser avec MCP :**
   ```bash
   python -m app.cli "Ta question" --use-mcp
   ```

### Serveurs MCP populaires

- **Filesystem** : Accéder aux fichiers locaux
- **GitHub** : Gérer repos, issues, PRs
- **Brave Search** : Rechercher sur le web
- **PostgreSQL / SQLite** : Interroger des bases de données
- Et bien d'autres...

📖 **Guide complet** : Voir [MCP_SETUP.md](MCP_SETUP.md) pour la documentation détaillée.

## 🔀 LangGraph - Workflows Personnalisés

Ce projet utilise **LangGraph** pour créer des workflows et agents avec contrôle total du flux d'exécution.

### Graphes disponibles

#### 1. Simple Agent
Agent conversationnel basique avec cycle agent → tools → agent.

```bash
python -m app.graph_cli simple "Quel temps fait-il à Paris ?"
```

#### 2. Research Agent
Workflow de recherche multi-étapes : analyze → generate_queries → search → synthesize.

```bash
python -m app.graph_cli research "Quelle est l'histoire de Python ?"
```

#### 3. Supervisor Multi-Agents
Orchestration de 3 agents spécialisés (researcher, coder, writer) par un superviseur.

```bash
python -m app.graph_cli supervisor "Crée un tutoriel FastAPI complet"
```

### Utilisation dans le code

```python
# Simple agent
from app.graphs.simple_agent import run_simple_agent
from app.tools.weather import get_weather_for_location

response = run_simple_agent(
    "Quel temps fait-il ?",
    tools=[get_weather_for_location]
)

# Research workflow
from app.graphs.research_agent import run_research

result = run_research("Ma question de recherche")
print(result["answer"])

# Supervisor
from app.graphs.supervisor import run_supervisor

result = run_supervisor("Crée un exemple d'API")
print(result["final_result"])
```

### Créer votre propre graphe

```python
from langgraph.graph import StateGraph, END
from app.graphs.base import AgentState

workflow = StateGraph(AgentState)
workflow.add_node("my_node", my_node_function)
workflow.set_entry_point("my_node")
workflow.add_edge("my_node", END)

graph = workflow.compile()
result = graph.invoke({"messages": [...]})
```

📖 **Guide complet** : Voir [LANGGRAPH_GUIDE.md](LANGGRAPH_GUIDE.md) pour la documentation détaillée.

## 📚 Documentation

- [LangChain v1 Docs](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain OpenAI](https://python.langchain.com/docs/integrations/platforms/openai)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📝 License

MIT
