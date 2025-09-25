import os
import sqlite3

def init_database():
    """Initialise la structure de la base de données"""
    db_path = os.getenv('DB_PATH', './db/data/velib.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
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
    
    # Vue pour les données les plus récentes
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS latest_availability AS
        SELECT 
            s.station_id,
            s.name,
            s.capacity,
            s.nom_arrondissement_communes as arrondissement,
            s.coordonnees_geo,
            a.ebikes,
            a.mechanical_bikes,
            a.docks_available,
            a.bikes_available,
            a.is_installed,
            a.is_renting,
            a.is_returning,
            a.timestamp
        FROM stations s
        JOIN availability a ON s.station_id = a.station_id
        WHERE a.timestamp = (
            SELECT MAX(timestamp) 
            FROM availability 
            WHERE station_id = s.station_id
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Base de données initialisée: {db_path}")

if __name__ == "__main__":
    init_database()