# Guide de Configuration MCP (Model Context Protocol)

Ce guide explique comment configurer et utiliser les serveurs MCP avec le projet LangChain Starter.

## Qu'est-ce que MCP ?

Le Model Context Protocol (MCP) est un protocole ouvert développé par Anthropic qui permet aux LLMs de se connecter facilement à des sources de données externes et des outils. Il offre une interface standardisée pour :

- Accéder à des systèmes de fichiers
- Interroger des bases de données
- Interagir avec des APIs (GitHub, Google Drive, etc.)
- Rechercher sur le web
- Et bien plus encore...

## Installation

### 1. Installer Node.js

La plupart des serveurs MCP officiels nécessitent Node.js et `npx`.

```bash
# Vérifier si Node.js est installé
node --version
npm --version

# Si non installé, télécharger depuis https://nodejs.org/
```

### 2. Installer les dépendances Python

Les dépendances MCP sont déjà incluses dans `pyproject.toml` :

```bash
pip install -e .
```

## Configuration des Serveurs MCP

### Option 1 : Fichier de configuration JSON (Recommandé)

Créer un fichier `mcp_servers.json` à la racine du projet :

```bash
cp mcp_servers.example.json mcp_servers.json
```

Éditer `mcp_servers.json` pour activer les serveurs souhaités :

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "description": "Accès au système de fichiers"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      },
      "description": "Intégration GitHub"
    }
  }
}
```

### Option 2 : Configuration dans le code

Éditer `src/app/mcp/config.py` pour configurer les serveurs directement :

```python
def get_default_mcp_servers():
    servers = {}

    # Activer le serveur filesystem
    servers["filesystem"] = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    )

    return servers
```

## Serveurs MCP Populaires

### 1. Filesystem Server

Permet d'accéder au système de fichiers local.

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/chemin/vers/dossier"]
  }
}
```

**Outils fournis :**
- `read_file` : Lire un fichier
- `write_file` : Écrire dans un fichier
- `list_directory` : Lister les fichiers
- `create_directory` : Créer un dossier
- etc.

### 2. GitHub Server

Intégration avec GitHub (repositories, issues, PRs).

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_TOKEN": "ghp_votre_token"
    }
  }
}
```

**Variables d'environnement nécessaires :**
- `GITHUB_TOKEN` : Token d'accès GitHub (https://github.com/settings/tokens)

**Outils fournis :**
- `create_issue` : Créer une issue
- `create_pull_request` : Créer une PR
- `search_repositories` : Rechercher des repos
- etc.

### 3. Brave Search Server

Recherche web via l'API Brave.

```json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_API_KEY": "votre_cle_api"
    }
  }
}
```

**Variables d'environnement nécessaires :**
- `BRAVE_API_KEY` : Clé API Brave (https://brave.com/search/api/)

### 4. PostgreSQL Server

Intégration avec PostgreSQL.

```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": {
      "DATABASE_URL": "postgresql://user:password@localhost:5432/dbname"
    }
  }
}
```

### 5. SQLite Server

Intégration avec SQLite.

```json
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "/chemin/vers/database.db"]
  }
}
```

## Variables d'Environnement

Ajouter les clés API nécessaires dans votre fichier `.env` :

```env
# MCP Servers
GITHUB_TOKEN=ghp_votre_token_github
BRAVE_API_KEY=votre_cle_brave
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Utilisation

### CLI avec MCP

```bash
# Utiliser l'agent avec les outils MCP
python -m app.cli "Quel temps fait-il ?" --use-mcp

# Exemple avec GitHub
python -m app.cli "Liste les issues du repo anthropics/anthropic-sdk-python" --use-mcp
```

### API avec MCP

```bash
curl -X POST "http://localhost:8000/weather" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quel temps fait-il ?",
    "user_id": "1",
    "use_mcp": true
  }'
```

### Dans le code

```python
from app.agents.weather_agent import ask_weather

# Avec MCP activé
response = ask_weather(
    "Quelle est la météo ?",
    user_id="1",
    use_mcp=True  # Active les outils MCP
)

print(response.text)
```

## Créer un Agent Personnalisé avec MCP

```python
from app.mcp import get_mcp_tools
from app.llm.models import get_default_model
from langgraph.prebuilt import create_agent

# Récupérer tous les outils MCP
mcp_tools = get_mcp_tools()

# Créer un agent avec ces outils
agent = create_agent(
    model=get_default_model(),
    tools=mcp_tools,
    system_prompt="Tu es un assistant qui peut accéder à des fichiers et GitHub."
)

# Utiliser l'agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Liste les fichiers dans /tmp"}]
})
```

## Dépannage

### Erreur : "npx: command not found"

Installer Node.js : https://nodejs.org/

### Erreur : "Server connection failed"

1. Vérifier que les variables d'environnement sont correctement configurées
2. Tester manuellement le serveur :
   ```bash
   npx -y @modelcontextprotocol/server-github
   ```
3. Vérifier les logs d'erreur

### Aucun outil MCP chargé

1. Vérifier que `mcp_servers.json` existe et est valide
2. Vérifier que les serveurs sont correctement configurés
3. Activer le mode debug pour voir les erreurs

## Ressources

- Documentation officielle MCP : https://modelcontextprotocol.io/
- Serveurs MCP officiels : https://github.com/modelcontextprotocol/servers
- Documentation LangChain MCP : https://docs.langchain.com/mcp
- Liste des serveurs communautaires : https://github.com/topics/mcp-server

## Développer votre Propre Serveur MCP

Vous pouvez créer vos propres serveurs MCP pour exposer vos APIs internes :

```python
# Exemple simple avec le SDK Python MCP
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("mon-serveur")

@app.tool()
def ma_fonction_custom(param: str) -> str:
    """Description de ma fonction."""
    return f"Résultat pour {param}"

if __name__ == "__main__":
    stdio_server(app)
```

Voir la documentation officielle pour plus de détails.
