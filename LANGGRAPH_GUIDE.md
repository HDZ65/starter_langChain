# Guide LangGraph - Workflows et Agents Personnalisés

Ce guide explique comment utiliser **LangGraph** pour créer des workflows et agents personnalisés dans le projet.

## 📚 Table des matières

1. [Introduction à LangGraph](#introduction)
2. [Concepts de base](#concepts-de-base)
3. [Graphes disponibles](#graphes-disponibles)
4. [Créer votre propre graphe](#créer-votre-graphe)
5. [Exemples d'utilisation](#exemples)
6. [Patterns avancés](#patterns-avancés)

## Introduction

**LangGraph** est une bibliothèque pour créer des applications LLM avec état sous forme de graphes. Contrairement à `create_agent()` qui abstrait la logique, LangGraph vous donne un contrôle total sur le flux d'exécution.

### Pourquoi LangGraph ?

- ✅ **Contrôle total** : Définir exactement le flux d'exécution
- ✅ **État partagé** : Gérer un état complexe entre les nodes
- ✅ **Conditionnels** : Brancher le flux selon des conditions
- ✅ **Cycles** : Créer des boucles (agent → tools → agent)
- ✅ **Multi-agents** : Orchestrer plusieurs agents spécialisés
- ✅ **Debuggable** : Visualiser et débugger facilement

## Concepts de base

### 1. État (State)

L'état est une classe TypedDict qui représente les données partagées entre les nodes.

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Liste de messages avec reducer
    user_id: str                              # Donnée personnalisée
    location: str | None                      # Donnée optionnelle
```

**Reducers** : `add_messages` est un reducer qui fusionne intelligemment les nouvelles valeurs avec les anciennes.

### 2. Nodes

Les nodes sont des fonctions qui prennent l'état et retournent une mise à jour partielle.

```python
def my_node(state: AgentState) -> dict:
    """Un node simple."""
    messages = state["messages"]
    # Traitement...
    return {"messages": [new_message]}  # Retourne seulement ce qui change
```

### 3. Edges

Les edges définissent le flux entre les nodes.

```python
workflow.add_edge("node_a", "node_b")  # Edge normal : A → B

# Edge conditionnel
workflow.add_conditional_edges(
    "node_a",
    router_function,  # Fonction qui retourne le nom du prochain node
    {
        "option_1": "node_b",
        "option_2": "node_c",
        "end": END
    }
)
```

### 4. Graphe complet

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Ajouter des nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# Définir le flow
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Compiler
graph = workflow.compile()

# Exécuter
result = graph.invoke({"messages": [...]})
```

## Graphes disponibles

Le projet fournit 4 types de graphes prêts à l'emploi :

### 1. Simple Agent (`simple_agent.py`)

Agent conversationnel basique avec outils.

**Architecture** :
```
START → agent → [should_continue]
                  ├─ tools → agent
                  └─ END
```

**Utilisation** :
```python
from app.graphs.simple_agent import build_simple_graph, run_simple_agent
from app.tools.weather import get_weather_for_location

# Avec build_simple_graph
graph = build_simple_graph(tools=[get_weather_for_location])
result = graph.invoke({"messages": [HumanMessage(content="Météo à Paris ?")]})

# Avec run_simple_agent (wrapper simplifié)
response = run_simple_agent(
    "Quel temps fait-il à Paris ?",
    tools=[get_weather_for_location],
    thread_id="my_session"
)
print(response)
```

**Caractéristiques** :
- Cycle agent → tools → agent
- Mémoire conversationnelle
- Support de n'importe quels outils

### 2. Research Agent (`research_agent.py`)

Workflow de recherche multi-étapes.

**Architecture** :
```
START → analyze → generate_queries → search → synthesize → END
```

**Utilisation** :
```python
from app.graphs.research_agent import run_research

result = run_research("Quelle est l'histoire de Python ?")

print(f"Requêtes : {result['queries']}")
print(f"Réponse : {result['answer']}")
```

**Caractéristiques** :
- Pipeline linéaire en 4 étapes
- Génération automatique de requêtes
- Synthèse finale des résultats
- État complexe avec métadonnées

### 3. Supervisor Graph (`supervisor.py`)

Multi-agents avec orchestration par superviseur.

**Architecture** :
```
                  ┌→ researcher →┐
START → supervisor ┼→ coder →    ├→ supervisor → ...
                  └→ writer →   ┘
```

**Utilisation** :
```python
from app.graphs.supervisor import run_supervisor

result = run_supervisor("Crée un tutoriel FastAPI complet")

print(f"Agents utilisés : {result['agents_used']}")
print(f"Résultat : {result['final_result']}")
print(f"Détails : {result['all_results']}")
```

**Caractéristiques** :
- 3 agents spécialisés (researcher, coder, writer)
- Superviseur intelligent qui délègue
- Routing dynamique avec structured output
- Accumulation des résultats de chaque agent

### 4. Weather Graph (`weather_graph.py`)

Agent météo avec StateGraph personnalisé.

**Architecture** :
```
START → agent → extract_location → [should_continue]
                                     ├─ tools → agent
                                     └─ END
```

**Utilisation** :
```python
from app.agents.weather_graph import ask_weather_graph

response = ask_weather_graph(
    "Quel temps fait-il ?",
    user_id="123",
    use_mcp=True
)

print(f"Réponse : {response.text}")
print(f"Localisation : {response.location}")
print(f"Étapes : {response.steps}")
```

## Créer votre propre graphe

### Exemple complet : Agent de traduction

```python
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.llm.models import get_default_model
from app.memory.base_memory import get_default_checkpointer

# 1. Définir l'état
class TranslationState(TypedDict):
    messages: Annotated[list, add_messages]
    source_lang: str
    target_lang: str
    original_text: str
    translated_text: str

# 2. Créer les nodes
def detect_language(state: TranslationState) -> dict:
    """Détecte la langue source."""
    model = get_default_model()
    text = state["original_text"]

    response = model.invoke([
        HumanMessage(content=f"Détecte la langue de ce texte (fr/en/es/de) : {text}")
    ])

    return {"source_lang": response.content.strip().lower()}

def translate(state: TranslationState) -> dict:
    """Traduit le texte."""
    model = get_default_model()

    prompt = f"""Traduis ce texte de {state['source_lang']} vers {state['target_lang']} :
{state['original_text']}

Fournis uniquement la traduction, sans explication."""

    response = model.invoke([HumanMessage(content=prompt)])

    return {
        "translated_text": response.content,
        "messages": [response]
    }

def quality_check(state: TranslationState) -> dict:
    """Vérifie la qualité de la traduction."""
    model = get_default_model()

    prompt = f"""Évalue cette traduction de {state['source_lang']} vers {state['target_lang']} :

Original : {state['original_text']}
Traduction : {state['translated_text']}

Est-elle correcte ? Réponds par OUI ou NON."""

    response = model.invoke([HumanMessage(content=prompt)])
    quality = response.content.strip().upper()

    return {"messages": [SystemMessage(content=f"Qualité : {quality}")]}

# 3. Fonction de routing
def should_retry(state: TranslationState) -> Literal["translate", "end"]:
    """Décide si on doit retraduire."""
    last_msg = state["messages"][-1]
    if "NON" in last_msg.content:
        return "translate"
    return "end"

# 4. Construire le graphe
def build_translation_graph() -> StateGraph:
    workflow = StateGraph(TranslationState)

    # Ajouter les nodes
    workflow.add_node("detect", detect_language)
    workflow.add_node("translate", translate)
    workflow.add_node("check", quality_check)

    # Définir le flow
    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "translate")
    workflow.add_edge("translate", "check")
    workflow.add_conditional_edges(
        "check",
        should_retry,
        {
            "translate": "translate",  # Retry
            "end": END
        }
    )

    # Compiler avec mémoire
    checkpointer = get_default_checkpointer()
    return workflow.compile(checkpointer=checkpointer)

# 5. Utiliser le graphe
def translate_text(text: str, target_lang: str = "fr") -> str:
    graph = build_translation_graph()

    result = graph.invoke({
        "messages": [],
        "source_lang": "",
        "target_lang": target_lang,
        "original_text": text,
        "translated_text": ""
    })

    return result["translated_text"]
```

## Exemples d'utilisation

### CLI des graphes

```bash
# Agent simple
python -m app.graph_cli simple "Quel temps fait-il à Paris ?"

# Recherche
python -m app.graph_cli research "Quelle est l'histoire de Python ?"

# Superviseur multi-agents
python -m app.graph_cli supervisor "Crée un tutoriel sur FastAPI"
```

### Dans le code

```python
# Simple agent
from app.graphs.simple_agent import build_simple_graph
from app.tools.weather import get_weather_for_location

graph = build_simple_graph(tools=[get_weather_for_location])
result = graph.invoke({"messages": [...]})

# Research
from app.graphs.research_agent import run_research

result = run_research("Ma question de recherche")

# Supervisor
from app.graphs.supervisor import run_supervisor

result = run_supervisor("Ma tâche complexe")
```

## Patterns avancés

### 1. Human-in-the-loop

Demander validation humaine avant de continuer.

```python
def human_approval(state: MyState) -> Literal["continue", "revise"]:
    """Demande l'approbation humaine."""
    draft = state["draft"]
    print(f"Draft : {draft}")
    approval = input("Approuver ? (y/n) : ")
    return "continue" if approval.lower() == "y" else "revise"

workflow.add_conditional_edges("generate_draft", human_approval)
```

### 2. Parallel execution

Exécuter plusieurs nodes en parallèle.

```python
from langgraph.graph import StateGraph

# Les nodes peuvent s'exécuter en parallèle si indépendants
workflow.add_node("search_web", search_web_node)
workflow.add_node("search_db", search_db_node)

# Démarrer les deux en parallèle depuis le même point
workflow.add_edge("start", "search_web")
workflow.add_edge("start", "search_db")

# Rejoindre après
workflow.add_edge("search_web", "synthesize")
workflow.add_edge("search_db", "synthesize")
```

### 3. Sous-graphes

Imbriquer des graphes dans d'autres graphes.

```python
def subgraph_node(state: ParentState) -> dict:
    """Node qui exécute un sous-graphe."""
    subgraph = build_research_graph()

    result = subgraph.invoke({
        "messages": state["messages"],
        # ... other subgraph state
    })

    return {"messages": result["messages"]}

workflow.add_node("research_phase", subgraph_node)
```

### 4. Retry avec backoff

Réessayer avec délai croissant.

```python
import time

class RetryState(TypedDict):
    messages: Annotated[list, add_messages]
    retry_count: int
    max_retries: int

def api_call_node(state: RetryState) -> dict:
    """Appel API avec retry."""
    try:
        # Tentative d'appel API
        result = call_external_api()
        return {"messages": [result], "retry_count": 0}
    except Exception as e:
        retry_count = state.get("retry_count", 0) + 1
        if retry_count < state.get("max_retries", 3):
            time.sleep(2 ** retry_count)  # Exponential backoff
            return {"retry_count": retry_count}
        raise

def should_retry(state: RetryState) -> Literal["retry", "end"]:
    if state.get("retry_count", 0) > 0:
        return "retry"
    return "end"
```

## Visualisation

LangGraph peut générer des visualisations de vos graphes :

```python
from langgraph.graph import StateGraph

graph = build_my_graph()

# Générer un diagramme Mermaid
print(graph.get_graph().draw_mermaid())

# Ou PNG (nécessite pygraphviz)
graph.get_graph().draw_png("my_graph.png")
```

## Debugging

### Afficher l'état à chaque étape

```python
graph = build_my_graph()

for step in graph.stream(initial_state):
    print(f"Step: {step}")
```

### Checkpoints intermédiaires

```python
# Avec checkpointer, vous pouvez récupérer l'historique
config = {"configurable": {"thread_id": "123"}}

result = graph.invoke(initial_state, config=config)

# Récupérer l'historique
for state in graph.get_state_history(config):
    print(state)
```

## Ressources

- **Documentation LangGraph** : https://langchain-ai.github.io/langgraph/
- **Exemples LangGraph** : https://github.com/langchain-ai/langgraph/tree/main/examples
- **Tutoriels** : https://langchain-ai.github.io/langgraph/tutorials/

## Prochaines étapes

1. Explorez les graphes fournis dans `src/app/graphs/`
2. Testez-les avec la CLI : `python -m app.graph_cli`
3. Créez votre propre graphe personnalisé
4. Combinez avec MCP pour des capacités étendues
5. Visualisez vos graphes pour mieux comprendre le flux

Bon développement avec LangGraph ! 🎯
