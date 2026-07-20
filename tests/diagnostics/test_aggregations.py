from src.mongo import get_collection


collection = get_collection("curated_tracks")

print("Top queries:")
query_pipeline = [
    {"$group": {"_id": "$search_query", "count": {"$sum": 1}}},
    {"$sort": {"count": -1, "_id": 1}},
    {"$limit": 10},
]

for doc in collection.aggregate(query_pipeline):
    print(f"{doc['_id']}: {doc['count']}")

print("\nTop artists:")
artist_pipeline = [
    {"$unwind": "$artist_names"},
    {"$group": {"_id": "$artist_names", "count": {"$sum": 1}}},
    {"$sort": {"count": -1, "_id": 1}},
    {"$limit": 15},
]

for doc in collection.aggregate(artist_pipeline):
    print(f"{doc['_id']}: {doc['count']}")