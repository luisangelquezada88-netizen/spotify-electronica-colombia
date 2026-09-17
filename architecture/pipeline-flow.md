# Flujo del pipeline ELT

> Fuente viva de este diagrama. El archivo anterior `pipeline-flow.mmd`
> (texto plano, GitHub no lo renderizaba) fue reemplazado por este `.md`.

```mermaid
flowchart TD
    A[Cron GHA diario 05:00 UTC<br/>o workflow_dispatch manual] --> B{Es lunes?}
    B -- Si --> C[Mode FULL<br/>10 terminos x 2018-2025 = 80 queries<br/>4 shards paralelos]
    B -- No --> D[Mode DAILY<br/>10 terminos x años recientes = 30 queries]

    C --> E[Cargar settings.yaml + secretos]
    D --> E

    E --> F[Token OAuth 2.0 cacheado 1h]
    F --> G[Por query: paginar search<br/>limit=10, market=CO]

    G --> H{Respuesta 429 con<br/>Retry-After mayor 300s?}
    H -- Si --> I[Abortar corrida<br/>status=quota_exhausted<br/>progreso parcial guardado]
    H -- No --> J[429/5xx: backoff + reintento]

    J --> K[Transform: aplanar track JSON<br/>filtro min_popularity si aplica]
    K --> L[Bulk upsert en curated_tracks<br/>indice unico spotify_track_id]

    L --> M{Pagina con menos de 10 items?}
    M -- Si --> N[Parada temprana:<br/>siguiente query]
    M -- No --> O[Sleep + siguiente offset]
    O --> G

    N --> P{Mas queries?}
    P -- Si --> G
    P -- No --> Q[Doc en ingestion_runs:<br/>modo, stats de popularity, errores]

    Q --> R[Solo shard 0:<br/>build_analysis.py -> analysis_tracks]
    R --> S[Dashboard Streamlit publico]
    S --> T[Fin]
```

## Reglas verificadas contra la API (2026-09)

- `limit=10` máximo aceptado (`>10` da `400 Invalid limit`).
- `offset` máximo útil 1000; la parada temprana evita paginar en vacío.
- `popularity` llega nulo en search y `/v1/tracks` da `403`: el filtro por
  umbral está implementado pero inactivo (`min_popularity: 0`).
  Detalle en `docs/data-source.md` §19.
