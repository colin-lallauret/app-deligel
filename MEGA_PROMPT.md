# 🧊 MÉGA PROMPT — Initialisation Complète du Projet DeligelApp

> Ce prompt contient l'intégralité du contexte métier, technique, architectural et de la modélisation de données pour initialiser le projet DeligelApp from scratch. Il est conçu pour être donné à un LLM (ou à un développeur) afin de générer l'ossature et le code complet de l'application sans bugs ni ambiguïtés de démarrage.

---

## RÔLE

Tu es un développeur senior fullstack spécialisé en React Native / Expo et en architecture Offline-First. Tu vas initialiser et développer une application mobile privée appelée **DeligelApp** pour une entreprise de livraison de produits surgelés à domicile.

---

## CONTEXTE MÉTIER

L'entreprise est une structure à taille humaine spécialisée dans la **vente et la livraison de produits surgelés à domicile**. Chaque employé possède sa propre liste de clients attitrés et réalise des tournées régulières pour livrer les commandes directement chez les particuliers.

**Problème actuel :** Les tournées ne sont enregistrées sur aucun support numérique centralisé. La connaissance des clients, de leur adresse exacte, de leurs habitudes de passage et des spécificités d'accès repose entièrement sur la mémoire des livreurs. Cela engendre :
- Perte d'historique en cas de départ ou d'absence d'un employé.
- Difficulté d'optimisation des trajets.
- Impossibilité pour un administrateur d'avoir une vision globale de l'activité commerciale.

**Objectifs du projet :**
1. Pérenniser le savoir-faire et l'historique des clients par tournée.
2. Sécuriser le travail sur le terrain grâce à un fonctionnement **100% autonome en zone blanche** (sans réseau).
3. Préparer l'avenir en structurant les données pour l'arrivée future d'un profil Administrateur.
4. Permettre une transition future vers une gestion commerciale complète (POS/facturation terrain + gestion des stocks chambre froide & camions).

---

## PROFILS UTILISATEURS

Le système intègre nativement deux rôles :
- **Livreur / Chauffeur / Vendeur (`driver`)** : Accède à ses tournées, valide ses passages, consulte les fiches clients, capture les positions GPS, ajoute des notes/photos historiques, réalise des ventes en direct, génère des tickets PDF et saisit les encaissements.
- **Administrateur (`admin`)** : Tous les droits du driver + accès aux données de toutes les tournées + droit exclusif de créer/modifier/attribuer les tournées + gestion complète du catalogue produits et niveaux de stock en chambre froide.

---

## STACK TECHNIQUE IMPOSÉE (EXPO SDK 51)

| Composant | Technologie | Version / Détails |
|:--|:--|:--|
| **Framework Mobile** | **React Native + Expo** | **Expo SDK 51** (Managed Workflow) |
| **Routing / Navigation** | **Expo Router** | File-based navigation, TypeScript typings |
| **Base locale** | **SQLite** | `expo-sqlite` (New API avec requêtes asynchrones) |
| **Base de données Cloud**| **Supabase** | `PostgreSQL` + `Supabase Storage` (seaux pour photos) |
| **State Global & Cache** | **Zustand + React Query** | Zustand (panier, état de sync) / React Query (requêtes api) |
| **Identifiants (UUID)** | `expo-crypto` | `Crypto.randomUUID()` pour l'offline (UUID v4 natif) |
| **GPS** | `expo-location` | Avec fallback / temporisation 3 secondes |
| **Appareil Photo** | `expo-camera` | Manipulation via `expo-image-manipulator` |
| **Fichiers & PDF** | `expo-file-system` | Cache images, PDF locaux via `expo-print` et `expo-sharing` |
| **Détection réseau** | `@react-native-community/netinfo` | Détecteur de statut pour envoi de la file d'attente |
| **Sécurité Offline** | `expo-secure-store` | Stockage sécurisé des credentials cryptés du livreur |

---

## STRUCTURE DE DOSSIERS DU PROJET

L'application doit respecter l'arborescence Expo Router suivante :
```
DeligelApp/
├── app/                        # Expo Router - Écrans de l'application
│   ├── _layout.tsx             # Layout racine (Providers Zustand, React Query, Theme)
│   ├── index.tsx               # Redirection automatique vers login ou dashboard
│   ├── (auth)/                 # Groupe d'authentification
│   │   ├── _layout.tsx
│   │   └── login.tsx           # Écran de connexion (supporte auth hors-ligne)
│   └── (driver)/               # Groupe des fonctionnalités Livreur
│       ├── _layout.tsx
│       ├── index.tsx           # Tableau de bord : liste des tournées du jour
│       ├── tour/
│       │   └── [id].tsx        # Tournée active : liste ordonnée des clients (code couleur)
│       └── client/
│           ├── [id].tsx        # Fiche client détaillée (GPS, photos, notes)
│           ├── [id]/
│           │   ├── sale.tsx    # POS Mobile : Catalogue produits, Panier, Validation
│           │   └── history.tsx # Historique d'achat : 5 dernières factures, duplication commande
├── src/
│   ├── components/             # Composants UI réutilisables (Boutons, Cartes, Modales)
│   ├── db/                     # Couche de données SQLite
│   │   ├── schema.ts           # Requêtes DDL de création de tables SQLite
│   │   ├── migrations.ts       # Gestion des migrations SQLite via user_version
│   │   └── client.ts           # Instance d'expo-sqlite et transactions natives
│   ├── hooks/                  # Custom React Hooks (useGPS, useSyncQueue)
│   ├── services/               # Logique d'API Supabase et synchronisation
│   │   ├── supabase.ts         # Client Supabase
│   │   └── sync.ts             # Algorithme de synchronisation bidirectionnelle
│   ├── store/                  # Gestion d'état global
│   │   ├── useCartStore.ts     # Panier de vente temporaire
│   │   └── useAuthStore.ts     # Informations de session locale
│   └── types/                  # Interfaces TypeScript partagées
│       └── index.ts            # Modèles métier (User, Client, Tour, Order, etc.)
├── .env.example                # Exemple de configuration d'environnement
├── app.json                    # Configuration Expo
└── package.json
```

---

## VARIABLES D'ENVIRONNEMENT (`.env`)

Toutes les variables de configuration doivent être préfixées par `EXPO_PUBLIC_` pour être injectées dans le bundle par Expo SDK 51 :
```env
EXPO_PUBLIC_SUPABASE_URL=https://votre-projet.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## MAPPING DE TYPES : SQLITE vs POSTGRESQL

Pour pallier l'absence de types natifs dans SQLite, le mapping suivant doit être strictement implémenté :

| Type Conceptuel | SQLite (Local) | PostgreSQL (Supabase) | Format / Règle |
|:--|:--|:--|:--|
| **UUID** | `TEXT` | `UUID` | Chaîne de 36 caractères générée par `Crypto.randomUUID()` |
| **BOOLEAN** | `INTEGER` | `BOOLEAN` | `0` pour False, `1` pour True |
| **DECIMAL** | `REAL` | `NUMERIC(10,2)` | Arrondi systématique à 2 décimales en JS via `Number.toFixed(2)` |
| **TIMESTAMP** | `TEXT` | `TIMESTAMPTZ` | Chaîne au format ISO 8601 UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`) |
| **DATE** | `TEXT` | `DATE` | Chaîne au format `YYYY-MM-DD` |
| **TIME** | `TEXT` | `TIME` | Chaîne au format `HH:mm:ss` |

---

## SCHÉMA DÉTAILLÉ DES TABLES SQLITE (LOCALES)

Toutes les requêtes de création de table locale doivent être exécutées dans `src/db/schema.ts` lors du premier démarrage si `PRAGMA user_version = 0`.

### Table 1 — `users`
```sql
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT DEFAULT 'driver',
    created_at TEXT NOT NULL
);
```

### Table 2 — `tours`
```sql
CREATE TABLE IF NOT EXISTS tours (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    date_tour TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_synced INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### Table 3 — `clients`
```sql
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    created_by_user_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    address TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    photo_url TEXT,
    local_photo_path TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_synced INTEGER DEFAULT 0,
    FOREIGN KEY(created_by_user_id) REFERENCES users(id)
);
```

### Table 4 — `delivery_logs`
```sql
CREATE TABLE IF NOT EXISTS delivery_logs (
    id TEXT PRIMARY KEY,
    tour_id TEXT NOT NULL,
    client_id TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    target_time TEXT,
    checked_in_at TEXT,
    driver_comment TEXT,
    updated_at TEXT NOT NULL,
    is_synced INTEGER DEFAULT 0,
    FOREIGN KEY(tour_id) REFERENCES tours(id),
    FOREIGN KEY(client_id) REFERENCES clients(id)
);
```

### Table 5 — `products`
```sql
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price_ht REAL NOT NULL,
    vat_rate REAL NOT NULL DEFAULT 5.50,
    price_ttc REAL NOT NULL,
    photo_url TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### Table 6 — `cold_storage_stock`
```sql
CREATE TABLE IF NOT EXISTS cold_storage_stock (
    id TEXT PRIMARY KEY,
    product_id TEXT UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    alert_threshold INTEGER DEFAULT 10,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
```

### Table 7 — `truck_stock`
```sql
CREATE TABLE IF NOT EXISTS truck_stock (
    id TEXT PRIMARY KEY,
    tour_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    qty_loaded INTEGER NOT NULL DEFAULT 0,
    qty_sold INTEGER NOT NULL DEFAULT 0, -- Dédupliqué et écrit localement
    qty_returned INTEGER DEFAULT 0,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(tour_id) REFERENCES tours(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);
```

### Table 8 — `orders`
```sql
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    tour_id TEXT NOT NULL,
    delivery_log_id TEXT, -- NULLABLE pour permettre des ventes spontanées hors-tournée
    total_ht REAL NOT NULL,
    total_vat REAL NOT NULL,
    total_ttc REAL NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT DEFAULT 'paid',
    invoice_number TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    is_synced INTEGER DEFAULT 0,
    FOREIGN KEY(client_id) REFERENCES clients(id),
    FOREIGN KEY(tour_id) REFERENCES tours(id),
    FOREIGN KEY(delivery_log_id) REFERENCES delivery_logs(id)
);
```

### Table 9 — `order_items`
```sql
CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_ht REAL NOT NULL,
    vat_rate REAL NOT NULL,
    total_ht REAL NOT NULL,
    total_ttc REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);
```

### Table 10 — `sync_queue` (Table Technique de File d'Attente)
```sql
CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    action TEXT NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    payload TEXT NOT NULL, -- JSON stringifié des colonnes modifiées
    created_at TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT
);
```

---

## STRATÉGIE DE MIGRATION SQLITE

Toute évolution de la base de données SQLite locale doit être orchestrée dans `src/db/migrations.ts`.
- Au démarrage, exécuter : `PRAGMA user_version;`
- Si la version retournée est inférieure à la dernière version cible (ex: version 2 après ajout du module POS), exécuter les scripts SQL de migration séquentiels.
- Mettre à jour la version via `PRAGMA user_version = X;` dans la transaction de migration.

---

## LOGIQUE DE SYNCHRONISATION BIDIRECTIONNELLE

L'algorithme de synchronisation dans `src/services/sync.ts` fonctionne selon un mécanisme **double canal** :

### 1. Canal Pull (Incrémental Matinal)
Lors du clic sur "Préparer ma tournée du jour" au dépôt en Wi-Fi :
- Récupérer du Cloud PostgreSQL uniquement les lignes modifiées depuis le dernier `updated_at` local stocké.
- Mettre à jour séquentiellement dans SQLite local : `products` ➔ `tours` ➔ `clients` ➔ `delivery_logs` (et l'historique d'achat des 5 dernières ventes de chaque client planifié dans la tournée du jour).

### 2. Canal Push (Sync Queue avec Transaction Offline)
Toute action hors-ligne (ex: validation de passage, commande POS, création de client, photo repère) doit :
1. Être écrite dans la table SQLite locale appropriée.
2. Être insérée dans `sync_queue` au sein de la même transaction de BDD locale pour garantir l'atomicité.
3. Déclencher une tentative d'envoi en arrière-plan si le réseau est détecté.
4. Pour l'envoi : dépiler la `sync_queue` par ordre chronologique strict de dépendance des clés primaires, pousser vers Supabase, marquer le statut de la file d'attente à `'completed'` et passer la colonne `is_synced` de la table métier à `1` (True).

---

## GESTION SPÉCIFIQUE DES FACTURES ET STOCKS

### Séquence de Facturation Hors-Ligne
Pour respecter la législation comptable sans réseau :
- Le numéro de facture `invoice_number` est construit au format `F-YYYYMMDD-DRIVER_ID-SEQ`.
- Le numéro séquentiel `SEQ` est stocké et incrémenté localement dans une table de métadonnées SQLite. Il redémarre à `1` à chaque changement de date.
- Un avoir de remboursement (`refund`) crée une nouvelle ligne dans `orders` avec des montants totaux calculés négativement et un type de transaction dédié, liée par l'historique mais conservant l'inviolabilité de la facture initiale.

### Transaction de Vente et Stock Camion
Lorsqu'une vente POS est validée hors-ligne :
1. Créer la ligne `orders`.
2. Créer les lignes `order_items`.
3. Mettre à jour `truck_stock` en décrémentant les stocks locaux (`qty_sold = qty_sold + quantity`).
4. Tout ceci est exécuté dans une **transaction SQLite unique** pour prévenir les ventes d'articles hors-stock en cas d'annulation ou crash applicatif.

---

## GESTION DES EXCENTRICITÉS MATÉRIELLES (PERMISSIONS & FALLBACKS)

- **GPS (`expo-location`)** :
  - Temporisation de 3 secondes requise pour stabiliser la puce GPS de l'appareil.
  - Si la permission est refusée ou introuvable après la temporisation, afficher une modale de saisie de coordonnées manuelles ou autoriser l'utilisation de placeholders `(0.000000, 0.000000)` avec flag d'avertissement visuel pour l'administrateur.
- **Photos & Caméra (`expo-camera`)** :
  - Si l'accès caméra est bloqué, permettre d'importer une photo depuis la galerie de l'appareil.
  - La compression via `expo-image-manipulator` (largeur max 1080px, qualité 70% JPEG) est obligatoire avant toute sauvegarde locale dans `expo-file-system`.
  - Supabase Storage : Les photos sont poussées vers le seau `client-photos` avec le chemin standardisé `{client_id}/repere_{timestamp}.jpg`.

---

## INSTRUCTIONS D'INITIALISATION ET DÉPENDANCES

Pour lancer le projet, exécute d'abord la création de l'application :
```bash
npx -y create-expo-app@latest ./ --template blank
```

Installe ensuite les dépendances critiques en spécifiant la compatibilité Expo SDK 51 :
```bash
npx expo install expo-sqlite expo-location expo-camera expo-image-manipulator expo-file-system expo-secure-store expo-print expo-sharing expo-crypto @react-native-community/netinfo
npm install zustand @tanstack/react-query @supabase/supabase-js
```

Puis, génère l'ensemble du code TypeScript en te conformant à l'arborescence, au typage SQLite strict, et à la logique de la file d'attente hors-ligne décrits dans ce document.
