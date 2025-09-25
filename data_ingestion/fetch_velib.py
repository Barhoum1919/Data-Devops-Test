import time
import schedule
from .utils import fetch_velib_data, transform_velib_data, get_db_connection, init_database
import os
from datetime import datetime

DB_PATH = os.getenv('DB_PATH', './db/data/velib.db')
UPDATE_INTERVAL = 300  # 5 minutes en secondes

def clear_old_data(conn):
    """Supprime les données de disponibilité précédentes"""
    cursor = conn.cursor()
    
    # Option 1: Supprimer toutes les données de disponibilité
    cursor.execute("DELETE FROM availability WHERE timestamp < datetime('now', '-1 day')")
    
 
    
    conn.commit()

def update_stations_data(conn, stations_data):
    """Met à jour les informations des stations (données fixes)"""
    cursor = conn.cursor()
    
    for station in stations_data:
        cursor.execute('''
            INSERT OR REPLACE INTO stations 
            (station_id, name, capacity, nom_arrondissement_communes, coordonnees_geo)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            station['station_id'],
            station['name'],
            station['capacity'],
            station['nom_arrondissement_communes'],
            station['coordonnees_geo']
        ))
    
    conn.commit()

def update_availability_data(conn, stations_data):
    """Met à jour les disponibilités avec un timestamp précis"""
    cursor = conn.cursor()
    
    # Timestamp UNIQUE pour cette mise à jour
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
    # SUPPRIMER les anciennes données avant d'insérer les nouvelles
    cursor.execute("DELETE FROM availability")
    
    for station in stations_data:
        cursor.execute('''
            INSERT INTO availability 
            (station_id, ebikes, mechanical_bikes, docks_available, bikes_available,
             is_installed, is_renting, is_returning, duedate, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            station['station_id'],
            station['ebikes'],
            station['mechanical_bikes'],
            station['docks_available'],
            station['bikes_available'],
            station['is_installed'],
            station['is_renting'],
            station['is_returning'],
            station['duedate'],
            current_timestamp  # MÊME timestamp pour TOUTES les stations de cette mise à jour
        ))
    
    conn.commit()
    print(f"🕒 Timestamp de la mise à jour: {current_timestamp}")

def fetch_and_store_data():
    """Tâche principale de récupération et stockage des données"""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 🔄 Mise à jour des données Vélib...")
    
    try:
        # Récupération des données
        raw_data = fetch_velib_data()
        
        if not raw_data:
            print("❌ Aucune donnée récupérée de l'API")
            return
        
        print(f"📊 {len(raw_data)} stations récupérées de l'API")
        
        # Transformation des données
        transformed_data = transform_velib_data(raw_data)
        
        # Connexion à la base
        conn = get_db_connection(DB_PATH)
        
        # Mise à jour des données (REMPLACEMENT, pas d'addition)
        update_stations_data(conn, transformed_data)  # Stations fixes (remplace si existe)
        update_availability_data(conn, transformed_data)  # Disponibilités (vide puis ajoute)
        
        conn.close()
        
        print(f"✅ Données mises à jour: {len(transformed_data)} stations")
        print(f"   - Vélos électriques: {sum(s['ebikes'] for s in transformed_data)}")
        print(f"   - Vélos mécaniques: {sum(s['mechanical_bikes'] for s in transformed_data)}")
        print(f"   - Places disponibles: {sum(s['docks_available'] for s in transformed_data)}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

def main():
    """Fonction principale"""
    print("🚀 Démarrage du service d'ingestion Vélib...")
    print(f"📁 Base de données: {DB_PATH}")
    
    # Initialisation de la base
    init_database()
    
    # Premier fetch immédiat
    fetch_and_store_data()
    
    # Planification des mises à jour régulières
    schedule.every(5).minutes.do(fetch_and_store_data)
    
    print(f"⏰ Service planifié - mise à jour toutes les 5 minutes")
    print("🔍 Logs de mise à jour ci-dessous...")
    print("-" * 50)
    
    # Boucle principale
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()