#!/usr/bin/env python3
"""
Script de lancement du dashboard Streamlit
"""
import subprocess
import sys
import os

def main():
    print("🚀 Lancement du Dashboard Vélib Streamlit...")
    print("📊 Le dashboard sera accessible sur http://localhost:8501")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    
    # Lancer Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "dashboard/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main()