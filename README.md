# 🚴 Dashboard Vélib - Paris

## 🎯 Contexte du projet

Ce projet s'inscrit dans le cadre d'un test technique pour un poste de Data Engineer/DevOps. L'objectif était de démontrer la capacité à construire un pipeline de données complet, de la collecte à la visualisation, en respectant les bonnes pratiques DevOps.

**Objectifs principaux :**
- Construire un pipeline ETL robuste
- Manipuler des données temps réel via API
- Créer des visualisations interactives
- Respecter les principes 12-factor app
- Fournir une solution containerisée

## 📊 Choix du sujet

### Pourquoi les données Vélib ?

Ce projet vise à concevoir et déployer une plateforme de **surveillance en temps réel** des stations Vélib parisiennes. L'objectif est de collecter, traiter et analyser les données de disponibilité pour fournir des **insights actionnables** via un dashboard interactif.

**Critères de sélection :**
- **Données temps réel** : API disponible avec mise à jour fréquente
- **Utilité publique** : Service de mobilité urbaine impactant
- **Complexité modérée** : Assez de données pour une analyse intéressante
- **Potentiel d'analyse** : Multi-dimensionnel (spatial, temporel, typologique)

**Angles d'étude originaux :**
1. **Analyse de disponibilité temps réel** : Surveillance live du parc
2. **Répartition géographique** : Équité territoriale entre arrondissements
3. **Mix énergétique** : Ratio vélos électriques/mécaniques
4. **Performance opérationnelle** : Taux d'occupation et optimisation

 **Valeur Ajoutée :**
- 📡 **Collecte temps réel** des données via API OpenData
- 🗄️ **Stockage optimisé** dans une base SQLite
- 📊 **Visualisation intuitive** avec Streamlit
- 🐳 **Déploiement containerisé** avec Docker
- 🔄 **Pipeline automatisé** end-to-end
## 🔧 Stack technique

### Backend & Data Processing
- **Python 3.9+** : Langage principal
- **Pandas** : Manipulation des données
- **Requests** : Appels API HTTP
- **SQLite** : Base de données légère
- **SQLAlchemy** : ORM pour les requêtes

### Frontend & Visualisation
- **Streamlit** : Framework web pour dashboard
- **Plotly** : Graphiques interactifs
- **Mapbox** : Cartographie interactive

### DevOps & Conteneurisation
- **Docker** : Conteneurisation de l'application
- **Docker Compose** : Orchestration multi-conteneurs
- **Git** : Versioning du code


┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│    INGESTION     │───▶│    PROCESSING    │───▶│     STORAGE      │───▶│  VISUALIZATION   │
│                  │    │                  │    │                  │    │                  │
│ • fetch_velib_   │    │ • transform_velib│    │ • update_        │    │ • load_data()    │
│   data()         │    │   _data()        │    │   stations_data  │    │ • Streamlit      │
│ • API call       │    │ • Transformation │    │ • update_        │    │ • Dashboard      │
│ • Raw JSON       │    │ • Enrichment     │    │   availability_  │    │ • Charts         │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘


## 🚀 Guide d'Installation Rapide

### Prérequis Système
- **Python 3.9+** : [Télécharger Python](https://www.python.org/downloads/)
- **Docker** : [Installer Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** : [Installer Docker Compose](https://docs.docker.com/compose/install/)
- **Git** : [Installer Git](https://git-scm.com/downloads)

---

### 1. Clonage du Repository
```bash
git clone https://github.com/Barhoum1919/Data-Devops-Test.git
cd Data-Devops-Test
```
### 2. Lancer L'application Containerisé
#### Construction et lancement des conteneurs
```bash
docker-compose up --build
```
### 3. Accès à l'Application
#### Dashboard Principal : http://localhost:8501/




## 📈 Processus ETL

### Extraction (E)
**Source :** API OpenData Vélib - Ville de Paris
- **Endpoint :** https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=100
- **Fréquence :** Toutes les 5 minutes
- **Format :** JSON avec pagination
- **Données extraites :**
  - Informations stations (nom, capacité, localisation)
  - Disponibilité temps réel (vélos, places)
  - Métadonnées (statut, horaires)

### Transformation (T)
**Nettoyage et enrichissement :**
- Parsing des coordonnées géographiques
- Calcul du taux d'occupation
- Agrégation par arrondissement
- Normalisation des types de données
- Gestion des valeurs manquantes

**Calculs métier :**
- occupancy_rate = (vélos_disponibles / capacité) * 100
- total_bikes = ebikes + mechanical_bikes
- utilisation_rate = (total_bikes / capacité_totale) * 100

### Chargement (L)
**Destination :** Base SQLite relationnelle
- **Schéma optimisé :** Tables `stations` et `availability`
- **Indexation :** Sur `station_id` et `timestamp` pour performances
- **Historisation :** Conservation des données pour analyse temporelle

## 🔍 Justification Détaillée des Visualisations

### 1. 📊 **KPI Temps Réel (Section 1)**
**Pourquoi ces indicateurs ?**
- **Stations Actives** : Santé globale du système
- **Vélos Électriques/Mécaniques** : Suivi du mix énergétique
- **Places Libres** : Capacité d'accueil disponible
- **Taux d'Occupation** : Efficacité d'utilisation

**Valeur métier :**
- Alertes précoces sur les pénures
- Optimisation des tournées de redistribution
- Mesure de la performance du service

### 2. 🗺️ **Carte Interactive (Section 2)**
**Choix stratégique :**
- **Visualisation spatiale** : Compréhension immédiate de la répartition
- **Couleurs par vélos électriques** : Identification rapide des stations "premium"
- **Tailles proportionnelles** : Perception intuitive de la disponibilité

**Avantages :**
- Navigation géographique naturelle pour les usagers
- Identification des "zones mortes" sous-desservies
- Support à la décision pour l'implantation de nouvelles stations

### 3. 📈 **Graphiques Analytiques (Section 3)**
**Camembert - Répartition par type :**
- **Objectif** : Comprendre la stratégie de mix énergétique
- **Insight** : Les usagers privilégient-ils l'électrique ?
- **Décision** : Ajustement des investissements par type de vélo

**Top 10 Stations - Graphique en barres :**
- **Objectif** : Identifier les points névralgiques
- **Insight** : Stations les plus critiques à approvisionner
- **Décision** : Priorisation des interventions

### 4. 📋 **Tableau Détaillé (Section 4)**
**Pourquoi un tableau en plus des graphiques ?**
- **Données brutes** : Accès aux chiffres exacts
- **Recherche textuelle** : Navigation personnalisée
- **Export potentiel** : Base pour analyses complémentaires

**Valeur ajoutée :**
- Transparence totale des données
- Flexibilité d'analyse pour experts
- Audit trail des métriques affichées

### 5. 🕐 **Analyse Historique 24h (Section 5)**
**Justification de l'analyse temporelle :**

**Graphique d'évolution globale :**
- **Patterns journaliers** : Comprendre les pics de demande (8h-9h, 18h-19h)
- **Corrélation vélos/places** : Équilibre offre/demande
- **Tendances saisonnières** (à étendre) : Impact météo/événements

**Comparaison électrique vs mécanique :**
- **Comportement utilisateur** : Préférences horaires par type
- **Usure différentielle** : Planning de maintenance préventive
- **Impact énergétique** : Consommation électrique par créneau

**Taux d'occupation :**
- **Efficacité infrastructure** : Stations sur/sous-utilisées
- **Planification capacité** : Besoins d'expansion/réduction
- **Qualité de service** : Taux de satisfaction potentiel


## 📊 Métriques Clés et Leur Signification

### **Opérationnelles (Temps Réel)**
- `Disponibilité immédiate` → Peut-on trouver un vélo maintenant ?
- `Mix électrique/mécanique` → Quel choix pour l'usager ?
- `Taux d'occupation` → Le système est-il saturé ?

### **Stratégiques (Historique)**
- `Pic horaire` → Quand renforcer le service ?
- `Variation journalière` → Stabilité du système
- `Ratio typologique` → Adéquation offre/demande

### **Territoriales (Spatial)**
- `Couverture géographique` → Équité d'accès
- `Points chauds/froids` → Optimisation des ressources
- `Densité par arrondissement` → Planification urbaine




