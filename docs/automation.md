# Automatización de la ingesta (GitHub Actions, costo $0)

## Qué corre y cuándo

Un solo workflow `.github/workflows/ingestion.yml`:

- **Cron diario `0 5 * * *` (UTC).** El job `decide` elige modo:
  - Lunes → `full` (matriz completa, 4 shards paralelos).
  - Martes–domingo → `daily` (solo `recent_years` de `config/settings.yaml`, 1 job).
- **`workflow_dispatch`** para corrida manual con inputs: `mode`, `min_popularity`, `limit_queries`.

Estimación: daily ~10–20 min, full ~2–4 h en 4 shards. Consumo mensual ~300–500 min,
muy por debajo de los 2.000 min free (privado) o ilimitado (público).

## Aviso cuenta Free + repo privado

En cuentas Free, `schedule` **no dispara en repositorios privados** (solo público o Pro).
Opciones:

1. Repo **público** (recomendado: es proyecto de portafolio).
2. Servicio externo (p. ej. cron-job.org) que llame `POST /repos/<owner>/<repo>/actions/workflows/ingestion.yml/dispatches`
   con un PAT y `{"ref":"main","inputs":{"mode":"daily"}}`.

## Secretos (Settings → Secrets → Actions)

| Secreto | Origen |
|---|---|
| `SPOTIFY_CLIENT_ID` | Spotify Dashboard |
| `SPOTIFY_CLIENT_SECRET` | Spotify Dashboard |
| `MONGO_URI` | Atlas M0 (`mongodb+srv://...`) |
| `MONGO_DB_NAME` | `spotify_electronica_colombia` |

Rotación: regenerar en Spotify/Atlas y actualizar aquí. Nunca en código.

## Smoke test antes del full

Actions → Ingestion pipeline → Run workflow → `limit_queries: 2`, `mode: daily`.
Verifica en logs: `popularity stats` (min/max/avg/nulos) y `Status: completed`.

## Sharding

`--shard-index i --num-shards 4` reparte queries por módulo (`queries[i::4]`).
Cada shard escribe su propio doc en `ingestion_runs` con `shard_index/num_shards`.
El índice único en `spotify_track_id` evita duplicados entre shards.
`build_analysis.py` corre solo en shard 0 para no duplicar el rebuild.
