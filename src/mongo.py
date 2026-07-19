from pymongo import MongoClient

from src.config import get_project_config
from src.logger import get_logger


logger = get_logger(__name__)


def get_mongo_client() -> MongoClient:
    config = get_project_config()
    mongo_uri = config["mongo_uri"]

    logger.info("Conectando a MongoDB")
    return MongoClient(mongo_uri)


def get_database():
    config = get_project_config()
    client = get_mongo_client()
    db_name = config["mongo_db_name"]

    logger.info("Usando base de datos: %s", db_name)
    return client[db_name]


def get_collection(collection_name: str):
    db = get_database()
    logger.info("Accediendo a colección: %s", collection_name)
    return db[collection_name]


def insert_one_document(collection_name: str, document: dict):
    collection = get_collection(collection_name)
    result = collection.insert_one(document)
    logger.info("Documento insertado en %s con _id=%s", collection_name, result.inserted_id)
    return result.inserted_id