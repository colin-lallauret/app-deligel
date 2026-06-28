# Spécifications Techniques - Architecture & Outils

## 1. Choix du Framework Mobile : Expo & React Native
Pour répondre au besoin multiplateforme et sécuriser l'accès bas niveau au matériel, le choix s'est porté sur **React Native associé à l'écosystème Expo**[cite: 14].

### Avantages Majeurs :
* **Code Unique :** Un seul code source maintenu pour générer l'application Android et iOS[cite: 14].
* **Accès Natif Stable :** Gestion des modules matériels : puce GPS (`expo-location`), appareil photo (`expo-camera`), et système de fichiers local (`expo-file-system`)[cite: 14].
* **Mises à jour à chaud (EAS Update) :** Permet de pousser des correctifs de code critiques sans réinstaller l'application manuellement[cite: 14].

## 2. Stratégie du Mode Déconnecté (Offline-First)
Pour garantir la persistance des données sans aucun réseau, l'application s'appuie sur une base de données locale installée sur le stockage physique de l'appareil, couplée à un moteur de synchronisation[cite: 14].

* **Base de données embarquée :** **SQLite** (via la bibliothèque native Expo) ou **WatermelonDB**[cite: 14]. Permet un stockage permanent, sans limite restrictive de taille, préservé par le système d'exploitation[cite: 14].
* **Moteur de Synchro :** Implémentation d'un orchestrateur de file d'attente (Sync Queue)[cite: 14]. Toutes les actions effectuées hors-ligne (création de tournée, de client, validation) sont stockées localement[cite: 14]. Dès que le gestionnaire de connectivité (`@react-native-community/netinfo`) détecte le retour du réseau, la file d'attente est dépilée vers le serveur via l'API[cite: 14].

## 3. Stockage, Cache et Optimisation des Médias (Photos)
* **Traitement à la prise de vue :** Afin de ne pas saturer l'espace disque du smartphone et d'alléger les transferts réseau, les photos capturées par `expo-camera` passent immédiatement par la bibliothèque `expo-image-manipulator` avant sauvegarde. Elles sont redimensionnées (largeur max 1080px) et compressées en JPEG (qualité 70%).
* **Téléchargement Initial :** Lors de la préparation matinale de la tournée, les photos repères des clients sont écrites sur le disque dur via `expo-file-system`[cite: 14].
* **Rendu Hors-Ligne :** Les composants d'affichage d'images pointent vers le chemin local du fichier (`file://...`) garantissant un affichage instantané même sans réseau[cite: 14].

## 4. Méthode de Déploiement Privé (Hors Stores Publics)
L'application étant strictement réservée à l'usage interne de l'entreprise, elle ne sera pas publiée de manière ouverte[cite: 14].

* **Déploiement Android :** Génération d'un fichier binaire `.apk` via les serveurs de build d'Expo (`eas build --platform android`)[cite: 14]. Distribué de manière privée (Google Drive sécurisé ou clé USB)[cite: 14].
* **Déploiement iOS :** Utilisation de la méthode **Internal Builds** (Ad-Hoc) d'Expo[cite: 14]. Les identifiants uniques (UDID) des iPhone de l'équipe sont enregistrés sur un compte Apple Developer Privé[cite: 14]. L'installation s'effectue simplement Over-The-Air via le scan d'un **QR Code privé** fourni par Expo[cite: 14].