"""
config.py — Configuration centralisée du système Self-RAG DeligelApp.

Charge les variables d'environnement depuis le fichier .env et expose
toutes les constantes utilisées par les agents, le vector store et
l'orchestrateur LangGraph.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ============================================
# Chargement des variables d'environnement
# ============================================
# Recherche le .env à la racine du projet (parent de src/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-VOTRE"):
    raise RuntimeError(
        "⚠️  OPENAI_API_KEY non configurée. "
        "Renseignez votre clé dans le fichier .env à la racine du projet."
    )

# ============================================
# Modèles LLM & Embeddings (OpenAI)
# ============================================
MODEL_GPT4O: str = "gpt-4o"                       # Génération principale + Critique
MODEL_GPT4O_MINI: str = "gpt-4o-mini"             # Tâches rapides (extraction mémoire, critique)
MODEL_EMBEDDING: str = "text-embedding-3-small"    # Modèle d'embeddings pour le RAG

# ============================================
# Chemins vers les fichiers de spécifications
# ============================================
KNOWLEDGE_DIR: Path = _PROJECT_ROOT  # Les fichiers .md sont à la racine du projet

KNOWLEDGE_FILES: list[str] = [
    "1_contexte_entreprise.md",
    "2_fonctionnement_application.md",
    "3_outils_techniques.md",
    "4_ameliorations_futures.md",
    "base_de_donnees.md",
]

# ============================================
# Paramètres de Chunking (Découpage des docs)
# ============================================
CHUNK_SIZE: int = 1000       # Taille maximale d'un chunk (en caractères)
CHUNK_OVERLAP: int = 200     # Chevauchement entre chunks consécutifs

# ============================================
# Paramètres du Vector Store (ChromaDB)
# ============================================
CHROMA_PERSIST_DIR: str = str(Path(__file__).resolve().parent / "database" / "chroma_db")
CHROMA_COLLECTION_NAME: str = "deligel_knowledge"

# ============================================
# Paramètres du Retriever
# ============================================
RETRIEVER_TOP_K: int = 5     # Nombre de chunks retournés par recherche sémantique

# ============================================
# Paramètres de la boucle Self-RAG
# ============================================
MAX_RETRIES: int = 3         # Nombre maximum de tentatives de régénération

# ============================================
# Mémoire Dynamique (Mem0 simulation)
# ============================================
MEM0_STORE_PATH: str = str(Path(__file__).resolve().parent / "database" / "mem0_store.json")
