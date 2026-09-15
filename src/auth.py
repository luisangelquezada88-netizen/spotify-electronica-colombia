import base64
import time
import requests

from src.config import get_project_config
from src.logger import get_logger


logger = get_logger(__name__)


class SpotifyAuthError(Exception):
    pass


# Token cacheado en memoria: evita pedir 1 token por request
# (una corrida full hacía 144+ tokens; ahora hace 1 por hora).
_cached_token: str | None = None
_token_expires_at: float = 0.0


def get_spotify_access_token() -> str:
    global _cached_token, _token_expires_at

    if _cached_token and time.time() < _token_expires_at - 60:
        return _cached_token

    config = get_project_config()

    client_id = config["spotify_client_id"]
    client_secret = config["spotify_client_secret"]
    token_url = config["settings"]["spotify"]["token_url"]

    if not client_id or not client_secret:
        raise SpotifyAuthError(
            "Faltan SPOTIFY_CLIENT_ID y/o SPOTIFY_CLIENT_SECRET en el archivo .env"
        )

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials"
    }

    logger.info("Solicitando access token a Spotify")

    response = requests.post(token_url, headers=headers, data=data, timeout=30)

    if response.status_code != 200:
        logger.error("Error al solicitar token: %s - %s", response.status_code, response.text)
        raise SpotifyAuthError(
            f"No fue posible obtener el token. Status code: {response.status_code}"
        )

    response_data = response.json()
    access_token = response_data.get("access_token")

    if not access_token:
        raise SpotifyAuthError("La respuesta no contiene access_token")

    expires_in = int(response_data.get("expires_in", 3600))
    _cached_token = access_token
    _token_expires_at = time.time() + expires_in

    logger.info("Token obtenido correctamente")

    return access_token


def invalidate_token_cache() -> None:
    """Limpia el token cacheado (p. ej. tras un 401)."""
    global _cached_token, _token_expires_at
    _cached_token = None
    _token_expires_at = 0.0