# Spotify Electrónica Colombia

![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)
![Ingestion](https://github.com/<owner>/<repo>/actions/workflows/ingestion.yml/badge.svg)

Pipeline ELT end-to-end (portafolio): Spotify Web API → MongoDB → datasets analíticos → dashboard Streamlit.
Automatizado con GitHub Actions y desplegable a **costo $0** (Atlas M0 + Streamlit Community Cloud).

## Arquitectura

1. Extracción: Spotify Search API (`market=CO`), token cacheado, retry con backoff + `Retry-After`.
2. Carga: upsert en bulk a `curated_tracks` (índice único `spotify_track_id`), runs en `ingestion_runs`.
3. Transformación: flatten de track JSON + stats de `popularity` por corrida.
4. Capa analítica: `scripts/build_analysis.py` → `analysis_tracks`.
5. Consumo: `src/dashboard_app.py` (Streamlit + Plotly).

Docs: `docs/architecture.md`, `docs/data-source.md`, `docs/methodology.md`,
`docs/automation.md`, `docs/deployment.md`, `docs/runbook.md`.

## Quickstart local

```powershell
cp .env.example .env   # completa SPOTIFY_CLIENT_ID/SECRET y MONGO_URI
pip install -r requirements.txt
python run_ingestion.py --mode daily --limit-queries 2
python scripts/build_analysis.py
streamlit run src/dashboard_app.py
```

## CLI ingesta

```powershell
python run_ingestion.py --mode daily                  # refresh años recientes
python run_ingestion.py --mode full                   # matriz completa
python run_ingestion.py --mode full --min-popularity 20
python run_ingestion.py --mode daily --limit-queries 2  # smoke test
python scripts/backfill_popularity.py --dry-run       # hidratar popularity faltante
```

## Automatización y despliegue

- Scheduling: GitHub Actions diario 05:00 UTC (lunes = full en 4 shards, resto = daily). Ver `docs/automation.md`.
- DB: MongoDB Atlas M0 free. Dashboard: Streamlit Community Cloud (URL pública). Ver `docs/deployment.md`.
- Secretos requeridos: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `MONGO_URI`, `MONGO_DB_NAME`.

## Estructura

```text
spotify-electronica-colombia/
├── .github/workflows/      # ingestion.yml (diaria+semanal) + ci.yml
├── config/settings.yaml    # matriz queries, paginación, min_popularity, recent_years
├── src/                    # auth, search, ingestion, transform, mongo, dashboard
├── scripts/                # build_analysis.py, backfill_popularity.py
├── docs/                   # arquitectura, fuente, metodología, automation, deployment, runbook
├── tests/diagnostics/      # checks manuales de mongo/conteos/agregaciones
├── Dockerfile              # paridad local / despliegue contenedor
└── run_ingestion.py        # entrypoint CLI
```
