from pymongo import ASCENDING, MongoClient, ReplaceOne
from pymongo.errors import BulkWriteError, PyMongoError

from src.config import get_project_config
from src.logger import get_logger


logger = get_logger(__name__)

# Cliente singleton: antes se abría un MongoClient por cada get_collection()
# (cientos por corrida). Ahora se reutiliza uno por proceso.
_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is not None:
        return _client

    config = get_project_config()
    mongo_uri = config["mongo_uri"]

    logger.info("Conectando a MongoDB")
    _client = MongoClient(mongo_uri)
    return _client


def close_mongo_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


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


def ensure_indexes(collection_name: str = "curated_tracks") -> None:
    """Crea índices idempotentes: único en spotify_track_id + popularity.

    Sin el índice único, re-corridas y shards paralelos generan duplicados.
    Sin el índice en popularity, el filtro por umbral hace COLLSCAN.
    """
    collection = get_collection(collection_name)
    collection.create_index([("spotify_track_id", ASCENDING)], unique=True)
    collection.create_index([("popularity", ASCENDING)])
    collection.create_index([("search_query", ASCENDING)])
    logger.info("Índices verificados en %s", collection_name)


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


def upsert_many_tracks(collection_name: str, documents: list[dict], unique_field: str = "spotify_track_id") -> int:
    """Upsert en bulk (1 round-trip por lote en vez de N).

    A 100 ops/s de Atlas M0, 10k docs en loop 1x1 = ~100 s solo en writes
    más overhead de conexión; en bulk son segundos. Retorna nº de writes.
    """
    valid_docs = [d for d in documents if d.get(unique_field)]
    skipped = len(documents) - len(valid_docs)
    if skipped:
        logger.warning("Documentos omitidos por no tener %s: %s", unique_field, skipped)
    if not valid_docs:
        return 0

    collection = get_collection(collection_name)
    operations = [
        ReplaceOne({unique_field: doc[unique_field]}, doc, upsert=True)
        for doc in valid_docs
    ]

    try:
        result = collection.bulk_write(operations, ordered=False)
        total = (result.upserted_count or 0) + (result.modified_count or 0) + (result.matched_count or 0)
        logger.info(
            "Bulk upsert en %s: %s ops (insertados=%s modificados=%s)",
            collection_name, len(valid_docs),
            result.upserted_count, result.modified_count,
        )
        return total
    except BulkWriteError as error:
        # Con ordered=False, parte del lote puede haber aplicado igual.
        details = error.details or {}
        n_applied = sum(
            1 for _ in (details.get("writeErrors") or [])
        )
        logger.error(
            "BulkWriteError en %s: %s errores de %s ops. Detalle: %s",
            collection_name, len(details.get("writeErrors") or []),
            len(valid_docs), str(details)[:1000],
        )
        return max(0, len(valid_docs) - n_applied)


def test_mongo_connection() -> bool:
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        logger.info("Conexión a MongoDB verificada correctamente")
        return True
    except PyMongoError as error:
        logger.error("Error conectando a MongoDB: %s", error)
        return False
