import requests
import sqlite3
import os
import json
from datetime import datetime

def get_db_connection(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def fetch_velib_data():
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
    params = {'limit': 100}  # Récupérer 100 stations
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return []

def transform_velib_data(raw_data):
    """Transforme les données brutes de l'API pour la base de données"""
    transformed = []
    
    for station in raw_data:
        # Gérer les valeurs booléennes (convertir "OUI"/"NON" en 1/0)
        is_installed = 1 if station.get('is_installed') == 'OUI' else 0
        is_renting = 1 if station.get('is_renting') == 'OUI' else 0
        is_returning = 1 if station.get('is_returning') == 'OUI' else 0
        
        transformed.append({
            'station_id': station.get('stationcode', ''),
            'name': station.get('name', ''),
            'capacity': station.get('capacity', 0),
            'ebikes': station.get('ebike', 0),  # Note: 'ebike' pas 'ebikes'
            'mechanical_bikes': station.get('mechanical', 0),  # Note: 'mechanical' pas 'mechanical_bikes'
            'docks_available': station.get('numdocksavailable', 0),
            'bikes_available': station.get('numbikesavailable', 0),
            'coordonnees_geo': json.dumps(station.get('coordonnees_geo', {})),  # Convertir en JSON
            'nom_arrondissement_communes': station.get('nom_arrondissement_communes', ''),
            'is_installed': is_installed,
            'is_renting': is_renting,
            'is_returning': is_returning,
            'duedate': station.get('duedate', ''),
            'timestamp': datetime.now().isoformat()
        })
    
    return transformed

def init_database():
    """Initialise la structure de la base de données"""
    db_path = os.getenv('DB_PATH', './db/data/velib.db')
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Table des stations (informations fixes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            capacity INTEGER,
            nom_arrondissement_communes TEXT,
            coordonnees_geo TEXT,
            code_insee_commune TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des disponibilités (données temps-réel)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT NOT NULL,
            ebikes INTEGER,
            mechanical_bikes INTEGER,
            docks_available INTEGER,
            bikes_available INTEGER,
            is_installed BOOLEAN,
            is_renting BOOLEAN,
            is_returning BOOLEAN,
            duedate TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (station_id) REFERENCES stations (station_id)
        )
    ''')
    
    # Index pour améliorer les performances
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_availability_station_time 
        ON availability(station_id, timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_stations_id 
        ON stations(station_id)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec la nouvelle structure")