"""
graph.py — Orchestrateur LangGraph du système Self-RAG.

Définit le workflow cyclique du système Self-RAG avec gestion d'état :

    START → retrieve → generate → critic ─┬─→ memory_update → END
                                           │
                          (hallucination    │ (hallucination=True
                           =False)         │  AND attempt < MAX)
                                           │
                                           └──→ generate (avec feedback)

Le State LangGraph contient la question, le contexte, la génération,
le feedback du critique, le compteur de tentatives et le verdict final.

La boucle de régénération est limitée à MAX_RETRIES tentatives pour
éviter les boucles infinies.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.config import MAX_RETRIES
from src.agents.retriever import retrieve
from src.agents.generator import generate
from src.agents.critic import critique
from src.agents.memory_updater import Mem0Client


# ============================================
# Instance globale du client mémoire
# ============================================
_mem0_client = Mem0Client()


# ============================================
# Définition du State LangGraph
# ============================================

class SelfRAGState(TypedDict):
    """État partagé entre tous les nœuds du graphe Self-RAG."""

    question: str               # Question posée par l'utilisateur
    user_id: str                # Identifiant de l'utilisateur courant
    context: str                # Contexte fusionné (RAG + Mem0)
    generation: str             # Dernière réponse générée
    critic_feedback: str        # Feedback du critique (raison du rejet)
    attempt: int                # Compteur de tentatives (1 à MAX_RETRIES)
    is_hallucination: bool      # Résultat du dernier verdict critique
    prefix_respecte: bool       # True si la réponse commence par "OK Colin -> "
    final_answer: str           # Réponse finale validée (ou avertissement)


# ============================================
# Nœuds du graphe
# ============================================

def retrieve_node(state: SelfRAGState) -> dict:
    """
    Nœud de recherche : interroge la base de connaissances et la mémoire Mem0.
    
    Fusionne le contexte projet (ChromaDB) et le contexte utilisateur (Mem0)
    en un bloc unique pour le générateur.
    """
    print("\n🔍 [Retrieve] Recherche dans la base de connaissances et Mem0...")

    context = retrieve(
        question=state["question"],
        user_id=state["user_id"],
    )

    return {
        "context": context,
        "attempt": 1,
        "critic_feedback": "",
        "is_hallucination": False,
        "prefix_respecte": True,
    }


def generate_node(state: SelfRAGState) -> dict:
    """
    Nœud de génération : produit une réponse basée sur le contexte.
    
    En cas de régénération (attempt > 1), le feedback du critique est
    transmis au générateur pour guider la correction.
    """
    attempt = state["attempt"]
    feedback = state.get("critic_feedback") or None

    if attempt > 1:
        print(f"\n🔄 [Generate] Régénération — Tentative {attempt}/{MAX_RETRIES}...")
    else:
        print("\n✍️  [Generate] Génération de la réponse...")

    generation = generate(
        question=state["question"],
        context=state["context"],
        previous_feedback=feedback,
        attempt=attempt,
    )

    return {"generation": generation}


def critic_node(state: SelfRAGState) -> dict:
    """
    Nœud critique : vérifie la fidélité au contexte ET le respect du préfixe.
    
    Produit un verdict structuré (hallucination, prefix_respecte, raison).
    """
    print("\n🔎 [Critic] Vérification anti-hallucination + contrôle préfixe...")

    verdict = critique(
        context=state["context"],
        generation=state["generation"],
    )

    # Log des résultats
    if verdict.hallucination:
        print(f"  ❌ Hallucination détectée : {verdict.raison}")
    else:
        print(f"  ✅ Contenu fidèle au contexte")

    if not verdict.prefix_respecte:
        print(f"  ❌ Préfixe 'OK Colin -> ' manquant ou incorrect")
    else:
        print(f"  ✅ Préfixe 'OK Colin -> ' respecté")

    return {
        "is_hallucination": verdict.hallucination,
        "prefix_respecte": verdict.prefix_respecte,
        "critic_feedback": verdict.raison,
    }


def memory_update_node(state: SelfRAGState) -> dict:
    """
    Nœud de mise à jour mémoire : extrait et mémorise les faits clés.
    
    Analyse la conversation (question + réponse finale) pour enrichir
    la mémoire utilisateur Mem0.
    """
    print("\n🧠 [Memory] Mise à jour de la mémoire utilisateur...")

    # Construire le texte de la conversation
    conversation = (
        f"Question de l'utilisateur : {state['question']}\n\n"
        f"Réponse du système : {state['generation']}"
    )

    _mem0_client.update_memories(
        user_id=state["user_id"],
        conversation=conversation,
    )

    # Déterminer la réponse finale
    final_answer = state["generation"]

    is_failed = state["is_hallucination"] or not state["prefix_respecte"]
    if is_failed:
        failure_reasons: list[str] = []
        if state["is_hallucination"]:
            failure_reasons.append("hallucination détectée")
        if not state["prefix_respecte"]:
            failure_reasons.append("préfixe 'OK Colin -> ' manquant")

        final_answer = (
            f"⚠️ AVERTISSEMENT : Après {state['attempt']} tentatives, le système "
            f"n'a pas pu produire une réponse conforme. "
            f"Raisons : {', '.join(failure_reasons)}. "
            f"Dernier feedback : « {state['critic_feedback']} ».\n\n"
            f"Voici la dernière réponse produite (à prendre avec précaution) :\n\n"
            f"{state['generation']}"
        )

    return {"final_answer": final_answer}


# ============================================
# Arête conditionnelle après le critique
# ============================================

def _route_after_critic(state: SelfRAGState) -> str:
    """
    Décide du prochain nœud après le verdict du critique.
    
    La réponse est rejetée si :
    - hallucination == True (contenu inventé)
    - OU prefix_respecte == False (préfixe 'OK Colin -> ' manquant)
    
    Returns:
        "regenerate" : si rejet ET tentatives restantes
        "finalize"   : si réponse validée OU tentatives épuisées
    """
    is_rejected = state["is_hallucination"] or not state["prefix_respecte"]

    if not is_rejected:
        # Réponse validée sur les 2 axes → finaliser
        return "finalize"

    # Construire le feedback d'erreur pour la régénération
    rejection_reasons: list[str] = []
    if state["is_hallucination"]:
        rejection_reasons.append("Tu as halluciné du contenu non présent dans le contexte.")
    if not state["prefix_respecte"]:
        rejection_reasons.append("Tu as oublié le préfixe obligatoire 'OK Colin -> '.")

    combined_feedback = " ".join(rejection_reasons) + f" Détail : {state['critic_feedback']}"

    if state["attempt"] < MAX_RETRIES:
        # Tentatives restantes → régénérer avec feedback strict
        print(f"  🔄 Rejet → régénération avec feedback : {combined_feedback}")
        return "regenerate"

    # Tentatives épuisées → finaliser avec avertissement
    print(f"\n⚠️  Nombre maximum de tentatives atteint ({MAX_RETRIES}).")
    return "finalize"


def _increment_attempt(state: SelfRAGState) -> dict:
    """Incrémente le compteur de tentatives avant la régénération."""
    return {"attempt": state["attempt"] + 1}


# ============================================
# Construction du graphe LangGraph
# ============================================

def build_graph() -> StateGraph:
    """
    Construit et compile le graphe LangGraph du système Self-RAG.
    
    Architecture du workflow :
        START → retrieve → generate → critic ──┬── finalize → memory_update → END
                                                │
                                    (hallucination + retry)
                                                │
                                    increment_attempt → generate → critic → ...
    
    Returns:
        Le graphe compilé, prêt à être invoqué avec .invoke().
    """
    # Définition du graphe avec le type d'état
    graph = StateGraph(SelfRAGState)

    # --- Ajout des nœuds ---
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("critic", critic_node)
    graph.add_node("increment_attempt", _increment_attempt)
    graph.add_node("memory_update", memory_update_node)

    # --- Arêtes fixes ---
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "critic")

    # --- Arête conditionnelle après le critique ---
    graph.add_conditional_edges(
        "critic",
        _route_after_critic,
        {
            "regenerate": "increment_attempt",
            "finalize": "memory_update",
        },
    )

    # Après l'incrémentation, retour au générateur
    graph.add_edge("increment_attempt", "generate")

    # Après la mise à jour mémoire, fin du workflow
    graph.add_edge("memory_update", END)

    # --- Compilation ---
    compiled_graph = graph.compile()
    return compiled_graph


# ============================================
# Instance pré-compilée pour import direct
# ============================================
self_rag_graph = build_graph()
