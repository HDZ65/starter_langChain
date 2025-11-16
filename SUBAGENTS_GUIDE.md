# Guide des Subagents - Délégation et Context Quarantine

Ce guide explique comment utiliser le **système de subagents** pour déléguer du travail et garder le contexte principal propre.

## 📚 Table des matières

1. [Pourquoi les subagents ?](#pourquoi-les-subagents)
2. [Architecture du système](#architecture)
3. [Subagents disponibles](#subagents-disponibles)
4. [Utilisation](#utilisation)
5. [Créer vos propres subagents](#créer-vos-subagents)
6. [Bonnes pratiques](#bonnes-pratiques)
7. [Patterns avancés](#patterns-avancés)

## Pourquoi les subagents ?

### Le problème : Context Bloat (Surcharge du contexte)

Quand un agent utilise des outils avec des sorties volumineuses (recherche web, lecture de fichiers, requêtes DB), le contexte se remplit rapidement avec des résultats intermédiaires, laissant moins d'espace pour le raisonnement principal.

**Exemple sans subagents :**
```
Agent principal → outil recherche 1 (500 tokens)
                → outil recherche 2 (600 tokens)
                → outil recherche 3 (550 tokens)
                → outil recherche 4 (480 tokens)
                → synthèse (100 tokens)

Contexte total: 2230 tokens (dont 2130 de résultats bruts)
```

**Avec subagents :**
```
Agent principal → délègue au subagent "research-specialist"
                  ├─ Subagent fait 4 recherches
                  └─ Retourne synthèse concise (150 tokens)

Contexte principal: 150 tokens seulement
```

### La solution : Context Quarantine

Les subagents **isolent** le travail détaillé. L'agent principal reçoit uniquement le résultat final concis, pas les dizaines d'appels d'outils intermédiaires.

### Quand utiliser les subagents ?

✅ **OUI** :
- Tâches multi-étapes qui encombreraient le contexte
- Domaines spécialisés nécessitant des instructions spécifiques
- Tâches nécessitant différentes capacités de modèle
- Garder l'agent principal concentré sur la coordination

❌ **NON** :
- Tâches simples, en une étape
- Quand vous devez maintenir le contexte intermédiaire
- Quand l'overhead dépasse les bénéfices

## Architecture

### Vue d'ensemble

```
┌──────────────────────────────────────────────┐
│         Agent Coordinateur                    │
│  - Analyse la tâche                           │
│  - Décide de déléguer ou traiter             │
│  - Synthétise les résultats                  │
└────────────┬─────────────────────────────────┘
             │
    ┌────────┴────────┐
    │   Délégation    │
    └────────┬────────┘
             │
    ┌────────▼───────────────────────────────┐
    │                                        │
    ▼                                        ▼
┌─────────────────┐              ┌─────────────────┐
│ Research        │              │ Code Expert     │
│ Specialist      │              │                 │
│ - Web search    │              │ - Code analysis │
│ - Synthesis     │              │ - Optimization  │
└─────────────────┘              └─────────────────┘
    │                                        │
    └──────────┬───────────────────────────┘
               │
               ▼
    Résultat concis (< 500 mots)
               │
               ▼
         Agent Coordinateur
```

### Components

1. **SubAgent** : Définition d'un agent spécialisé
2. **Registry** : Registre des subagents disponibles
3. **Coordinator** : Agent qui délègue intelligemment
4. **Specialized Agents** : Subagents prédéfinis

## Subagents disponibles

Le projet fournit 5 subagents prédéfinis :

### 1. Research Specialist

**Nom** : `research-specialist`

**Description** : Recherche approfondie multi-sources avec synthèse structurée.

**Quand l'utiliser** :
- Questions de recherche complexes
- Besoin de synthétiser plusieurs sources
- Analyse approfondie d'un sujet

**Format de sortie** :
- Résumé (2-3 paragraphes)
- Points clés (3-5 bullets)
- Sources

**Exemple** :
```python
from app.subagents.coordinator import delegate_task

result = delegate_task("Recherche sur l'IA quantique et ses applications")
# Le coordinateur délègue automatiquement à research-specialist
```

### 2. Code Expert

**Nom** : `code-expert`

**Description** : Expert Python pour résolution de problèmes, optimisation, debugging.

**Quand l'utiliser** :
- Problèmes de code complexes
- Optimisation de performance
- Debugging
- Refactoring

**Format de sortie** :
- Code solution (commenté)
- Explication concise
- Considérations

**Exemple** :
```python
result = delegate_task(
    "Crée une fonction Python qui trouve le plus court chemin dans un graphe"
)
```

### 3. Data Analyst

**Nom** : `data-analyst`

**Description** : Analyse de données avec extraction d'insights.

**Quand l'utiliser** :
- Analyse de données
- Identification de patterns
- Recommandations basées sur données

**Format de sortie** :
- Insights clés (3-5 bullets)
- Score de confiance
- Recommandations

**Exemple** :
```python
result = delegate_task("Analyse les tendances du marché tech en 2025")
```

### 4. Professional Writer

**Nom** : `professional-writer`

**Description** : Rédaction professionnelle et structurée.

**Quand l'utiliser** :
- Création de documentation
- Rédaction de rapports
- Communications professionnelles
- Transformation de contenu technique en langage clair

**Format de sortie** :
- Contenu structuré
- Langage professionnel
- Longueur adaptée

**Exemple** :
```python
result = delegate_task("Rédige un email professionnel pour présenter notre nouveau produit")
```

### 5. Quick Helper

**Nom** : `quick-helper`

**Description** : Assistant polyvalent pour tâches rapides.

**Quand l'utiliser** :
- Questions factuelles
- Calculs simples
- Tâches directes sans analyse approfondie

**Exemple** :
```python
result = delegate_task("Quelle est la capitale de la France ?")
```

## Utilisation

### CLI Simple

```bash
# Le coordinateur choisit automatiquement le meilleur subagent
python -m app.subagent_cli "Recherche sur les tendances IA 2025"

python -m app.subagent_cli "Crée une fonction de tri optimisée"

python -m app.subagent_cli "Analyse les données de ventes Q4"
```

### Dans le code

#### Délégation automatique

```python
from app.subagents.coordinator import delegate_task

# Le coordinateur analyse et choisit le subagent approprié
result = delegate_task("Recherche approfondie sur le machine learning quantique")

print(result)
```

#### Délégation manuelle à un subagent spécifique

```python
from app.subagents.coordinator import execute_subagent
from app.subagents.specialized import research_subagent

# Exécuter directement un subagent spécifique
result = execute_subagent(
    subagent=research_subagent,
    task="Analyse les avancées en IA quantique",
    user_id="my_session"
)

print(result.to_string())
```

#### Avec subagents personnalisés

```python
from app.subagents.base import SubAgent
from app.subagents.coordinator import delegate_task
from app.subagents.registry import register_subagent, clear_registry

# Créer un subagent personnalisé
custom_subagent = SubAgent(
    name="legal-expert",
    description="Expert juridique pour analyse de contrats",
    system_prompt="""Tu es un expert juridique.
    Analyse les contrats et identifie les points clés et risques.
    Sois concis et précis.""",
    tools=None
)

# Enregistrer
clear_registry()
register_subagent(custom_subagent)

# Utiliser
result = delegate_task("Analyse ce contrat de vente...")
```

## Créer vos propres subagents

### Structure de base

```python
from langchain_core.tools import tool
from app.subagents.base import SubAgent

# 1. Définir les outils (optionnel)
@tool
def my_custom_tool(param: str) -> str:
    """Description de l'outil."""
    return f"Résultat pour {param}"

# 2. Créer le subagent
my_subagent = SubAgent(
    name="my-specialist",
    description="Description concise de ce que fait ce subagent",
    system_prompt="""Instructions détaillées pour le subagent.

    Format de sortie :
    - Point 1
    - Point 2

    IMPORTANT : Garde la réponse concise (< 500 mots).""",
    tools=[my_custom_tool],  # Optionnel
    model_name="gpt-4o",     # Optionnel, surcharge le modèle par défaut
    max_iterations=15,        # Optionnel
)

# 3. Enregistrer
from app.subagents.registry import register_subagent

register_subagent(my_subagent)

# 4. Utiliser
from app.subagents.coordinator import delegate_task

result = delegate_task("Ma tâche spécialisée")
```

### Exemple complet : Subagent de traduction

```python
from langchain_core.tools import tool
from app.subagents.base import SubAgent
from app.subagents.registry import register_subagent

@tool
def detect_language(text: str) -> str:
    """Détecte la langue d'un texte."""
    # Implémentation réelle ici
    return "fr"

@tool
def translate_text(text: str, target_lang: str) -> str:
    """Traduit le texte vers la langue cible."""
    # Implémentation réelle ici
    return f"Texte traduit en {target_lang}"

translation_subagent = SubAgent(
    name="translator",
    description="Traduit des textes entre différentes langues avec haute qualité. Détecte automatiquement la langue source.",
    system_prompt="""Tu es un traducteur expert multilingue.

    Processus :
    1. Détecte la langue source avec detect_language
    2. Traduis avec translate_text
    3. Vérifie la qualité de la traduction

    Format de sortie :
    - Langue source → langue cible
    - Traduction
    - Notes (si nécessaire)

    Sois précis et garde le ton original.""",
    tools=[detect_language, translate_text],
    max_iterations=5,
)

register_subagent(translation_subagent)

# Utilisation
from app.subagents.coordinator import delegate_task

result = delegate_task("Traduis 'Hello world' en français")
```

## Bonnes pratiques

### 1. Descriptions claires et spécifiques

✅ **BON** :
```python
description="Analyse des données financières avec extraction d'insights actionnables et scores de confiance. Pour analyses de marché et recommandations d'investissement."
```

❌ **MAUVAIS** :
```python
description="Fait des trucs avec les finances"
```

### 2. System prompts détaillés

Incluez :
- **Rôle** : Qui est le subagent
- **Processus** : Comment doit-il procéder
- **Format de sortie** : Structure attendue
- **Contraintes** : Longueur max, ton, etc.

```python
system_prompt="""Tu es un expert en sécurité informatique.

Rôle :
- Analyser les vulnérabilités de code
- Identifier les failles de sécurité
- Proposer des corrections

Processus :
1. Scanner le code pour patterns dangereux
2. Identifier les CVEs connues
3. Évaluer la criticité (1-10)
4. Proposer des fixes

Format de sortie :
- Vulnérabilités trouvées (liste)
- Criticité globale
- Recommandations prioritaires

IMPORTANT : Limite à 400 mots. Priorise les problèmes critiques."""
```

### 3. Outils minimalistes

Ne donnez que les outils nécessaires :

✅ **BON** :
```python
email_subagent = SubAgent(
    name="email-sender",
    tools=[send_email, validate_email],  # Focused
)
```

❌ **MAUVAIS** :
```python
email_subagent = SubAgent(
    name="email-sender",
    tools=[send_email, web_search, db_query, file_read],  # Too many
)
```

### 4. Retours concis

Instruisez explicitement à retourner des résumés :

```python
system_prompt="""...

Format de sortie :
- Résumé exécutif (100 mots max)
- 3-5 points clés
- Recommandation finale

NE PAS INCLURE :
- Données brutes
- Calculs intermédiaires
- Résultats complets des outils

Objectif : Contexte propre pour l'agent principal."""
```

### 5. Choisir le bon modèle

```python
subagents = [
    SubAgent(
        name="contract-reviewer",
        description="Revue de contrats légaux",
        system_prompt="...",
        model_name="claude-sonnet-4-5-20250929",  # Grand contexte
    ),
    SubAgent(
        name="quick-calculator",
        description="Calculs mathématiques rapides",
        system_prompt="...",
        model_name="gpt-4o-mini",  # Plus rapide et économique
    ),
]
```

## Patterns avancés

### 1. Chaîne de subagents

```python
from app.subagents.coordinator import execute_subagent
from app.subagents.specialized import (
    data_analyst_subagent,
    research_subagent,
    writer_subagent
)

# Étape 1 : Recherche
research_result = execute_subagent(
    research_subagent,
    "Recherche sur les tendances IA 2025"
)

# Étape 2 : Analyse
analysis_result = execute_subagent(
    data_analyst_subagent,
    f"Analyse ces données : {research_result.result}"
)

# Étape 3 : Rédaction
final_result = execute_subagent(
    writer_subagent,
    f"Rédige un rapport basé sur : {analysis_result.result}"
)

print(final_result.to_string())
```

### 2. Subagent avec validation

```python
from app.subagents.base import SubAgent

validation_subagent = SubAgent(
    name="validator",
    description="Valide et vérifie les résultats d'autres subagents",
    system_prompt="""Tu es un validateur expert.

    Ton rôle :
    1. Vérifier la cohérence des informations
    2. Identifier les erreurs ou incohérences
    3. Donner un score de confiance (0-100)

    Format :
    - Validation: OK/KO
    - Score de confiance: X/100
    - Problèmes identifiés (si applicable)
    - Recommandations""",
)

# Utilisation
result = execute_subagent(research_subagent, "Recherche...")
validation = execute_subagent(
    validation_subagent,
    f"Valide ce résultat : {result.result}"
)
```

### 3. Subagent avec retry logic

```python
from app.subagents.base import SubAgent, SubAgentResult

def execute_with_retry(subagent: SubAgent, task: str, max_retries: int = 3) -> SubAgentResult:
    """Exécute un subagent avec retry en cas d'échec."""
    for attempt in range(max_retries):
        result = execute_subagent(subagent, task)

        if result.success:
            return result

        print(f"Tentative {attempt + 1} échouée: {result.error}")

    return result  # Retourne le dernier résultat même si échec

# Utilisation
result = execute_with_retry(code_expert_subagent, "Crée un algo complexe")
```

### 4. Agrégation de résultats

```python
from app.subagents.specialized import get_default_subagents
from app.subagents.coordinator import execute_subagent

def get_multiple_perspectives(question: str) -> dict[str, str]:
    """Obtient des perspectives de plusieurs subagents."""
    perspectives = {}

    # Demander à plusieurs subagents
    for subagent in get_default_subagents()[:3]:  # 3 premiers
        result = execute_subagent(subagent, question)
        if result.success:
            perspectives[subagent.name] = result.result

    return perspectives

# Utilisation
perspectives = get_multiple_perspectives("Quelle est la meilleure approche pour l'IA ?")
for agent, response in perspectives.items():
    print(f"\n{agent}:")
    print(response[:200] + "...")
```

## Troubleshooting

### Subagent non appelé

**Problème** : Le coordinateur traite lui-même au lieu de déléguer.

**Solutions** :
1. Rendre la description plus spécifique
2. Vérifier que le subagent est bien enregistré
3. S'assurer que la tâche correspond au domaine du subagent

### Contexte toujours surchargé

**Problème** : Les résultats sont trop verbeux.

**Solutions** :
1. Renforcer les instructions de concision dans le system_prompt
2. Ajouter une limite de mots explicite
3. Demander un format structuré (bullets, tableaux)

### Mauvais subagent sélectionné

**Problème** : Le coordinateur choisit le mauvais subagent.

**Solutions** :
1. Différencier clairement les descriptions
2. Ajouter des exemples d'usage dans la description
3. Créer des subagents plus spécialisés

## Ressources

- **Code source** : `src/app/subagents/`
- **Exemples** : `src/app/subagents/specialized.py`
- **Tests** : `tests/test_subagents.py`
- **Documentation LangGraph** : https://langchain-ai.github.io/langgraph/

## Prochaines étapes

1. Testez la CLI : `python -m app.subagent_cli "Votre tâche"`
2. Créez votre premier subagent personnalisé
3. Expérimentez avec différents patterns de délégation
4. Mesurez la réduction du contexte avant/après

Bon développement avec les subagents ! 🚀
