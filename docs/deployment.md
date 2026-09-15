# Despliegue gratuito (Atlas M0 + Streamlit Cloud + GitHub Actions)

Costo total: **$0**. Los tres son free-forever verificados en 2026.

## 1. MongoDB Atlas M0 (datos)

1. Crea cuenta en Atlas → proyecto → cluster **M0 Free** (512 MB, 1 por proyecto).
2. Database Access → usuario + password (guárdalo).
3. Network Access → `0.0.0.0/0` (los runners de GHA tienen IP dinámica).
4. Connect → copia la URI `mongodb+srv://<user>:<pass>@<cluster>/...`.
5. Ponla en `.env` local (`MONGO_URI`) y en secretos GHA/Streamlit.

Nota: Atlas pausa clusters tras 30 días sin conexiones. La ingesta diaria lo evita sola.
Si pausó: Atlas → Resume. Sin pérdida de datos.

## 2. GitHub Actions (pipeline)

Ver `docs/automation.md`. Solo añade los 4 secretos y haz un dispatch manual
con `limit_queries: 2` para validar conexión Spotify + Atlas.

## 3. Streamlit Community Cloud (dashboard, URL pública)

1. Haz push del repo a GitHub (público para schedule + app gratis ilimitada).
2. En Streamlit Cloud → New app → repo/rama → main file: `src/dashboard_app.py`.
3. App settings → Secrets:
   ```toml
   MONGO_URI = "mongodb+srv://<user>:<pass>@<cluster>/..."
   MONGO_DB_NAME = "spotify_electronica_colombia"
   ```
   (El dashboard también acepta `MONGODB_URI`/`MONGODB_DB`.)
4. Deploy → obtienes `https://<tu-app>.streamlit.app` para compartir.

Límites: ~1 GB RAM (esta app usa <100 MB), duerme tras ~7 días sin visitas
(despierta en 30–60 s), 1 app privada / ilimitadas públicas.

## 4. Docker (opcional, paridad local)

```powershell
docker build -t spotify-etl .
docker run --rm --env-file .env spotify-etl python run_ingestion.py --mode daily --limit-queries 2
```

## Rollback

- Pipeline: Actions → re-ejecuta un run verde anterior con `workflow_dispatch`.
- Datos: cada `ingestion_runs` guarda `mode`, queries y stats; el upsert es
  idempotente por `spotify_track_id`, re-correr no duplica.
- Dashboard: Streamlit Cloud → reboot o redeploy de un commit anterior.
