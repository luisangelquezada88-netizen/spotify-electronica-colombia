from src.mongo import get_collection


collection = get_collection("curated_tracks")
result = collection.delete_many({})

print(f"Documentos eliminados de curated_tracks: {result.deleted_count}")