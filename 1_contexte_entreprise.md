# Spécifications Fonctionnelles - Contexte & Métier

## 1. Présentation de l'Entreprise
L'entreprise est une structure à taille humaine spécialisée dans la **vente et la livraison de produits surgelés à domicile**.

Chaque employé possède sa propre liste de clients attitrés et réalise des tournées régulières pour livrer les commandes directement chez les particuliers.

## 2. La Problématique Actuelle
Actuellement, les tournées ne sont enregistrées sur **aucun support numérique centralisé**. La connaissance des clients, de leur adresse exacte, de leurs habitudes de passage et des spécificités d'accès repose entièrement sur la mémoire des livreurs. 

Cette absence de structure présente plusieurs risques :
* Perte d'historique en cas de départ ou d'absence d'un employé.
* Difficulté d'optimisation des trajets.
* Impossible pour un administrateur d'avoir une vision globale de l'activité commerciale.

## 3. Objectifs du Projet
Le but est de développer une **application mobile privée** permettant de :
1. **Pérenniser le savoir-faire** et l'historique des clients par tournée.
2. **Sécuriser le travail sur le terrain** grâce à un fonctionnement 100% autonome en zone blanche (sans réseau).
3. **Préparer l'avenir** en structurant les données pour l'arrivée future d'un profil Administrateur (gestionnaire de tournées).
4. **Permettre une transition future** vers une gestion commerciale complète en intégrant la vente de produits chez le client (POS/facturation terrain) et la gestion des stocks (chambre froide & camions).

## 4. Les Profils Utilisateurs (Évolution des Rôles)
Le système doit intégrer nativement une gestion des droits basée sur deux rôles distincts :
* **Livreur / Chauffeur / Vendeur (`driver`) :** Accède à ses tournées, valide ses passages, consulte les fiches clients, capture les positions GPS, ajoute des notes/photos historiques, et (à terme) réalise des ventes en direct, édite des tickets de caisse et enregistre les encaissements TPE.
* **Administrateur (`admin`) :** Possède tous les droits du livreur, accède aux données de l'ensemble des tournées, et dispose du droit exclusif de créer/modifier/attribuer les tournées (option activable à distance pour verrouiller l'autonomie actuelle des livreurs). De plus, l'administrateur aura la gestion complète du catalogue de produits et des niveaux de stock en chambre froide.
