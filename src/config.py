from pathlib import Path
import os
import yaml
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
SETTINGS_PATH = BASE_DIR / "config" / "settings.yaml"


load_dotenv(ENV_PATH)


def load_settings() -> dict:
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_env_variable(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def get_project_config() -> dict:
    config_data = load_settings()
    settings = config_data["settings"]

    return {
        "spotify_client_id": get_env_variable("SPOTIFY_CLIENT_ID"),
        "spotify_client_secret": get_env_variable("SPOTIFY_CLIENT_SECRET"),
        "spotify_token_url": get_env_variable(
            "SPOTIFY_TOKEN_URL",
            settings["spotify"]["token_url"]
        ),
        "spotify_search_url": get_env_variable(
            "SPOTIFY_SEARCH_URL",
            settings["spotify"]["search_url"]
        ),
        "mongo_uri": get_env_variable("MONGO_URI", "mongodb://localhost:27017"),
        "mongo_db_name": get_env_variable(
            "MONGO_DB_NAME",
            settings["mongodb"]["database"]
        ),
        "log_level": get_env_variable("LOG_LEVEL", "INFO"),
        "settings": settings,
    }