"""Wrapper CLI para construir la capa analítica.

Uso:
    python scripts/build_analysis.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mongo import close_mongo_client, get_collection
from src.prepare_analysis_dataset import main


if __name__ == "__main__":
    main()
    # Índice para los filtros del dashboard.
    try:
        get_collection("analysis_tracks").create_index("popularity")
        get_collection("analysis_tracks").create_index("release_year")
    except Exception as error:
        print(f"Aviso: no se pudieron crear índices en analysis_tracks: {error}")
    close_mongo_client()
