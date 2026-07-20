from datetime import datetime, UTC
import time

from src.config import get_project_config
from src.logger import get_logger
from src.search import search_tracks
from src.transform import transform_search_results
from src.mongo import insert_one_document, upsert_many_tracks


logger = get_logger(__name__)


def build_queries() -> list[str]:
    config = get_project_config()
    settings = config["settings"]

    query_terms = settings["spotify"]["query_terms"]
    start_year = settings["project"]["start_year"]
    end_year = settings["project"]["end_year"]

    queries = []

    for term in query_terms:
        for year in range(start_year, end_year + 1):
            queries.append(f"{term} year:{year}")

    return queries


def build_offsets(limit: int, max_pages: int) -> list[int]:
    return [page * limit for page in range(max_pages)]


def run_ingestion() -> dict:
    config = get_project_config()
    settings = config["settings"]

    limit = settings["spotify"]["limit"]
    sleep_seconds = settings["spotify"]["sleep_seconds"]
    max_pages = settings["spotify"]["max_pages"]

    queries = build_queries()
    offsets = build_offsets(limit, max_pages)

    run_started_at = datetime.now(UTC).isoformat()

    total_queries = 0
    total_requests = 0
    total_tracks_transformed = 0
    total_upserts = 0
    query_summaries = []

    logger.info("Iniciando proceso de ingesta")
    logger.info("Total de queries a ejecutar: %s", len(queries))
    logger.info("Offsets por query: %s", offsets)

    for query in queries:
        logger.info("Ejecutando query base: %s", query)

        query_tracks_transformed = 0
        query_upserts = 0
        query_requests = 0

        for offset in offsets:
            logger.info("Ejecutando query paginada: %s | offset=%s", query, offset)

            search_result = search_tracks(query, limit=limit, offset=offset)
            curated_documents = transform_search_results(search_result, query)
            upsert_results = upsert_many_tracks("curated_tracks", curated_documents)

            query_requests += 1
            total_requests += 1

            query_tracks_transformed += len(curated_documents)
            total_tracks_transformed += len(curated_documents)

            query_upserts += len(upsert_results)
            total_upserts += len(upsert_results)

            time.sleep(sleep_seconds)

        query_summary = {
            "query": query,
            "requests_executed": query_requests,
            "tracks_found": query_tracks_transformed,
            "upserts_executed": query_upserts,
        }

        query_summaries.append(query_summary)
        total_queries += 1

    run_finished_at = datetime.now(UTC).isoformat()

    run_document = {
        "run_started_at": run_started_at,
        "run_finished_at": run_finished_at,
        "total_queries": total_queries,
        "total_requests": total_requests,
        "total_tracks_transformed": total_tracks_transformed,
        "total_upserts": total_upserts,
        "query_summaries": query_summaries,
        "source": "spotify_web_api",
        "collection_target": "curated_tracks",
        "status": "completed",
    }

    inserted_id = insert_one_document("ingestion_runs", run_document)

    logger.info("Ingesta finalizada con éxito. _id de corrida: %s", inserted_id)

    return {
        "run_id": str(inserted_id),
        "total_queries": total_queries,
        "total_requests": total_requests,
        "total_tracks_transformed": total_tracks_transformed,
        "total_upserts": total_upserts,
    }