# Spécifications Fonctionnelles - Améliorations Futures

Ce document définit les spécifications des modules à intégrer lors des prochaines phases de développement de l'application DeligelApp. Ces évolutions transformeront l'outil de suivi de tournée en une application de gestion commerciale (ERP/POS mobile) complète.

---

## 1. Module de Gestion des Stocks (Chambre Froide & Camions)

Afin d'éviter les ruptures de stock et de sécuriser la chaîne du froid, l'application intégrera un suivi de l'inventaire en temps réel.

### A. Gestion du Stock Dépôt (Chambre Froide)
* **Interface Administrateur (Cloud) :** Permet d'ajouter des références de produits (SKU, nom, prix HT/TTC, taux de TVA, photo).
* **Suivi des Quantités :** Affichage des niveaux de stock physiques dans la chambre froide.
* **Alertes Rupture :** Notification visuelle et envoi d'alertes par e-mail/SMS lorsque le niveau de stock d'un produit descend sous le seuil d'alerte (`alert_threshold`).

### B. Chargement du Camion (Le Matin)
* **Inventaire de Départ :** Avant de démarrer sa tournée, le livreur saisit ou valide les quantités de produits qu'il transfère de la chambre froide vers son camion.
* **Validation Double :** L'administrateur valide le transfert, ce qui décrémente automatiquement le stock de la chambre froide globale et crédite la table `truck_stock` pour la tournée active.

### C. Retour de Tournée (Le Soir)
* **Reconciliation :** Au retour au dépôt, le système compare le stock théorique restant dans le camion (Quantité chargée - Quantités vendues) avec le comptage physique réel du livreur.
* **Réintégration :** Les invendus conformes sont réintégrés en chambre froide (crédite la chambre froide et vide le stock camion). Les pertes éventuelles (produit abîmé, rupture de froid) sont déclarées avec un motif spécifique.

---

## 2. Module de Vente chez le Client (POS Mobile)

Ce module permet au livreur de réaliser des ventes en direct lorsqu'il se trouve chez le client, même sans connexion Internet.

### A. Processus d'Entrée en Vente
1. Depuis la fiche client ou la liste de la tournée, le vendeur clique sur le bouton **"Vente chez le client"**.
2. Si le client n'était pas planifié, le vendeur peut rechercher le client par son nom dans la base de données locale ou en créer un à la volée.

### B. Prise de Commande (Catalogue & Panier)
* **Recherche et Filtres (Haute Performance) :** Accès au catalogue complet des produits synchronisés localement. Pour garantir une saisie rapide sans latence même avec des milliers de références, la recherche utilise **SQLite FTS (Full Text Search)** pour filtrer instantanément par mot-clef (ex: "colin", "glace") ou par catégorie lors de la frappe.
* **Disponibilité en Temps Réel :** Affichage de la quantité disponible *dans le camion* (`qty_loaded` - `qty_sold`). Le vendeur ne peut pas vendre un produit s'il n'est plus en stock physique dans son camion (sécurité anti-erreur).
* **Panier Interactif :** Sélection rapide des quantités avec des boutons `+` et `-`. Le montant total HT, TVA (5.5% ou 20%) et TTC s'actualise instantanément à l'écran.

### C. Validation et Génération de Ticket
* **Génération de Facture / Ticket :** Une fois le panier validé, l'application génère un ticket de caisse virtuel complet au format PDF.
* **Informations obligatoires sur le ticket :** 
  * En-tête de l'entreprise (Nom, SIRET, Coordonnées).
  * Date, heure et numéro de facture unique (ex: `F-YYYYMMDD-DRIVER_ID-SEQ` pour garantir l'unicité offline sans collision).
  * Informations client (Nom, Adresse).
  * Liste détaillée : Nom du produit, quantité, prix unitaire HT, taux de TVA appliqué, prix total TTC.
  * Récapitulatif : Total HT, Total TVA par taux, et Total TTC final.
* **Résilience Offline & Partage :** Le ticket PDF généré est écrit dans le stockage permanent de l'appareil (`expo-file-system`). Si le partage immédiat par SMS, e-mail ou WhatsApp échoue à cause d'une zone blanche, le ticket reste disponible dans l'historique d'achat du client pour un renvoi ultérieur. L'application propose également l'impression physique directe via une imprimante thermique Bluetooth portable (qui ne requiert aucun réseau).

### D. Encaissement et Intégration TPE
* **Paiement par TPE :**
  1. L'application affiche clairement le montant TTC total de la facture.
  2. Le vendeur saisit manuellement ce montant sur son terminal de paiement électronique (TPE) physique.
  3. Une fois la transaction acceptée par le TPE, le vendeur valide la transaction dans l'application en sélectionnant le mode de paiement **"TPE / Carte Bancaire"**.
* **Autres Modes de Paiement :** Possibilité de sélectionner **"Espèces"** ou **"Chèque"**.
* **Clôture :** La commande passe au statut `paid`, la vente est enregistrée localement avec le mode de paiement et ajoutée à la file de synchronisation offline.

### E. Gestion des Erreurs et Annulations de Vente (Avoirs)
* **Intégrité de Facturation :** Pour respecter la législation comptable (inviolabilité et séquence continue des numéros de factures), une commande validée et finalisée ne peut pas être modifiée ou supprimée de la base de données.
* **Workflow d'Avoir / Remboursement :**
  1. Si le livreur commet une erreur de saisie ou si le client refuse un produit après validation, le livreur accède à la commande dans l'historique et clique sur **"Générer un avoir"**.
  2. Le système crée une commande de type `'refund'` liée à la facture d'origine. Les quantités de produits retournés sont saisies en négatif (ex: `-2 Filet de Colin`).
  3. Le système incrémente automatiquement le stock théorique du camion pour y réintégrer les produits retournés.
  4. Un ticket d'avoir PDF est généré et stocké localement, indiquant le montant négatif à rembourser ou à déduire.


---

## 3. Module d'Historique d'Achat Client

Pour personnaliser la relation commerciale et anticiper les besoins des clients, le vendeur doit avoir accès au passif d'achat.

### A. Affichage sur la Fiche Client
* **Résumé Rapide :** Date de la dernière commande, montant total dépensé, et mode de paiement habituel.
* **Liste Chronologique :** Historique des commandes triées de la plus récente à la plus ancienne.

### B. Détail de Commande Historique
* En cliquant sur une ancienne commande, le vendeur affiche le détail des articles achetés (quantités et prix appliqués).
* Un bouton **"Dupliquer la commande"** permet de charger rapidement le panier avec les mêmes produits pour accélérer la vente du jour.

### C. Stratégie Offline-First
* Lors de la synchronisation matinale, l'application télécharge localement l'historique des 5 dernières ventes de chaque client présent dans la tournée du jour. Cela évite d'encombrer le stockage du téléphone tout en garantissant l'accès aux données clés sur le terrain en zone blanche.
