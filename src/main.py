"""
main.py — Point d'entrée CLI du système Self-RAG DeligelApp.

Lance une boucle interactive où l'utilisateur peut poser des questions
sur le projet DeligelApp. Chaque question est traitée par le graphe
LangGraph Self-RAG (retrieve → generate → critic → memory_update).

Commandes spéciales :
    /rebuild  — Réindexe les fichiers .md dans ChromaDB
    /memory   — Affiche la mémoire Mem0 de l'utilisateur courant
    /clear    — Efface la mémoire Mem0 de l'utilisateur courant
    /quit     — Quitte l'application
"""

from __future__ import annotations

import sys

from src.graph import self_rag_graph, SelfRAGState
from src.database.rag_storage import rebuild_index
from src.agents.memory_updater import Mem0Client


# ============================================
# Configuration de la session
# ============================================
DEFAULT_USER_ID = "user_default"


def _print_banner() -> None:
    """Affiche la bannière d'accueil."""
    print("\n" + "=" * 60)
    print("  🧊 DeligelApp — Self-RAG System (LangGraph)")
    print("  Assistant expert de l'application DeligelApp")
    print("=" * 60)
    print("  Commandes : /rebuild | /memory | /clear | /quit")
    print("=" * 60 + "\n")


def _handle_command(command: str, user_id: str, mem0: Mem0Client) -> bool:
    """
    Gère les commandes spéciales.
    
    Returns:
        True si la commande a été traitée, False sinon.
    """
    cmd = command.strip().lower()

    if cmd == "/quit":
        print("\n👋 Au revoir !")
        sys.exit(0)

    if cmd == "/rebuild":
        rebuild_index()
        return True

    if cmd == "/memory":
        memories = mem0.get_user_memories(user_id)
        if memories:
            print(f"\n🧠 Mémoire de l'utilisateur '{user_id}' :")
            for i, fact in enumerate(memories, 1):
                print(f"  {i}. {fact}")
        else:
            print(f"\n🧠 Aucune mémoire enregistrée pour '{user_id}'.")
        return True

    if cmd == "/clear":
        mem0._memories.pop(user_id, None)
        mem0._save_to_disk()
        print(f"\n🗑️  Mémoire effacée pour '{user_id}'.")
        return True

    return False


def main() -> None:
    """Boucle interactive principale du système Self-RAG."""
    _print_banner()

    mem0 = Mem0Client()
    user_id = DEFAULT_USER_ID

    while True:
        try:
            question = input("📝 Votre question : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Au revoir !")
            break

        if not question:
            continue

        # Vérifier les commandes spéciales
        if question.startswith("/"):
            if _handle_command(question, user_id, mem0):
                print()
                continue
            else:
                print(f"  ❓ Commande inconnue : {question}")
                print()
                continue

        # --- Exécution du graphe Self-RAG ---
        print("\n" + "-" * 50)

        initial_state: SelfRAGState = {
            "question": question,
            "user_id": user_id,
            "context": "",
            "generation": "",
            "critic_feedback": "",
            "attempt": 0,
            "is_hallucination": False,
            "prefix_respecte": True,
            "final_answer": "",
        }

        try:
            result = self_rag_graph.invoke(initial_state)
        except Exception as e:
            print(f"\n❌ Erreur lors du traitement : {e}")
            print()
            continue

        # --- Affichage du résultat ---
        final_answer = result.get("final_answer", "Aucune réponse produite.")
        attempt_count = result.get("attempt", 1)
        was_hallucination = result.get("is_hallucination", False)

        print("\n" + "=" * 50)
        print("📋 RÉPONSE FINALE")
        print("=" * 50)
        print(final_answer)
        print("-" * 50)
        print(f"  📊 Tentatives : {attempt_count}/{3}")
        print(f"  🛡️  Verdict critique : {'⚠️ Hallucination (non corrigée)' if was_hallucination else '✅ Validée'}")
        print("-" * 50 + "\n")


# ============================================
# Point d'entrée
# ============================================
if __name__ == "__main__":
    main()
