# Runbook / Troubleshooting

## La ingesta marca `completed_with_errors`

1. Abre el log del job → busca `Query fallida` / `Upsert fallido`.
2. El doc en `ingestion_runs` guarda `errors` (máx 50) con query/offset/error.
3. Re-ejecuta solo lo fallido: `python run_ingestion.py --mode daily` (el upsert
   es idempotente; lo ya guardado no se duplica).

## 429 Too Many Requests

El cliente respeta `Retry-After` hasta 300 s con backoff. Dos casos:

- **429 normal**: reintenta solo y sigue. Si ves varios seguidos, sube
  `sleep_seconds` en `config/settings.yaml` (p. ej. a 2).
- **429 con Retry-After gigante (>300 s, p. ej. 85000 s)**: es baneo de cuota
  de ~horas, no ventana corta. La corrida aborta sola con
  `status: quota_exhausted` guardando el progreso parcial (los upserts ya
  hechos no se pierden). No re-dispates de inmediato: espera al día siguiente
  (el cron diario lo reintenta solo) o prueba con
  `--limit-queries 1 --max-pages 2` para sondear.

La paginación para sola cuando una página trae menos items que `limit`
(no se queman requests en vacío).

## 401 Unauthorized

El token cacheado se invalida y se refresca solo una vez. Si persiste:
verifica `SPOTIFY_CLIENT_ID/SECRET` en secretos (rotaron o caducaron).

## `popularity` con muchos nulos

1. Mira `popularity_stats` del run (`min/max/avg/null_count`).
2. Si `null_count` ≈ total: tu app puede estar en Development Mode restringido.
   Corre `python scripts/backfill_popularity.py --dry-run` y luego por lotes:
   `python scripts/backfill_popularity.py --max-batches 5`.
3. Si el backfill también devuelve nulos, documenta el límite y evalúa
   pedir Extended Quota en Spotify Dashboard.

## Filtrar por popularidad

- Permanente: `min_popularity` en `config/settings.yaml`.
- Por corrida: `--min-popularity 20` o secreto/env `MIN_POPULARITY=20`.
- Los filtrados se cuentan en `total_filtered_by_popularity` del run.

## Atlas no conecta desde GHA

- Network Access debe incluir `0.0.0.0/0`.
- Verifica que `MONGO_URI` sea `mongodb+srv://...` con password con caracteres
  URL-escapados (`@` → `%40`, etc.).

## Dashboard vacío ("No hay datos en analysis_tracks")

1. Corre `python scripts/build_analysis.py` (reconstruye `analysis_tracks`).
2. Verifica `test_counts.py`: `curated_tracks` debe tener docs.
3. En Streamlit Cloud, revisa que los Secrets tengan `MONGO_URI` (o `MONGODB_URI`).

## Comandos locales útiles

```powershell
python run_ingestion.py --mode daily --limit-queries 2   # smoke test
python run_ingestion.py --mode daily --min-popularity 20 # con umbral
python scripts/backfill_popularity.py --dry-run
python tests/diagnostics/test_counts.py
```
