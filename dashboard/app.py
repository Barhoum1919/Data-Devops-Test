import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Vélib - Paris",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache des données avec timeout
@st.cache_data(ttl=300)  # 5 minutes
def load_data():
    """Charge les données depuis la base SQLite"""
    try:
        db_path = os.getenv('DB_PATH', './db/data/velib.db')
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Requête optimisée pour les données récentes
        query = """
        SELECT 
            s.name, 
            s.nom_arrondissement_communes as arrondissement,
            s.capacity,
            a.ebikes, 
            a.mechanical_bikes, 
            a.docks_available,
            a.timestamp,
            s.coordonnees_geo,
            (a.ebikes + a.mechanical_bikes) as total_bikes,
            CASE 
                WHEN s.capacity > 0 THEN ROUND((a.ebikes + a.mechanical_bikes) * 100.0 / s.capacity, 1)
                ELSE 0 
            END as occupancy_rate
        FROM stations s
        JOIN availability a ON s.station_id = a.station_id
        WHERE a.is_installed = 1
        ORDER BY a.timestamp DESC
        LIMIT 1000
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Traitement des coordonnées
        if not df.empty and 'coordonnees_geo' in df.columns:
            df[['lat', 'lon']] = df['coordonnees_geo'].apply(
                lambda x: pd.Series(parse_coordinates(x))
            )
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur base de données: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # 1 heure pour les données historiques
def load_historical_data(hours=24):
    """Charge les données historiques des 24 dernières heures"""
    try:
        db_path = os.getenv('DB_PATH', './db/data/velib.db')
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Calcul de la date de début (24h avant maintenant)
        start_time = datetime.now() - timedelta(hours=hours)
        
        query = f"""
        SELECT 
            s.name,
            s.nom_arrondissement_communes as arrondissement,
            a.ebikes, 
            a.mechanical_bikes,
            a.docks_available,
            a.timestamp,
            (a.ebikes + a.mechanical_bikes) as total_bikes,
            CASE 
                WHEN s.capacity > 0 THEN ROUND((a.ebikes + a.mechanical_bikes) * 100.0 / s.capacity, 1)
                ELSE 0 
            END as occupancy_rate
        FROM stations s
        JOIN availability a ON s.station_id = a.station_id
        WHERE a.is_installed = 1 
        AND a.timestamp >= '{start_time.strftime('%Y-%m-%d %H:%M:%S')}'
        ORDER BY a.timestamp
        """
        
        df_hist = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_hist.empty:
            # Conversion du timestamp et extraction de l'heure
            df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
            df_hist['heure'] = df_hist['timestamp'].dt.floor('H')  # Agrégation par heure
            
        return df_hist
        
    except Exception as e:
        st.error(f"❌ Erreur données historiques: {e}")
        return pd.DataFrame()

def parse_coordinates(coord_str):
    """Parse les coordonnées géographiques"""
    if not coord_str:
        return None, None
    try:
        coords = json.loads(coord_str)
        return coords.get('lat'), coords.get('lon')
    except:
        return None, None

def create_historical_analysis(df_hist, selected_arrondissement):
    """Crée les visualisations historiques"""
    if df_hist.empty:
        st.info("📊 Données historiques insuffisantes pour l'analyse temporelle")
        return
    
    # Filtrage par arrondissement si sélectionné
    if selected_arrondissement != 'Tous':
        df_hist = df_hist[df_hist['arrondissement'] == selected_arrondissement]
    
    if df_hist.empty:
        st.info("📊 Aucune donnée historique pour cet arrondissement")
        return
    
    # Agrégation par heure
    hourly_data = df_hist.groupby('heure').agg({
        'total_bikes': 'mean',
        'ebikes': 'mean',
        'mechanical_bikes': 'mean',
        'docks_available': 'mean',
        'occupancy_rate': 'mean'
    }).reset_index()
    
    hourly_data['heure_str'] = hourly_data['heure'].dt.strftime('%H:%M')
    
    # Graphique 1: Évolution globale sur 24h
    fig_evolution = go.Figure()
    
    fig_evolution.add_trace(go.Scatter(
        x=hourly_data['heure_str'],
        y=hourly_data['total_bikes'],
        mode='lines+markers',
        name='Vélos disponibles',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    fig_evolution.add_trace(go.Scatter(
        x=hourly_data['heure_str'],
        y=hourly_data['docks_available'],
        mode='lines+markers',
        name='Places libres',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=6)
    ))
    
    fig_evolution.update_layout(
        title='🕐 Évolution de la disponibilité sur 24h',
        xaxis_title='Heure',
        yaxis_title='Nombre moyen',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Graphique 2: Comparaison vélos électriques vs mécaniques
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bike_types = go.Figure()
        
        fig_bike_types.add_trace(go.Scatter(
            x=hourly_data['heure_str'],
            y=hourly_data['ebikes'],
            mode='lines+markers',
            name='🔌 Vélos électriques',
            line=dict(color='#2ca02c', width=3)
        ))
        
        fig_bike_types.add_trace(go.Scatter(
            x=hourly_data['heure_str'],
            y=hourly_data['mechanical_bikes'],
            mode='lines+markers',
            name='⚙️ Vélos mécaniques',
            line=dict(color='#d62728', width=3)
        ))
        
        fig_bike_types.update_layout(
            title='📊 Répartition par type de vélo',
            xaxis_title='Heure',
            yaxis_title='Nombre moyen',
            height=350
        )
        
        st.plotly_chart(fig_bike_types, use_container_width=True)
    
    with col2:
        # Graphique 3: Taux d'occupation
        fig_occupancy = go.Figure()
        
        fig_occupancy.add_trace(go.Scatter(
            x=hourly_data['heure_str'],
            y=hourly_data['occupancy_rate'],
            mode='lines+markers',
            name='Taux d\'occupation',
            line=dict(color='#9467bd', width=3),
            fill='tozeroy'
        ))
        
        fig_occupancy.update_layout(
            title='📈 Taux d\'occupation moyen',
            xaxis_title='Heure',
            yaxis_title='Taux d\'occupation (%)',
            yaxis=dict(range=[0, 100]),
            height=350
        )
        
        st.plotly_chart(fig_occupancy, use_container_width=True)
    
    # Métriques résumées
    st.subheader("📋 Statistiques sur 24h")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        peak_hour = hourly_data.loc[hourly_data['total_bikes'].idxmax(), 'heure_str']
        st.metric("🕐 Heure de pic", peak_hour)
    
    with col2:
        avg_bikes = hourly_data['total_bikes'].mean()
        st.metric("🚴 Moyenne vélos/h", f"{avg_bikes:.0f}")
    
    with col3:
        variation = ((hourly_data['total_bikes'].iloc[-1] - hourly_data['total_bikes'].iloc[0]) / 
                    hourly_data['total_bikes'].iloc[0] * 100)
        st.metric("📈 Variation 24h", f"{variation:+.1f}%")
    
    with col4:
        avg_occupancy = hourly_data['occupancy_rate'].mean()
        st.metric("🏪 Occupation moyenne", f"{avg_occupancy:.1f}%")

def main():
    # Header principal
    st.title("🚴 Dashboard Vélib - Paris")
    st.markdown("### Surveillance en temps réel et analyse historique des stations Vélib")
    
    # Sidebar - Contrôles
    with st.sidebar:
        st.title("🎛️ Contrôles")
        
        # Actualisation manuelle
        if st.button("🔄 Actualiser maintenant", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # Filtres
        st.subheader("🔧 Filtres")
    
    # Chargement des données
    with st.spinner("📊 Chargement des données..."):
        df = load_data()
        df_hist = load_historical_data(24)  # 24 heures d'historique
    
    # Gestion des données manquantes
    if df.empty:
        st.error("""
        ❌ Aucune donnée disponible
        
        **Solutions possibles :**
        - Vérifiez que le service d'ingestion est en cours d'exécution
        - Attendez 2-3 minutes après le démarrage
        - Vérifiez que la base de données existe
        """)
        
        if st.button("🔄 Réessayer le chargement"):
            st.cache_data.clear()
            st.rerun()
        return
    
    # Filtre par arrondissement
    arrondissements = ['Tous'] + sorted(df['arrondissement'].dropna().unique().tolist())
    selected_arrondissement = st.sidebar.selectbox(
        "🏘️ Arrondissement", 
        arrondissements,
        help="Filtrer par arrondissement"
    )
    
    # Application du filtre
    if selected_arrondissement != 'Tous':
        df_filtered = df[df['arrondissement'] == selected_arrondissement]
    else:
        df_filtered = df.copy()
    
    # ===== SECTION 1: KPI PRINCIPAUX =====
    st.header("📊 Tableau de bord en temps réel")
    
    # KPI en grille responsive
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        total_stations = len(df_filtered)
        st.metric(
            "Stations Actives", 
            f"{total_stations:,}",
            help="Nombre total de stations avec données"
        )
    
    with kpi2:
        total_ebikes = int(df_filtered['ebikes'].sum())
        st.metric(
            "🔌 Vélos Électriques", 
            f"{total_ebikes:,}",
            delta=f"+{int(df_filtered['ebikes'].mean())} moyenne/stations" if total_ebikes > 0 else None
        )
    
    with kpi3:
        total_mechanical = int(df_filtered['mechanical_bikes'].sum())
        st.metric(
            "⚙️ Vélos Mécaniques", 
            f"{total_mechanical:,}",
            delta=f"+{int(df_filtered['mechanical_bikes'].mean())} moyenne/stations" if total_mechanical > 0 else None
        )
    
    with kpi4:
        total_docks = int(df_filtered['docks_available'].sum())
        st.metric(
            "🅿️ Places Libres", 
            f"{total_docks:,}",
            help="Places de stationnement disponibles"
        )
    
    # KPI secondaires
    kpi5, kpi6 = st.columns(2)
    
    with kpi5:
        avg_occupancy = df_filtered['occupancy_rate'].mean()
        st.metric(
            "📈 Taux d'Occupation Moyen", 
            f"{avg_occupancy:.1f}%",
            delta=f"{avg_occupancy - df['occupancy_rate'].mean():+.1f}% vs global" if selected_arrondissement != 'Tous' else None
        )
    
    with kpi6:
        total_capacity = df_filtered['capacity'].sum()
        utilization_rate = (df_filtered['total_bikes'].sum() / total_capacity * 100) if total_capacity > 0 else 0
        st.metric(
            "🎯 Taux d'Utilisation", 
            f"{utilization_rate:.1f}%",
            help="Pourcentage de vélos disponibles par rapport à la capacité totale"
        )
    
    # ===== SECTION 2: CARTE INTERACTIVE =====
    st.header("🗺️ Carte des stations")
    
    if 'lat' in df_filtered.columns and 'lon' in df_filtered.columns:
        map_data = df_filtered[['lat', 'lon', 'name', 'ebikes', 'mechanical_bikes', 'docks_available']].dropna()
        
        if not map_data.empty:
            # Préparation des données pour la carte
            map_data['total_bikes'] = map_data['ebikes'] + map_data['mechanical_bikes']
            map_data['size'] = map_data['total_bikes'].apply(lambda x: min(max(x * 2, 5), 30))
            map_data['station_info'] = map_data.apply(
                lambda row: f"{row['name']}<br>🔌 {row['ebikes']} électriques<br>⚙️ {row['mechanical_bikes']} mécaniques<br>🅿️ {row['docks_available']} places",
                axis=1
            )
            
            # Création de la carte
            fig = px.scatter_mapbox(
                map_data,
                lat="lat",
                lon="lon",
                size="size",
                color="ebikes",
                hover_name="name",
                hover_data={"ebikes": True, "mechanical_bikes": True, "docks_available": True},
                color_continuous_scale="viridis",
                size_max=20,
                zoom=11,
                height=500,
                title="Localisation des stations Vélib"
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 40, "l": 0, "b": 0},
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Aucune donnée de localisation disponible")
    else:
        st.info("🗺️ Les données de localisation ne sont pas disponibles")
    
    # ===== SECTION 3: ANALYSES AVANCÉES =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📊 Répartition par type de vélo")
        
        # Graphique en camembert
        bike_types = ['Vélos Électriques', 'Vélos Mécaniques']
        bike_counts = [df_filtered['ebikes'].sum(), df_filtered['mechanical_bikes'].sum()]
        
        if sum(bike_counts) > 0:
            fig_pie = px.pie(
                values=bike_counts,
                names=bike_types,
                title="Répartition des vélos disponibles",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("📊 Aucun vélo disponible pour l'analyse")
    
    with col2:
        st.header("🏆 Top 10 des stations")
        
        # Stations avec le plus de vélos
        top_stations = df_filtered.nlargest(10, 'total_bikes')[['name', 'arrondissement', 'total_bikes', 'ebikes', 'mechanical_bikes']]
        
        if not top_stations.empty:
            fig_bar = px.bar(
                top_stations,
                x='total_bikes',
                y='name',
                orientation='h',
                title="Stations avec le plus de vélos disponibles",
                labels={'total_bikes': 'Nombre total de vélos', 'name': 'Station'},
                color='total_bikes',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("🏆 Données insuffisantes pour le classement")
    
    # ===== SECTION 4: DONNÉES DÉTAILLÉES =====
    st.header("📋 Données détaillées par station")
    
    # Options d'affichage
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Rechercher une station", placeholder="Nom de la station...")
    
    with col2:
        rows_to_show = st.selectbox("Lignes à afficher", [10, 25, 50, 100], index=0)
    
    # Filtrage par recherche
    if search_term:
        display_data = df_filtered[df_filtered['name'].str.contains(search_term, case=False, na=False)]
    else:
        display_data = df_filtered
    
    # Colonnes à afficher
    display_columns = ['name', 'arrondissement', 'ebikes', 'mechanical_bikes', 'total_bikes', 'docks_available', 'occupancy_rate']
    available_columns = [col for col in display_columns if col in display_data.columns]
    
    # Affichage du tableau
    if not display_data.empty:
        st.dataframe(
            display_data[available_columns].head(rows_to_show),
            use_container_width=True,
            height=400
        )
        
        # Statistiques du tableau
        st.caption(f"📊 Affichage de {min(len(display_data), rows_to_show)} stations sur {len(display_data)} totales")
    else:
        st.info("🔍 Aucune station ne correspond à votre recherche")
    
    # ===== SECTION 5: ANALYSE HISTORIQUE 24H (MAINTENANT EN BAS) =====
    st.header("🕐 Analyse historique sur 24 heures")
    create_historical_analysis(df_hist, selected_arrondissement)
    
    # ===== SECTION 6: INFORMATIONS TECHNIQUES =====
    with st.expander("ℹ️ Informations techniques"):
        st.write(f"**Dernière mise à jour:** {datetime.now().strftime('%H:%M:%S')}")
        st.write(f"**Nombre total de stations:** {len(df)}")
        st.write(f"**Arrondissement sélectionné:** {selected_arrondissement}")
        st.write(f"**Données chargées:** {len(df_filtered)} stations")
        
        if 'timestamp' in df.columns and not df.empty:
            latest_timestamp = pd.to_datetime(df['timestamp']).max()
            st.write(f"**Dernière actualisation des données:** {latest_timestamp}")
        
        if not df_hist.empty:
            hist_start = df_hist['timestamp'].min()
            hist_end = df_hist['timestamp'].max()
            st.write(f"**Période historique:** {hist_start.strftime('%d/%m %H:%M')} - {hist_end.strftime('%d/%m %H:%M')}")
            st.write(f"**Points de données historiques:** {len(df_hist)}")
    
    # Actualisation automatique silencieuse
    if st.button("🔄", key="auto_refresh", help="Actualiser automatiquement"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()