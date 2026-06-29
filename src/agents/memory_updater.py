"""
memory_updater.py — Agent de mémoire dynamique (simulation Mem0).

Gère la mémoire à long terme de chaque utilisateur :
- Extraction automatique de faits clés depuis les conversations
- Stockage et récupération des préférences / décisions / contraintes utilisateur
- Persistance locale en JSON (remplaçable par l'API Mem0 cloud)

Architecture :
    Le Mem0Client stocke les faits dans un dictionnaire indexé par user_id.
    Les faits sont persistés dans un fichier JSON local pour survivre aux
    redémarrages de l'application.
"""

from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import OPENAI_API_KEY, MODEL_GPT4O_MINI, MEM0_STORE_PATH


# ============================================
# Prompt d'extraction de faits
# ============================================
_EXTRACTION_PROMPT = """\
Tu es un extracteur de faits. Analyse la conversation ci-dessous et extrais \
les FAITS CLÉS, PRÉFÉRENCES et DÉCISIONS de l'utilisateur qui méritent \
d'être mémorisés pour les interactions futures.

RÈGLES :
1. Extrais uniquement des faits concrets et utiles (pas de bavardage).
2. Formule chaque fait comme une phrase courte et autonome.
3. Renvoie les faits sous forme de liste numérotée.
4. Si aucun fait nouveau ne mérite d'être mémorisé, renvoie "AUCUN".

Exemples de faits à extraire :
- "L'utilisateur préfère que les réponses soient en français."
- "Le client travaille sur le module de vente (POS mobile)."
- "L'utilisateur utilise PostgreSQL avec Supabase comme backend cloud."
"""


# ============================================
# Client Mem0 (Simulation locale)
# ============================================

class Mem0Client:
    """
    Simulation locale de l'API Mem0 pour la gestion de la mémoire utilisateur.
    
    Stocke les faits extraits de chaque conversation dans un dictionnaire
    en mémoire, persisté dans un fichier JSON local.
    
    Pour migrer vers Mem0 cloud, remplacez les méthodes get_user_memories()
    et update_memories() par des appels à l'API REST Mem0 sans modifier
    le reste de l'architecture.
    """

    def __init__(self, store_path: str = MEM0_STORE_PATH) -> None:
        """
        Initialise le client Mem0.
        
        Args:
            store_path: Chemin vers le fichier JSON de persistance.
        """
        self._store_path = Path(store_path)
        self._memories: dict[str, list[str]] = self._load_from_disk()
        self._llm = ChatOpenAI(
            model=MODEL_GPT4O_MINI,
            temperature=0.0,
            openai_api_key=OPENAI_API_KEY,
        )

    # --- Persistance ---

    def _load_from_disk(self) -> dict[str, list[str]]:
        """Charge les mémoires depuis le fichier JSON s'il existe."""
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_to_disk(self) -> None:
        """Persiste les mémoires dans le fichier JSON."""
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(
            json.dumps(self._memories, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # --- API publique ---

    def get_user_memories(self, user_id: str) -> list[str]:
        """
        Récupère les faits mémorisés pour un utilisateur donné.
        
        Args:
            user_id: Identifiant unique de l'utilisateur.
        
        Returns:
            Liste des faits mémorisés (chaînes de texte).
        """
        return self._memories.get(user_id, [])

    def update_memories(self, user_id: str, conversation: str) -> None:
        """
        Analyse une conversation et extrait les nouveaux faits à mémoriser.
        
        Utilise gpt-4o-mini pour identifier les faits clés, puis les ajoute
        à la mémoire de l'utilisateur (sans doublons).
        
        Args:
            user_id: Identifiant unique de l'utilisateur.
            conversation: Le texte complet de l'échange (question + réponse).
        """
        messages = [
            SystemMessage(content=_EXTRACTION_PROMPT),
            HumanMessage(content=f"Conversation à analyser :\n\n{conversation}"),
        ]

        response = self._llm.invoke(messages)
        raw_output = response.content.strip()

        # Si aucun fait à extraire
        if raw_output.upper() == "AUCUN" or not raw_output:
            return

        # Parser les faits numérotés
        new_facts: list[str] = []
        for line in raw_output.splitlines():
            # Nettoyer les préfixes de numérotation (1., 2., -, *, etc.)
            cleaned = line.strip().lstrip("0123456789.-)*• ").strip()
            if cleaned and len(cleaned) > 10:  # Ignorer les lignes trop courtes
                new_facts.append(cleaned)

        if not new_facts:
            return

        # Ajouter les faits (dédupliquation simple)
        existing = set(self._memories.get(user_id, []))
        added_count = 0
        for fact in new_facts:
            if fact not in existing:
                self._memories.setdefault(user_id, []).append(fact)
                existing.add(fact)
                added_count += 1

        if added_count > 0:
            self._save_to_disk()
            print(f"  🧠 Mem0 : {added_count} nouveau(x) fait(s) mémorisé(s) pour l'utilisateur '{user_id}'.")
