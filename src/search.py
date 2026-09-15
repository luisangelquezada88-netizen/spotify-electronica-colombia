import time

import requests

from src.auth import get_spotify_access_token, invalidate_token_cache
from src.config import get_project_config
from src.logger import get_logger


logger = get_logger(__name__)


class SpotifySearchError(Exception):
    pass


def _sleep_for_retry(attempt: int, response: requests.Response | None) -> None:
    """Espera Retry-After si Spotify lo envía; si no, backoff exponencial."""
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                delay = max(1, int(retry_after))
                logger.warning("Rate limit (429). Esperando %s s (Retry-After)", delay)
                time.sleep(delay)
                return
            except ValueError:
                pass
    delay = min(2 ** attempt, 60)
    logger.warning("Reintentando en %s s (intento %s)", delay, attempt + 1)
    time.sleep(delay)


def search_tracks(
    query: str,
    limit: int = 10,
    offset: int = 0,
    max_retries: int = 5,
) -> dict:
    config = get_project_config()
    search_url = config["settings"]["spotify"]["search_url"]

    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        access_token = get_spotify_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "q": query,
            "type": "track",
            "limit": limit,
            "offset": offset,
            "market": "CO",
        }

        logger.info(
            "Realizando búsqueda en Spotify: %s | offset=%s | limit=%s",
            query, offset, limit,
        )

        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=30)
        except requests.RequestException as error:
            last_error = SpotifySearchError(f"Error de red en búsqueda Spotify: {error}")
            logger.error("Error de red (intento %s/%s): %s", attempt + 1, max_retries + 1, error)
            if attempt < max_retries:
                _sleep_for_retry(attempt, None)
                continue
            raise last_error from error

        if response.status_code == 200:
            logger.info("Búsqueda completada correctamente")
            return response.json()

        if response.status_code == 401 and attempt == 0:
            # Token expirado o revocado: limpiar cache y reintentar una vez.
            logger.warning("401 Unauthorized: refrescando token y reintentando")
            invalidate_token_cache()
            continue

        if response.status_code in (429, 500, 502, 503, 504):
            logger.warning(
                "Spotify respondió %s (intento %s/%s)",
                response.status_code, attempt + 1, max_retries + 1,
            )
            if attempt < max_retries:
                _sleep_for_retry(attempt, response)
                continue

        logger.error("Error en búsqueda: %s - %s", response.status_code, response.text[:500])
        raise SpotifySearchError(
            f"Error en búsqueda Spotify. Status code: {response.status_code}"
        )

    raise last_error or SpotifySearchError("Búsqueda fallida tras reintentos")
