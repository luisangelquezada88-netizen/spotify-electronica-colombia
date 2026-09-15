"""Backfill de `popularity` sin re-scrapear todo.

Para docs en curated_tracks con popularity None/ausente, re-hidrata vía
GET /v1/tracks?ids=<hasta 50 IDs> (mucho más barato que repetir searches).

Uso:
    python scripts/backfill_popularity.py --dry-run
    python scripts/backfill_popularity.py --max-batches 20
"""
import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.auth import get_spotify_access_token
from src.config import get_project_config
from src.logger import get_logger
from src.mongo import close_mongo_client, get_collection

logger = get_logger(__name__)
TRACKS_URL = "https://api.spotify.com/v1/tracks"


def fetch_popularities(ids: list[str]) -> dict[str, int | None]:
    token = get_spotify_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        TRACKS_URL, headers=headers, params={"ids": ",".join(ids), "market": "CO"}, timeout=30
    )
    if response.status_code != 200:
        logger.error("Error hidratando tracks: %s - %s", response.status_code, response.text[:500])
        return {}
    result = {}
    for track in (response.json().get("tracks") or []):
        if track and track.get("id"):
            result[track["id"]] = track.get("popularity")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill de popularity en curated_tracks")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--max-batches", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    collection = get_collection("curated_tracks")
    cursor = collection.find(
        {"$or": [{"popularity": None}, {"popularity": {"$exists": False}}]},
        {"spotify_track_id": 1},
    )
    ids = [d["spotify_track_id"] for d in cursor if d.get("spotify_track_id")]
    logger.info("Docs sin popularity: %s", len(ids))

    if args.dry_run:
        print(f"DRY-RUN: se hidratarían {len(ids)} docs en ~{(len(ids) + args.batch_size - 1) // args.batch_size} batches")
        close_mongo_client()
        return

    updated = 0
    batches = 0
    for i in range(0, len(ids), args.batch_size):
        if args.max_batches is not None and batches >= args.max_batches:
            break
        batch = ids[i:i + args.batch_size]
        popularities = fetch_popularities(batch)
        for track_id, pop in popularities.items():
            if pop is not None:
                collection.update_one(
                    {"spotify_track_id": track_id}, {"$set": {"popularity": pop}}
                )
                updated += 1
        batches += 1
        logger.info("Batch %s: %s/%s actualizados", batches, updated, len(ids))
        time.sleep(1)

    print(f"Backfill completo: {updated} docs actualizados de {len(ids)}")
    close_mongo_client()


if __name__ == "__main__":
    main()
