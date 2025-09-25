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

