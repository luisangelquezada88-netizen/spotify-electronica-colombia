from src.mongo import test_mongo_connection

if test_mongo_connection():
    print("MongoDB OK")
else:
    print("MongoDB ERROR")