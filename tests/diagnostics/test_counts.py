from src.mongo import get_collection


collections = ["raw_search_results", "curated_tracks", "ingestion_runs"]

for name in collections:
    collection = get_collection(name)
    count = collection.count_documents({})
    print(f"{name}: {count}")