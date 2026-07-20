from pymongo import MongoClient
from pymongo.errors import PyMongoError

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


def insert_many_documents(collection_name: str, documents: list[dict]):
    collection = get_collection(collection_name)
    result = collection.insert_many(documents)
    logger.info("Se insertaron %s documentos en %s", len(result.inserted_ids), collection_name)
    return result.inserted_ids


def upsert_document(collection_name: str, filter_query: dict, document: dict):
    collection = get_collection(collection_name)
    result = collection.replace_one(filter_query, document, upsert=True)

    if result.upserted_id is not None:
        logger.info(
            "Documento insertado por upsert en %s con _id=%s",
            collection_name,
            result.upserted_id
        )
    else:
        logger.info(
            "Documento actualizado por upsert en %s. Matched=%s Modified=%s",
            collection_name,
            result.matched_count,
            result.modified_count
        )

    return result


def upsert_many_tracks(collection_name: str, documents: list[dict], unique_field: str = "spotify_track_id"):
    results = []

    for document in documents:
        unique_value = document.get(unique_field)

        if not unique_value:
            logger.warning("Documento omitido por no tener %s", unique_field)
            continue

        result = upsert_document(
            collection_name=collection_name,
            filter_query={unique_field: unique_value},
            document=document
        )
        results.append(result)

    logger.info("Proceso de upsert completado en %s para %s documentos", collection_name, len(results))
    return results


def test_mongo_connection() -> bool:
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        logger.info("Conexión a MongoDB verificada correctamente")
        return True
    except PyMongoError as error:
        logger.error("Error conectando a MongoDB: %s", error)
        return False