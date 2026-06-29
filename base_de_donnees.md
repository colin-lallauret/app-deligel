# Architecture de la Base de Données (Schéma Relationnel Final)

Voici la modélisation finale de la base de données. Ce schéma doit être rigoureusement identique dans la base de données centrale Cloud (ex: PostgreSQL/Supabase) et être fidèlement répliqué dans la base locale du téléphone (SQLite/WatermelonDB).

> [!IMPORTANT]
> **Règles d'Identifiants et de Synchronisation (Offline-First) :**
> 1. **Identifiants uniques :** Afin d'éviter toute collision de clés primaires lors de la création de lignes hors-ligne (ex: nouveaux clients, nouvelles ventes), tous les identifiants (`id`) utilisent le format **UUID v4** généré par l'appareil client (stocké sous forme de `TEXT`/`VARCHAR(36)` sous SQLite, et de type `UUID` sous PostgreSQL). Les clés primaires auto-incrémentées classiques sont proscrites.
> 2. **Ordre strict de Synchronisation :** Pour respecter les contraintes d'intégrité référentielle lors de la poussée vers le serveur, la file d'attente locale (Sync Queue) doit être traitée dans l'ordre suivant :
>    `users` ➔ `clients` ➔ `tours` ➔ `delivery_logs` ➔ `products` ➔ `orders` ➔ `order_items` ➔ `truck_stock`


## 1. Table `users` (Utilisateurs / Employés)
Stocke les informations d'authentification et définit les droits d'accès[cite: 15].

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK (Généré par le serveur) | Identifiant unique de l'utilisateur |
| `email` | VARCHAR(255) | Unique, NOT NULL | Adresse email de connexion[cite: 15] |
| `password_hash`| VARCHAR(255) | NOT NULL | Empreinte sécurisée du mot de passe[cite: 15] |
| `first_name` | VARCHAR(100) | NOT NULL | Prénom de l'employé[cite: 15] |
| `last_name` | VARCHAR(100) | NOT NULL | Nom de l'employé[cite: 15] |
| `role` | VARCHAR(20) | DEFAULT 'driver' | Rôle de l'utilisateur : `'driver'` ou `'admin'`[cite: 15] |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création du compte[cite: 15] |

## 2. Table `tours` (Tournées)
Représente une boucle de livraison spécifique associée à un employé pour une date donnée[cite: 15].

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique de la tournée (généré client/serveur) |
| `user_id` | UUID | FK (`users.id`) | Livreur assigné à cette tournée |
| `name` | VARCHAR(100) | NOT NULL | Nom de la tournée (ex: "Zone Nord - Mardi")[cite: 15] |
| `date_tour` | DATE | NOT NULL | Date prévue de réalisation de la tournée[cite: 15] |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Statut de la tournée : `'pending'`, `'active'`, `'completed'`[cite: 15] |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date d'édition de la ligne[cite: 15] |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Horodatage pour la gestion des conflits[cite: 15] |
| `is_synced` | BOOLEAN | DEFAULT FALSE | `true` si la tournée (créée hors-ligne) est synchronisée sur le Cloud[cite: 15] |

## 3. Table `clients` (Fiches Répertoires Permanentes)
Regroupe les coordonnées et les informations géographiques permanentes de chaque client. Un client n'est pas réécrit à chaque tournée[cite: 15].

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique du client (généré client-side) |
| `first_name` | VARCHAR(100) | NOT NULL | Prénom du client[cite: 15] |
| `last_name` | VARCHAR(100) | NOT NULL | Nom de famille du client[cite: 15] |
| `phone` | VARCHAR(20) | | Numéro de téléphone pour appel 1-clic[cite: 15] |
| `address` | TEXT | NOT NULL | Adresse postale textuelle complète[cite: 15] |
| `latitude` | DECIMAL(10, 8) | | Coordonnée GPS de latitude calculée[cite: 15] |
| `longitude` | DECIMAL(11, 8) | | Coordonnée GPS de longitude calculée[cite: 15] |
| `photo_url` | TEXT | | URL de la photo historique de repère sur le Cloud[cite: 15] |
| `local_photo_path`| TEXT | | Chemin local du fichier image sur le téléphone[cite: 15] |
| `notes` | TEXT | | Notes permanentes pour le guidage terrain[cite: 15] |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création de la fiche client[cite: 15] |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Horodatage pour la gestion des conflits[cite: 15] |
| `is_synced` | BOOLEAN | DEFAULT FALSE | `true` si le client (créé à la volée) est synchronisé[cite: 15] |

## 4. Table `delivery_logs` (Suivi, Ordre et Validation des passages)
Fait le pont entre une tournée et un client. Elle enregistre l'ordre de passage choisi pour la journée et l'état du passage[cite: 15].

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique du log (généré client-side) |
| `tour_id` | UUID | FK (`tours.id`) | Liaison à la tournée correspondante |
| `client_id` | UUID | FK (`clients.id`) | Client concerné par l'action |
| `sort_order` | INT | NOT NULL, DEFAULT 0 | Index numérique pour l'ordre de passage[cite: 15] |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending'| Statut du passage : `'pending'` (gris), `'delivered'` (vert), `'absent'` (rouge)[cite: 15] |
| `target_time` | TIME | | Horaire théorique de passage estimé pour ce jour précis[cite: 15] |
| `checked_in_at`| TIMESTAMP | | Heure précise du clic de validation (Heure réelle de passage)[cite: 15] |
| `driver_comment`| TEXT | | Note de livraison spécifique à ce jour précis (ex: "glacière absente")[cite: 15] |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Horodatage pour la gestion des conflits de réorganisation. |
| `is_synced` | BOOLEAN | DEFAULT FALSE | Flag local : `true` si l'action est synchronisée sur le Cloud. |

## 5. Table `products` (Catalogue Produits - Évolution)
Stocke le référentiel des produits surgelés disponibles à la vente.

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique du produit (généré par le serveur) |
| `sku` | VARCHAR(50) | Unique, NOT NULL | Code de référence unique (ex: "SURG-COL-001") |
| `name` | VARCHAR(255) | NOT NULL | Nom commercial du produit |
| `description` | TEXT | | Description du produit (contenance, allergènes, etc.) |
| `price_ht` | DECIMAL(10, 2) | NOT NULL | Prix unitaire de vente Hors Taxes |
| `vat_rate` | DECIMAL(5, 2) | NOT NULL, DEFAULT 5.50 | Taux de TVA applicable en % (ex: 5.50, 20.00) |
| `price_ttc` | DECIMAL(10, 2) | NOT NULL | Prix unitaire Toutes Taxes Comprises |
| `photo_url` | TEXT | | URL de la photo produit sur le Cloud |
| `is_active` | BOOLEAN | DEFAULT TRUE | `false` si le produit est retiré de la vente |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date d'ajout du produit au catalogue |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Horodatage pour la synchronisation |

## 6. Table `cold_storage_stock` (Stock Chambre Froide - Évolution)
Gère les niveaux de stock physiques présents dans la chambre froide du dépôt principal (administré via le Cloud).

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique de la ligne de stock |
| `product_id` | UUID | FK (`products.id`), Unique | Référence du produit |
| `quantity` | INT | NOT NULL, DEFAULT 0 | Quantité physique actuellement en stock au dépôt |
| `alert_threshold`| INT | DEFAULT 10 | Seuil d'alerte pour les ruptures de stock |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Date de la dernière modification de stock |

## 7. Table `truck_stock` (Stock Camion de Tournée - Évolution)
Stocke l'inventaire embarqué dans le camion du livreur pour une tournée spécifique (remplissage le matin, décrémentation lors des ventes).

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique du stock camion |
| `tour_id` | UUID | FK (`tours.id`), NOT NULL | Tournée concernée par ce stock |
| `product_id` | UUID | FK (`products.id`), NOT NULL | Produit chargé dans le camion |
| `qty_loaded` | INT | NOT NULL, DEFAULT 0 | Quantité chargée le matin au dépôt |
| `qty_sold` | INT | NOT NULL, DEFAULT 0 | Quantité vendue (valeur calculée à la volée via sum(order_items) pour éviter les incohérences) |
| `qty_returned` | INT | DEFAULT 0 | Quantité invendue retournée en chambre froide le soir |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Horodatage de synchronisation |

## 8. Table `orders` (Commandes / Factures Ventes - Évolution)
En-tête de la facture ou du ticket généré lors d'une vente directe chez un client.

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique de la vente (généré client-side) |
| `client_id` | UUID | FK (`clients.id`), NOT NULL | Client acheteur |
| `tour_id` | UUID | FK (`tours.id`), NOT NULL | Tournée dans laquelle s'effectue la vente |
| `delivery_log_id`| UUID | FK (`delivery_logs.id`), Unique | Liaison avec le journal de passage |
| `total_ht` | DECIMAL(10, 2) | NOT NULL | Somme des montants Hors Taxes |
| `total_vat` | DECIMAL(10, 2) | NOT NULL | Somme des montants de TVA |
| `total_ttc` | DECIMAL(10, 2) | NOT NULL | Montant total TTC à encaisser sur le TPE physique |
| `payment_method` | VARCHAR(30) | NOT NULL | Moyen de paiement utilisé (`'tpe'`, `'cash'`, `'check'`) |
| `payment_status` | VARCHAR(20) | DEFAULT 'paid' | Statut du paiement : `'paid'`, `'pending'`, `'failed'` |
| `invoice_number` | VARCHAR(100) | Unique, NOT NULL | Numéro de facture unique généré hors-ligne (ex: F-20260629-DRV01-001) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date et heure de l'achat |
| `is_synced` | BOOLEAN | DEFAULT FALSE | `true` si la vente est synchronisée vers le Cloud |

## 9. Table `order_items` (Lignes de Commande - Évolution)
Détail de chaque produit vendu dans une commande/facture spécifique.

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique de la ligne (généré client-side) |
| `order_id` | UUID | FK (`orders.id`), NOT NULL | Commande associée |
| `product_id` | UUID | FK (`products.id`), NOT NULL | Produit vendu |
| `quantity` | INT | NOT NULL | Quantité achetée |
| `unit_price_ht`| DECIMAL(10, 2) | NOT NULL | Prix unitaire HT appliqué au moment de l'achat (évite les variations futures de tarifs) |
| `vat_rate` | DECIMAL(5, 2) | NOT NULL | Taux de TVA appliqué au moment de l'achat |
| `total_ht` | DECIMAL(10, 2) | NOT NULL | Quantité * Prix HT unitaire |
| `total_ttc` | DECIMAL(10, 2) | NOT NULL | Quantité * Prix TTC unitaire |