"""
critic.py — Agent Guardrail anti-hallucination.

Vérifie factuellement si la réponse générée est fidèle au contexte
fourni par le retriever. Utilise le mode structured output de LangChain
pour forcer un verdict JSON strict via un schéma Pydantic.

Le verdict est binaire :
- hallucination = True  → la réponse contient des informations non présentes
                           dans le contexte (fabrication, invention, extrapolation)
- hallucination = False → la réponse est fidèle au contexte fourni
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import OPENAI_API_KEY, MODEL_GPT4O_MINI


# ============================================
# Schéma Pydantic pour la sortie structurée
# ============================================

class CriticVerdict(BaseModel):
    """Verdict du critique anti-hallucination + contrôle de préfixe."""

    hallucination: bool = Field(
        description=(
            "True si la réponse contient des informations qui ne sont PAS "
            "présentes dans le contexte fourni (hallucination détectée). "
            "False si la réponse est fidèle et cohérente avec le contexte."
        )
    )
    prefix_respecte: bool = Field(
        description=(
            "True si la réponse commence EXACTEMENT par la chaîne "
            "'OK Colin -> ' (avec l'espace après la flèche). "
            "False si le préfixe est absent, mal orthographié ou précédé "
            "d'un quelconque caractère (espace, guillemet, saut de ligne)."
        )
    )
    raison: str = Field(
        description=(
            "Explication concise du verdict. Précise si le rejet est dû "
            "à une hallucination, à un préfixe manquant, ou aux deux."
        )
    )


# ============================================
# Initialisation du LLM critique
# ============================================
_llm_critic = ChatOpenAI(
    model=MODEL_GPT4O_MINI,
    temperature=0.0,          # Déterministe pour la vérification factuelle
    openai_api_key=OPENAI_API_KEY,
).with_structured_output(CriticVerdict)


# ============================================
# Prompt système du critique
# ============================================
_CRITIC_SYSTEM_PROMPT = """\
Tu es un vérificateur factuel rigoureux. Ton rôle est double :
1. Vérifier si la réponse est fidèle au contexte source (anti-hallucination).
2. Vérifier si la réponse respecte la règle de formatage obligatoire.

DÉFINITION D'UNE HALLUCINATION :
- Toute affirmation dans la réponse qui N'EST PAS supportée par le contexte fourni.
- L'invention de noms de tables, de champs, de fonctionnalités ou de chiffres \
  qui n'apparaissent pas dans le contexte.
- L'extrapolation non fondée au-delà de ce que le contexte affirme explicitement.

CE QUI N'EST PAS UNE HALLUCINATION :
- Les reformulations fidèles du contexte.
- Les synthèses ou résumés qui restent factuellement corrects.
- Les réponses qui admettent explicitement ne pas avoir l'information.

CONTRÔLE DE PRÉFIXE OBLIGATOIRE :
- La réponse DOIT commencer EXACTEMENT par la chaîne : "OK Colin -> "
- Aucun espace, guillemet, saut de ligne ou caractère ne doit précéder cette chaîne.
- Si le préfixe est absent ou mal formé, prefix_respecte doit être False.

CONSIGNE :
Analyse méticuleusement la réponse sur les DEUX axes (hallucination ET préfixe). \
Remplis les trois champs du verdict en conséquence.
"""


# ============================================
# API publique
# ============================================

def critique(context: str, generation: str) -> CriticVerdict:
    """
    Vérifie si la génération est fidèle au contexte fourni.
    
    Compare chaque affirmation de la réponse générée avec le contexte
    source et renvoie un verdict structuré (hallucination oui/non + raison).
    
    Args:
        context: Le bloc de contexte fusionné (RAG + Mem0) qui a servi
                 de base à la génération.
        generation: La réponse produite par l'agent générateur.
    
    Returns:
        CriticVerdict avec le champ `hallucination` (bool) et `raison` (str).
    """
    user_message = (
        f"=== CONTEXTE SOURCE ===\n{context}\n=== FIN DU CONTEXTE ===\n\n"
        f"=== RÉPONSE À VÉRIFIER ===\n{generation}\n=== FIN DE LA RÉPONSE ==="
    )

    messages = [
        SystemMessage(content=_CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    verdict: CriticVerdict = _llm_critic.invoke(messages)
    return verdict
