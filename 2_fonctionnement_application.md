# Spécifications Fonctionnelles - Fonctionnement de l'Application

## 1. Logique Globale du Mode "Offline-First"
L'application fonctionne sans connexion Internet active[cite: 13]. La synchronisation avec le serveur cloud se fait en arrière-plan[cite: 13].

### Cycle d'une Journée Type (Mode Routine) :
1. **Le Matin (Au dépôt) :** Le livreur clique sur **"Préparer ma tournée du jour"**[cite: 13]. L'application télécharge localement l'intégralité des données de la tournée (fiches clients, géolocalisation, notes et photos repères)[cite: 13]. Un voyant vert indique *"Tournée prête"*[cite: 13].
2. **Pendant la Tournée :** L'application affiche un bandeau visuel **"Mode Hors-ligne"** si le réseau coupe[cite: 13]. L'employé navigue, valide ses livraisons, modifie des notes ou prend une photo[cite: 13]. Tout est écrit instantanément en local[cite: 13].
3. **Au Retour du Réseau :** La synchronisation s'enclenche automatiquement[cite: 13]. Les données locales sont poussées vers le serveur central[cite: 13].

## 2. Fonctionnalités Clés sur le Terrain

### A. Gestion de la Tournée & Liste Ordonnée
* L'employé accède à sa liste de clients du jour triée de manière linéaire par **ordre de passage** (glisser-déposer disponible pour réorganiser l'itinéraire)[cite: 13].
* **Code Couleur de Statut :** Chaque client de la liste arbore un indicateur visuel : `Gris` (Passage non effectué), `Vert` (Livraison validée), `Rouge` (Client absent ou anomalie)[cite: 13].

### B. La Fiche Client Détaillée
Chaque fiche client regroupe les informations indispensables à la livraison[cite: 13] :
* Nom, Prénom, Téléphone (bouton d'appel en 1 clic via le réseau cellulaire classique)[cite: 13].
* Adresse textuelle complète et horaire de passage théorique prévu[cite: 13].
* **Position GPS Précise :** Un bouton permet de capturer instantanément la latitude/longitude courante de l'appareil (temporisation de 3 secondes pour stabiliser la puce GPS)[cite: 13]. Une mini-carte permet d'ajuster visuellement le marqueur ("pin") si nécessaire[cite: 13].
* **Navigation GPS :** Un bouton dédié ouvre l'application Google Maps native du téléphone avec les coordonnées exactes en paramètre[cite: 13].
* **Photo Historique "Repère" :** Une ou deux photos permanentes stockées dans l'appareil permettant d'identifier un point critique d'accès (portail, boîte aux lettres cachée)[cite: 13].
* **Notes Complémentaires :** Champ de texte libre pour les spécificités terrain (*"Sonner fort", "Laisser dans la glacière bleue"*)[cite: 13].

## 3. Gestion des Conflits de Synchronisation
* **Cloisonnement strict :** Un livreur ne peut pas éditer les données d'une tournée qui ne lui est pas explicitement attribuée[cite: 13].
* **Règle temporelle (Dernier Clic) :** En cas de modification simultanée, l'horodatage (`updated_at`) le plus récent écrase la version antérieure lors de la fusion[cite: 13].

## 4. Phase d'Amorçage (Remplissage Initial de l'Application)
Au lancement initial, l'application et la base de données centrale sont vides de contenu[cite: 13]. Le système permet aux livreurs de remplir l'application directement depuis le terrain[cite: 13].

### A. Création de Tournée par le Livreur
* Un bouton "Nouvelle Tournée" est accessible sur l'écran d'accueil pour le rôle `driver`[cite: 13].
* Le livreur saisit le nom de la zone et sélectionne la date pour initialiser la tournée dans la table `tours`[cite: 13].

### B. Ajout de Client à la Volée et Tri Automatique
* À l'intérieur d'une tournée active, un bouton "Ajouter un Client" permet d'ouvrir un formulaire de saisie[cite: 13].
* **Formulaire d'amorçage :** Le livreur remplit les champs textuels (Nom, Prénom, Téléphone, Adresse)[cite: 13].
* **Capture Initiale & Photo :** Un clic enregistre le point GPS précis de l'emplacement actuel et déclenche l'appareil photo pour enregistrer immédiatement l'image "repère" (automatiquement compressée par le système)[cite: 13].
* **Indexation Automatique :** Pour éviter de forcer le livreur à réordonner manuellement sa liste pendant sa route, chaque nouveau client ajouté reçoit automatiquement un index de tri `sort_order` incrémenté (+1 par rapport au dernier client inséré). L'itinéraire se construit ainsi de façon logique et chronologique en fonction du trajet réel de l'employé.