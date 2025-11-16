"""Subagents spécialisés pré-définis."""

from langchain_core.tools import tool

from app.subagents.base import SubAgent

# === RESEARCH SUBAGENT ===

RESEARCH_PROMPT = """Tu es un chercheur expert spécialisé dans la recherche approfondie.

Ton rôle :
1. Décomposer la question de recherche en sous-questions clés
2. Utiliser les outils de recherche disponibles pour collecter des informations
3. Synthétiser les résultats de manière concise et structurée

Format de sortie OBLIGATOIRE :
- Résumé (2-3 paragraphes maximum)
- Points clés (3-5 bullet points)
- Sources (si disponibles)

IMPORTANT : Garde ta réponse sous 500 mots pour maintenir un contexte propre.
Ne retourne PAS les résultats bruts des recherches."""


@tool
def simulate_web_search(query: str) -> str:
    """Simule une recherche web (à remplacer par une vraie API)."""
    return f"Résultats simulés pour: {query}\n- Information 1\n- Information 2\n- Information 3"


research_subagent = SubAgent(
    name="research-specialist",
    description="Conduit des recherches approfondies sur des sujets spécifiques. Utilise plusieurs recherches et synthétise les résultats. Idéal pour questions complexes nécessitant analyse multi-sources.",
    system_prompt=RESEARCH_PROMPT,
    tools=[simulate_web_search],
    max_iterations=15,
    return_format="structured_summary",
)


# === CODE EXPERT SUBAGENT ===

CODE_EXPERT_PROMPT = """Tu es un expert en programmation Python.

Ton rôle :
1. Analyser les problèmes de code
2. Proposer des solutions optimisées et testées
3. Fournir des explications claires

Format de sortie :
- Code solution (bien commenté)
- Explication concise (3-4 lignes)
- Considérations importantes

IMPORTANT : Limite ta réponse à l'essentiel. Pas de verbosité excessive."""


@tool
def analyze_code(code: str) -> str:
    """Analyse du code (placeholder)."""
    return f"Analyse: Le code contient {len(code.split())} mots"


code_expert_subagent = SubAgent(
    name="code-expert",
    description="Expert en programmation Python. Résout des problèmes de code, optimise, debug et explique. Utilise pour tâches de développement complexes.",
    system_prompt=CODE_EXPERT_PROMPT,
    tools=[analyze_code],
    max_iterations=10,
)


# === DATA ANALYST SUBAGENT ===

DATA_ANALYST_PROMPT = """Tu es un analyste de données expert.

Ton rôle :
1. Collecter et analyser des données
2. Identifier des patterns et insights
3. Présenter des conclusions actionnables

Format de sortie :
- Insights clés (3-5 bullet points)
- Score de confiance
- Recommandations

IMPORTANT : Résume, n'inclus PAS les données brutes ou calculs intermédiaires."""


@tool
def analyze_dataset(data_description: str) -> str:
    """Analyse de données (placeholder)."""
    return f"Analyse des données: {data_description[:100]}..."


data_analyst_subagent = SubAgent(
    name="data-analyst",
    description="Analyste de données spécialisé. Collecte, analyse et extrait des insights de données. Fournit des recommandations basées sur l'analyse. Pour tâches analytiques complexes.",
    system_prompt=DATA_ANALYST_PROMPT,
    tools=[analyze_dataset],
)


# === WRITER SUBAGENT ===

WRITER_PROMPT = """Tu es un rédacteur professionnel expert.

Ton rôle :
1. Transformer des informations techniques en contenu clair
2. Adapter le ton et le style selon l'audience
3. Structurer le contenu de manière logique

Format de sortie :
- Contenu bien structuré
- Langage clair et professionnel
- Longueur adaptée au besoin

IMPORTANT : Sois concis. Qualité > Quantité."""


writer_subagent = SubAgent(
    name="professional-writer",
    description="Rédacteur professionnel. Transforme des informations en contenu clair et structuré. Adapte le ton selon l'audience. Pour création de documentation, rapports, communications.",
    system_prompt=WRITER_PROMPT,
    tools=None,
)


# === QUICK HELPER (General Purpose) ===

QUICK_HELPER_PROMPT = """Tu es un assistant polyvalent et efficace.

Ton rôle :
1. Traiter rapidement des tâches simples
2. Fournir des réponses directes et concises
3. Utiliser les outils disponibles de manière efficace

IMPORTANT : Garde tes réponses courtes et précises."""


quick_helper_subagent = SubAgent(
    name="quick-helper",
    description="Assistant polyvalent pour tâches simples et rapides. Répond directement sans analyse approfondie. Pour questions factuelles, calculs simples, tâches directes.",
    system_prompt=QUICK_HELPER_PROMPT,
    tools=None,
)


# Liste de tous les subagents par défaut
DEFAULT_SUBAGENTS = [
    research_subagent,
    code_expert_subagent,
    data_analyst_subagent,
    writer_subagent,
    quick_helper_subagent,
]


def get_default_subagents() -> list[SubAgent]:
    """
    Retourne la liste des subagents par défaut.

    Returns:
        Liste des subagents spécialisés prédéfinis
    """
    return DEFAULT_SUBAGENTS.copy()
