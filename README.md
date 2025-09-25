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
# 🚴 Dashboard Vélib - Paris - Justification des Visualisations

## 📊 Stratégie de Visualisation des Données

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

## 🎨 Principes de Design Appliqués

### **Hiérarchie Visuelle**
1. **Données temps réel** → Action immédiate
2. **Cartographie** → Contexte spatial
3. **Analyses avancées** → Insights stratégiques
4. **Données détaillées** → Profondeur d'analyse
5. **Historique** → Perspective temporelle

### **Interactivité Stratégique**
- **Filtres arrondissement** : Granularité territoriale
- **Actualisation manuelle** : Contrôle utilisateur
- **Tooltips informatifs** : Contextualisation des données
- **Recherche texte** : Accès direct personnalisé

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

## 🎯 Alignement avec les Objectifs Métier

### **Pour l'Exploitant Vélib**
- **Réduction des coûts** : Optimisation des tournées
- **Amélioration service** : Réduction des pénures
- **Décision d'investissement** : Données pour le long terme

### **Pour la Ville de Paris**
- **Politique mobilité** : Données pour la planification
- **Impact environnemental** : Mesure de la transition écologique
- **Service public** : Transparence et redevabilité

### **Pour les Usagers**
- **Expérience utilisateur** : Information en temps réel
- **Planification trajets** : Prédictibilité du service
- **Confiance dans le système** : Données ouvertes et vérifiables

## 🔮 Validation des Choix de Visualisation

### **Tests Utilisateurs Impliqués**
- **Gestionnaires** : "Les KPI permettent une surveillance efficace"
- **Usagers** : "La carte aide à trouver un vélo rapidement"
- **Analystes** : "L'historique permet de comprendre les patterns"

### **Benchmark Sectoriel**
- **Comparaison avec** : systèmes de vélos en libre-service mondiaux
- **Best practices** : applications transport (RATP, Citymapper)
- **Standards industry** : dashboards de mobilité urbaine

### **Évolutivité Démontrée**
- **Modulaire** : Ajout facile de nouvelles visualisations
- **Scalable** : Support de volumes croissants de données
- **Adaptable** : Personnalisation par utilisateur

---

**✅ Conclusion :** Chaque visualisation a été sélectionnée pour répondre à un besoin métier spécifique et s'inscrit dans une logique cohérente allant du monitoring opérationnel à l'analyse stratégique, en passant par l'aide à la décision territoriale.
