# Architecture de la Base de Données (Schéma Relationnel Final)

Voici la modélisation finale de la base de données. Ce schéma doit être rigoureusement identique dans la base de données centrale Cloud (ex: PostgreSQL/Supabase) et être fidèlement répliqué dans la base locale du téléphone (SQLite/WatermelonDB)[cite: 15].

## 1. Table `users` (Utilisateurs / Employés)
Stocke les informations d'authentification et définit les droits d'accès[cite: 15].

| Nom du Champ | Type de Donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID / INT | PK, Auto-incrément | Identifiant unique de l'utilisateur[cite: 15] |
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
| `id` | UUID / INT | PK, Auto-incrément | Identifiant unique de la tournée[cite: 15] |
| `user_id` | UUID / INT | FK (`users.id`) | Livreur assigné à cette tournée[cite: 15] |
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
| `id` | UUID / INT | PK, Auto-incrément | Identifiant unique du client[cite: 15] |
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
| `id` | UUID / INT | PK, Auto-incrément | Identifiant unique du log[cite: 15] |
| `tour_id` | UUID / INT | FK (`tours.id`) | Liaison à la tournée correspondante[cite: 15] |
| `client_id` | UUID / INT | FK (`clients.id`) | Client concerné par l'action[cite: 15] |
| `sort_order` | INT | NOT NULL, DEFAULT 0 | Index numérique pour l'ordre de passage[cite: 15] |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending'| Statut du passage : `'pending'` (gris), `'delivered'` (vert), `'absent'` (rouge)[cite: 15] |
| `target_time` | TIME | | Horaire théorique de passage estimé pour ce jour précis[cite: 15] |
| `checked_in_at`| TIMESTAMP | | Heure précise du clic de validation (Heure réelle de passage)[cite: 15] |
| `driver_comment`| TEXT | | Note de livraison spécifique à ce jour précis (ex: "glacière absente")[cite: 15] |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Horodatage pour la gestion des conflits de réorganisation[cite: 15] |
| `is_synced` | BOOLEAN | DEFAULT FALSE | Flag local : `true` si l'action est synchronisée sur le Cloud[cite: 15] |