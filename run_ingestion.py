import argparse

from src.ingestion import run_ingestion


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta Spotify -> MongoDB")
    parser.add_argument("--mode", choices=["full", "daily"], default="full")
    parser.add_argument("--limit-queries", type=int, default=None,
                        help="Smoke test: ejecuta solo N queries")
    parser.add_argument("--min-popularity", type=int, default=None,
                        help="Umbral de popularity (default: settings)")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    args = parser.parse_args()

    result = run_ingestion(
        mode=args.mode,
        limit_queries=args.limit_queries,
        min_popularity=args.min_popularity,
        max_pages=args.max_pages,
        shard_index=args.shard_index,
        num_shards=args.num_shards,
    )

    print("Ingesta completada")
    print(f"Status: {result['status']}")
    print(f"Run ID: {result['run_id']}")
    print(f"Total de queries: {result['total_queries']} (fallidas: {result['failed_queries']})")
    print(f"Total de requests: {result['total_requests']}")
    print(f"Tracks transformados: {result['total_tracks_transformed']}")
    print(f"Filtrados por popularidad: {result['total_filtered_by_popularity']}")
    print(f"Upserts ejecutados: {result['total_upserts']}")
    print(f"Popularity stats: {result['popularity_stats']}")


if __name__ == "__main__":
    main()
