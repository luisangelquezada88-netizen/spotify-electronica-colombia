import base64
import requests

from src.config import get_project_config
from src.logger import get_logger


logger = get_logger(__name__)


class SpotifyAuthError(Exception):
    pass


def get_spotify_access_token() -> str:
    config = get_project_config()

    client_id = config["spotify_client_id"]
    client_secret = config["spotify_client_secret"]
    token_url = config["spotify_token_url"]

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

    logger.info("Token obtenido correctamente")

    return access_token