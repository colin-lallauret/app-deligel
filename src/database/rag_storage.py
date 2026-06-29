"""
rag_storage.py — Indexation des fichiers de spécifications dans ChromaDB.

Ce module :
1. Charge les 5 fichiers .md de spécifications du projet DeligelApp.
2. Découpe chaque document en chunks avec chevauchement (RecursiveCharacterTextSplitter).
3. Enrichit chaque chunk avec des métadonnées (fichier source, titre de section).
4. Indexe le tout dans un vector store ChromaDB persisté localement.

Usage standalone (pour reconstruire l'index) :
    python -m src.database.rag_storage
"""

from __future__ import annotations

import re
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import (
    OPENAI_API_KEY,
    MODEL_EMBEDDING,
    KNOWLEDGE_DIR,
    KNOWLEDGE_FILES,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)


# ============================================
# Fonctions utilitaires
# ============================================

def _extract_section_title(text: str) -> str:
    """
    Extrait le titre de la première section Markdown trouvée dans un chunk.
    
    Cherche les en-têtes de niveau 1 à 3 (# à ###).
    Retourne "Contenu général" si aucun titre n'est trouvé.
    """
    match = re.search(r"^#{1,3}\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else "Contenu général"


def _load_and_split_documents() -> list[Document]:
    """
    Charge les fichiers .md de spécifications et les découpe en chunks.
    
    Chaque chunk est enrichi avec les métadonnées suivantes :
    - source_file : nom du fichier d'origine (ex: "base_de_donnees.md")
    - section_title : titre de la section Markdown la plus proche
    
    Returns:
        Liste de Documents LangChain prêts à être indexés.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",    # Priorité aux titres de section niveau 2
            "\n### ",   # Puis niveau 3
            "\n\n",     # Puis double saut de ligne (paragraphes)
            "\n",       # Puis simple saut de ligne
            " ",        # Puis espaces
        ],
        keep_separator=True,
    )

    all_documents: list[Document] = []

    for filename in KNOWLEDGE_FILES:
        filepath = Path(KNOWLEDGE_DIR) / filename

        if not filepath.exists():
            print(f"  ⚠️  Fichier introuvable, ignoré : {filepath}")
            continue

        # Lecture du contenu brut du fichier
        raw_text = filepath.read_text(encoding="utf-8")

        # Découpage en chunks
        chunks = text_splitter.split_text(raw_text)

        for i, chunk_text in enumerate(chunks):
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "source_file": filename,
                    "section_title": _extract_section_title(chunk_text),
                    "chunk_index": i,
                },
            )
            all_documents.append(doc)

        print(f"  ✅ {filename} → {len(chunks)} chunks")

    return all_documents


def _get_embeddings() -> OpenAIEmbeddings:
    """Retourne l'instance du modèle d'embeddings OpenAI configuré."""
    return OpenAIEmbeddings(
        model=MODEL_EMBEDDING,
        openai_api_key=OPENAI_API_KEY,
    )


# ============================================
# API publique
# ============================================

def rebuild_index() -> Chroma:
    """
    Reconstruit entièrement l'index vectoriel ChromaDB.
    
    Supprime l'index existant puis réindexe tous les fichiers .md.
    À appeler quand les fichiers de spécifications changent.
    
    Returns:
        Instance ChromaDB prête à l'emploi.
    """
    print("\n🔄 Reconstruction de l'index vectoriel ChromaDB...")
    print(f"   Répertoire de persistance : {CHROMA_PERSIST_DIR}")

    # Charger et découper les documents
    documents = _load_and_split_documents()

    if not documents:
        raise RuntimeError(
            "Aucun document trouvé. Vérifiez que les fichiers .md "
            "sont présents dans le répertoire du projet."
        )

    # Créer le vector store ChromaDB (écrase l'existant)
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=_get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
    )

    print(f"\n✅ Index construit avec succès : {len(documents)} chunks indexés.")
    return vectorstore


def get_vectorstore() -> Chroma:
    """
    Retourne l'instance ChromaDB existante (sans réindexer).
    
    Si l'index n'existe pas encore, le construit automatiquement.
    
    Returns:
        Instance ChromaDB prête pour la recherche sémantique.
    """
    persist_path = Path(CHROMA_PERSIST_DIR)

    # Vérifie si le répertoire ChromaDB existe et contient des données
    if persist_path.exists() and any(persist_path.iterdir()):
        return Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=_get_embeddings(),
            collection_name=CHROMA_COLLECTION_NAME,
        )

    # Sinon, construire l'index pour la première fois
    print("📦 Index vectoriel introuvable. Construction initiale...")
    return rebuild_index()


# ============================================
# Point d'entrée standalone
# ============================================

if __name__ == "__main__":
    rebuild_index()
