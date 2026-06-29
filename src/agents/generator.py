"""
generator.py — Agent de génération principale (Self-RAG).

Produit une réponse ancrée sur le contexte fourni par le retriever.
En cas de régénération (tentative > 1), le prompt intègre le feedback
du critique pour guider la correction et éviter la même erreur.
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import OPENAI_API_KEY, MODEL_GPT4O


# ============================================
# Initialisation du LLM de génération
# ============================================
_llm = ChatOpenAI(
    model=MODEL_GPT4O,
    temperature=0.3,          # Peu de créativité, on veut de la fidélité au contexte
    openai_api_key=OPENAI_API_KEY,
)

# ============================================
# Prompt système
# ============================================
_SYSTEM_PROMPT = """\
Tu es un assistant expert de l'application DeligelApp, une application mobile \
de gestion de tournées de livraison de produits surgelés.

RÈGLE DE FORMATAGE ABSOLUE ET NON NÉGOCIABLE :
→ Tu DOIS commencer CHAQUE réponse par la chaîne exacte : "OK Colin -> "
→ Aucun espace, aucun caractère, aucun saut de ligne ne doit précéder cette chaîne.
→ Le reste de ta réponse suit immédiatement après "OK Colin -> ".
→ Si tu oublies ce préfixe, ta réponse sera automatiquement rejetée.

RÈGLES STRICTES :
1. Réponds UNIQUEMENT en te basant sur le contexte fourni ci-dessous.
2. Si l'information demandée n'est pas présente dans le contexte, dis-le \
   explicitement : "OK Colin -> Cette information n'est pas disponible dans mes sources."
3. Ne fabrique JAMAIS de données, de noms de tables, de champs ou de \
   fonctionnalités qui ne sont pas mentionnés dans le contexte.
4. Cite tes sources quand c'est possible (nom du fichier de spécification).
5. Réponds en français.
"""



# ============================================
# API publique
# ============================================

def generate(
    question: str,
    context: str,
    previous_feedback: str | None = None,
    attempt: int = 1,
) -> str:
    """
    Génère une réponse à la question en s'appuyant sur le contexte fourni.
    
    Si c'est une tentative de régénération (attempt > 1), le feedback du
    critique est inclus dans le prompt pour guider la correction.
    
    Args:
        question: La question posée par l'utilisateur.
        context: Le bloc de contexte fusionné (RAG + Mem0) fourni par le retriever.
        previous_feedback: Le retour du critique si c'est une régénération.
                           None lors de la première tentative.
        attempt: Numéro de la tentative courante (1 = première, 2+ = régénération).
    
    Returns:
        La réponse générée par le LLM.
    """
    # Construction du message utilisateur
    user_parts: list[str] = []

    # Bloc de contexte
    user_parts.append(f"=== CONTEXTE ===\n{context}\n=== FIN DU CONTEXTE ===")

    # Si régénération, ajouter le feedback du critique
    if attempt > 1 and previous_feedback:
        user_parts.append(
            f"\n⚠️ ATTENTION — TENTATIVE {attempt} DE RÉGÉNÉRATION ⚠️\n"
            f"Le vérificateur a rejeté ta réponse précédente pour la raison suivante :\n"
            f"« {previous_feedback} »\n\n"
            f"Corrige ta réponse en te basant STRICTEMENT sur le contexte ci-dessus. "
            f"Ne reproduis pas la même erreur."
        )

    # Question de l'utilisateur
    user_parts.append(f"\nQuestion de l'utilisateur : {question}")

    user_message = "\n".join(user_parts)

    # Appel au LLM
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = _llm.invoke(messages)
    return response.content
