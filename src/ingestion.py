from datetime import datetime, UTC
import time

from src.config import get_project_config
from src.logger import get_logger
from src.search import search_tracks, SpotifySearchError
from src.transform import transform_search_results
from src.mongo import (
    close_mongo_client,
    ensure_indexes,
    insert_one_document,
    upsert_many_tracks,
)


logger = get_logger(__name__)


def build_queries(mode: str = "full") -> list[str]:
    """Construye queries término × año.

    - full: toda la matriz (barrido semanal para escalar a 200k-500k).
    - daily: solo años recientes (refresh diario barato).
    """
    config = get_project_config()
    settings = config["settings"]

    query_terms = settings["spotify"]["query_terms"]
    start_year = settings["project"]["start_year"]
    end_year = settings["project"]["end_year"]

    if mode == "daily":
        recent_years = int(settings["project"].get("recent_years", 3))
        start_year = max(start_year, end_year - recent_years + 1)

    queries = []
    for term in query_terms:
        for year in range(start_year, end_year + 1):
            queries.append(f"{term} year:{year}")

    return queries


def build_offsets(limit: int, max_pages: int) -> list[int]:
    return [page * limit for page in range(max_pages)]


def _popularity_stats(documents: list[dict]) -> dict:
    values = [d.get("popularity") for d in documents]
    present = [v for v in values if isinstance(v, (int, float))]
    nulls = len(values) - len(present)
    if not present:
        return {"min": None, "max": None, "avg": None, "null_count": nulls, "total": len(values)}
    return {
        "min": min(present),
        "max": max(present),
        "avg": round(sum(present) / len(present), 2),
        "null_count": nulls,
        "total": len(values),
    }


def run_ingestion(
    mode: str = "full",
    limit_queries: int | None = None,
    min_popularity: int | None = None,
    max_pages: int | None = None,
    shard_index: int = 0,
    num_shards: int = 1,
) -> dict:
    """Ejecuta la ingesta. Una query fallida no aborta la corrida.

    - mode: "full" (matriz completa) o "daily" (años recientes).
    - limit_queries: smoke test (p. ej. 2 queries).
    - min_popularity: filtra tracks bajo el umbral (default: settings).
    - shard_index/num_shards: reparte queries entre jobs GHA paralelos.
    """
    config = get_project_config()
    settings = config["settings"]

    limit = settings["spotify"]["limit"]
    sleep_seconds = settings["spotify"]["sleep_seconds"]
    effective_max_pages = max_pages or settings["spotify"]["max_pages"]
    if min_popularity is None:
        min_popularity = int(settings["project"].get("min_popularity", 0))

    queries = build_queries(mode=mode)
    if num_shards > 1:
        queries = [q for i, q in enumerate(queries) if i % num_shards == shard_index]
    if limit_queries:
        queries = queries[:limit_queries]
    offsets = build_offsets(limit, effective_max_pages)

    ensure_indexes("curated_tracks")

    run_started_at = datetime.now(UTC).isoformat()

    total_queries = 0
    total_requests = 0
    total_tracks_transformed = 0
    total_filtered_by_popularity = 0
    total_upserts = 0
    failed_queries = 0
    query_summaries = []
    errors = []
    all_popularities: list = []

    logger.info("Iniciando proceso de ingesta (mode=%s, min_popularity=%s)", mode, min_popularity)
    logger.info("Total de queries a ejecutar: %s", len(queries))
    logger.info("Offsets por query: %s", offsets)

    try:
        for query in queries:
            logger.info("Ejecutando query base: %s", query)

            query_tracks_transformed = 0
            query_upserts = 0
            query_requests = 0

            for offset in offsets:
                logger.info("Ejecutando query paginada: %s | offset=%s", query, offset)

                try:
                    search_result = search_tracks(query, limit=limit, offset=offset)
                except SpotifySearchError as error:
                    logger.error("Query fallida %s offset=%s: %s", query, offset, error)
                    errors.append({"query": query, "offset": offset, "error": str(error)})
                    continue

                curated_documents = transform_search_results(search_result, query)
                all_popularities.extend([d.get("popularity") for d in curated_documents])

                if min_popularity > 0:
                    before = len(curated_documents)
                    curated_documents = [
                        d for d in curated_documents
                        if isinstance(d.get("popularity"), (int, float))
                        and d["popularity"] >= min_popularity
                    ]
                    total_filtered_by_popularity += before - len(curated_documents)

                try:
                    upserted = upsert_many_tracks("curated_tracks", curated_documents)
                except Exception as error:
                    logger.error("Upsert fallido %s offset=%s: %s", query, offset, error)
                    errors.append({"query": query, "offset": offset, "error": f"upsert: {error}"})
                    continue

                query_requests += 1
                total_requests += 1

                query_tracks_transformed += len(curated_documents)
                total_tracks_transformed += len(curated_documents)
                query_upserts += upserted
                total_upserts += upserted

                time.sleep(sleep_seconds)

            query_summary = {
                "query": query,
                "requests_executed": query_requests,
                "tracks_found": query_tracks_transformed,
                "upserts_executed": query_upserts,
            }
            query_summaries.append(query_summary)
            total_queries += 1
            if query_requests == 0:
                failed_queries += 1
    finally:
        close_mongo_client()

    present = [v for v in all_popularities if isinstance(v, (int, float))]
    popularity_stats = {
        "min": min(present) if present else None,
        "max": max(present) if present else None,
        "avg": round(sum(present) / len(present), 2) if present else None,
        "null_count": len(all_popularities) - len(present),
        "total_sampled": len(all_popularities),
    }
    logger.info(
        "Popularity stats: min=%s max=%s avg=%s nulos=%s/%s",
        popularity_stats["min"], popularity_stats["max"], popularity_stats["avg"],
        popularity_stats["null_count"], popularity_stats["total_sampled"],
    )

    status = "completed" if not errors else "completed_with_errors"
    run_finished_at = datetime.now(UTC).isoformat()

    run_document = {
        "run_started_at": run_started_at,
        "run_finished_at": run_finished_at,
        "mode": mode,
        "min_popularity": min_popularity,
        "shard_index": shard_index,
        "num_shards": num_shards,
        "total_queries": total_queries,
        "failed_queries": failed_queries,
        "total_requests": total_requests,
        "total_tracks_transformed": total_tracks_transformed,
        "total_filtered_by_popularity": total_filtered_by_popularity,
        "total_upserts": total_upserts,
        "popularity_stats": popularity_stats,
        "query_summaries": query_summaries,
        "errors": errors[:50],
        "source": "spotify_web_api",
        "collection_target": "curated_tracks",
        "status": status,
    }

    inserted_id = insert_one_document("ingestion_runs", run_document)
    close_mongo_client()

    logger.info("Ingesta finalizada (%s). _id de corrida: %s", status, inserted_id)

    return {
        "run_id": str(inserted_id),
        "status": status,
        "total_queries": total_queries,
        "failed_queries": failed_queries,
        "total_requests": total_requests,
        "total_tracks_transformed": total_tracks_transformed,
        "total_filtered_by_popularity": total_filtered_by_popularity,
        "total_upserts": total_upserts,
        "popularity_stats": popularity_stats,
    }
