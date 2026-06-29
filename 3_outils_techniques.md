# Spécifications Techniques - Architecture & Outils

## 1. Choix du Framework Mobile : Expo & React Native
Pour répondre au besoin multiplateforme et sécuriser l'accès bas niveau au matériel, le choix s'est porté sur **React Native associé à l'écosystème Expo**[cite: 14].

### Avantages Majeurs :
* **Code Unique :** Un seul code source maintenu pour générer l'application Android et iOS[cite: 14].
* **Accès Natif Stable :** Gestion des modules matériels : puce GPS (`expo-location`), appareil photo (`expo-camera`), et système de fichiers local (`expo-file-system`)[cite: 14].
* **Mises à jour à chaud (EAS Update) :** Permet de pousser des correctifs de code critiques sans réinstaller l'application manuellement[cite: 14].

## 2. Stratégie du Mode Déconnecté (Offline-First)
Pour garantir la persistance des données sans aucun réseau, l'application s'appuie sur une base de données locale installée sur le stockage physique de l'appareil, couplée à un moteur de synchronisation bidirectionnel et à un système de mise à jour à chaud du code.

* **Base de données embarquée :** **SQLite** (via la bibliothèque native Expo) ou **WatermelonDB**. Permet un stockage permanent, sans limite restrictive de taille, préservé par le système d'exploitation.
* **Moteur de Synchro (Double Canaux) :**
  * **Synchronisation active / manuelle (Matin & Soir) :** Le matin au dépôt (Wi-Fi), le livreur effectue un chargement complet ("Pull") pour récupérer les mises à jour structurelles : catalogue produits, tarifs actualisés, tournée du jour, historique client et stock camion. Le soir, la clôture force le dépôt ("Push") des données finales.
  * **Synchronisation passive / arrière-plan (Pendant la journée) :** Utilise un orchestrateur de file d'attente (Sync Queue). Toutes les actions hors-ligne (validation, ventes, notes) y sont stockées. Dès que `@react-native-community/netinfo` détecte une connexion (4G/5G), la file d'attente est envoyée au serveur via des requêtes API REST sécurisées.
* **Mises à jour Applicatives à Chaud (EAS Update) :** Au lancement matinal lors du clic sur "Préparer la tournée", l'application interroge les serveurs Expo. Si un nouveau lot de code JS/assets est disponible (correctifs de bugs, nouvelles fonctionnalités), il est téléchargé et appliqué immédiatement en tâche de fond, assurant que tous les livreurs travaillent avec la même version de l'application.
* **Authentification Sécurisée Hors-Ligne :** Afin de permettre au livreur de se connecter même en zone blanche sans accès au serveur d'authentification central, les jetons de session et l'empreinte chiffrée (hash) des identifiants utilisateur du dernier employé connecté sont stockés localement de manière sécurisée via `expo-secure-store`.


## 3. Stockage, Cache et Optimisation des Médias (Photos)
* **Traitement à la prise de vue :** Afin de ne pas saturer l'espace disque du smartphone et d'alléger les transferts réseau, les photos capturées par `expo-camera` passent immédiatement par la bibliothèque `expo-image-manipulator` avant sauvegarde. Elles sont redimensionnées (largeur max 1080px) et compressées en JPEG (qualité 70%).
* **Téléchargement Initial :** Lors de la préparation matinale de la tournée, les photos repères des clients sont écrites sur le disque dur via `expo-file-system`[cite: 14].
* **Rendu Hors-Ligne :** Les composants d'affichage d'images pointent vers le chemin local du fichier (`file://...`) garantissant un affichage instantané même sans réseau[cite: 14].

## 4. Méthode de Déploiement Privé (Hors Stores Publics)
L'application étant strictement réservée à l'usage interne de l'entreprise, elle ne sera pas publiée de manière ouverte[cite: 14].

* **Déploiement Android :** Génération d'un fichier binaire `.apk` via les serveurs de build d'Expo (`eas build --platform android`)[cite: 14]. Distribué de manière privée (Google Drive sécurisé ou clé USB)[cite: 14].
* **Déploiement iOS :** Utilisation de la méthode **Internal Builds** (Ad-Hoc) d'Expo. Les identifiants uniques (UDID) des iPhone de l'équipe sont enregistrés sur un compte Apple Developer Privé. L'installation s'effectue simplement Over-The-Air via le scan d'un **QR Code privé** fourni par Expo.

## 5. Spécifications Techniques pour les Évolutions Futures
Pour supporter le module POS/Vente et la gestion des stocks, de nouveaux composants techniques seront nécessaires :
* **Base de données Locale Étendue :** Le catalogue produit complet (produits, prix, TVA, images) sera stocké dans SQLite/WatermelonDB. La synchronisation devra être incrémentale (télécharger uniquement les modifications de produits depuis la dernière synchro pour limiter la consommation de données).
* **Mise en cache des Images de Produits :** Utilisation de la bibliothèque `expo-image` pour gérer un cache performant des photos de produits et éviter de re-télécharger les images à chaque affichage du catalogue hors-ligne.
* **Génération de Tickets PDF :** Intégration de la bibliothèque `expo-print` pour convertir un template HTML en fichier PDF localement. Ce PDF pourra être partagé via `expo-sharing` (par SMS, e-mail, WhatsApp) pour fournir un ticket dématérialisé au client.
* **Impression Bluetooth Optionnelle :** Pour l'impression physique sur ticket thermique de caisse, intégration d'une bibliothèque React Native gérant le protocole Bluetooth Low Energy (BLE) et les commandes ESC/POS pour envoyer les données textuelles structurées directement à l'imprimante portable du vendeur.