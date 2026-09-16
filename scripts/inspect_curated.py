import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mongo import close_mongo_client, get_collection


collection = get_collection("curated_tracks")
document = collection.find_one()

print(document)
close_mongo_client()