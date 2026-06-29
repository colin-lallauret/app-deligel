"""
retriever.py — Agent de recherche hybride (RAG + Mémoire dynamique).

Fusionne deux sources de contexte en un bloc unique :
1. Recherche sémantique dans le vector store ChromaDB (fichiers .md du projet)
2. Interrogation de la mémoire dynamique Mem0 (faits/préférences utilisateur)

Le contexte fusionné est ensuite injecté dans le prompt du générateur.
"""

from __future__ import annotations

from src.config import RETRIEVER_TOP_K
from src.database.rag_storage import get_vectorstore
from src.agents.memory_updater import Mem0Client


# ============================================
# Instance globale du client mémoire
# ============================================
_mem0_client = Mem0Client()


# ============================================
# API publique
# ============================================

def retrieve(question: str, user_id: str) -> str:
    """
    Recherche hybride : base de connaissances projet + mémoire utilisateur.
    
    Étapes :
    1. Interroge ChromaDB pour extraire les top-k chunks les plus pertinents
       par rapport à la question posée.
    2. Interroge la mémoire Mem0 pour récupérer les faits connus de cet
       utilisateur (préférences, décisions passées, etc.).
    3. Fusionne les deux sources en un bloc de contexte structuré.
    
    Args:
        question: La question posée par l'utilisateur.
        user_id: Identifiant unique de l'utilisateur courant.
    
    Returns:
        Un bloc de texte structuré contenant le contexte fusionné,
        prêt à être injecté dans le prompt du générateur.
    """
    # --- 1. Recherche sémantique dans ChromaDB ---
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_TOP_K},
    )
    relevant_docs = retriever.invoke(question)

    # Formater les chunks avec leurs métadonnées source
    knowledge_chunks: list[str] = []
    for doc in relevant_docs:
        source = doc.metadata.get("source_file", "inconnu")
        section = doc.metadata.get("section_title", "")
        header = f"[Source: {source} | Section: {section}]"
        knowledge_chunks.append(f"{header}\n{doc.page_content}")

    knowledge_context = "\n\n---\n\n".join(knowledge_chunks) if knowledge_chunks else (
        "Aucun document pertinent trouvé dans la base de connaissances."
    )

    # --- 2. Interrogation de la mémoire dynamique Mem0 ---
    user_memories = _mem0_client.get_user_memories(user_id)

    if user_memories:
        memory_context = "\n".join(f"- {fact}" for fact in user_memories)
    else:
        memory_context = "Aucun historique ou préférence enregistré pour cet utilisateur."

    # --- 3. Fusion en un bloc de contexte structuré ---
    fused_context = (
        "## Contexte Projet (Base de Connaissances)\n"
        f"{knowledge_context}\n\n"
        "## Contexte Utilisateur (Mémoire Dynamique)\n"
        f"{memory_context}"
    )

    return fused_context
