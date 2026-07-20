from src.ingestion import run_ingestion


result = run_ingestion()

print("Ingesta completada")
print(f"Run ID: {result['run_id']}")
print(f"Total de queries: {result['total_queries']}")
print(f"Total de requests: {result['total_requests']}")
print(f"Tracks transformados: {result['total_tracks_transformed']}")
print(f"Upserts ejecutados: {result['total_upserts']}")