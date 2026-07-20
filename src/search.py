import requests

from src.auth import get_spotify_access_token
from src.config import get_project_config
from src.logger import get_logger


logger = get_logger(__name__)


def search_tracks(query: str, limit: int = 10, offset: int = 0) -> dict:
    config = get_project_config()
    search_url = config["settings"]["spotify"]["search_url"]

    access_token = get_spotify_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    params = {
        "q": query,
        "type": "track",
        "limit": limit,
        "offset": offset,
        "market": "CO",
    }

    logger.info("Realizando búsqueda en Spotify: %s | offset=%s | limit=%s", query, offset, limit)

    response = requests.get(search_url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        logger.error("Error en búsqueda: %s - %s", response.status_code, response.text)
        raise Exception(f"Error en búsqueda Spotify. Status code: {response.status_code}")

    logger.info("Búsqueda completada correctamente")
    return response.json()