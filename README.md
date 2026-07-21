# Spotify Electrónica Colombia

Proyecto end-to-end de ingeniería de datos orientado a portafolio, enfocado en la recolección, almacenamiento, transformación y análisis de metadatos de la Spotify Web API para estudiar música electrónica en Colombia.

## Objetivo

Construir un pipeline reproducible con enfoque ELT, usando MongoDB como capa inicial de aterrizaje para datos semiestructurados provenientes de la Spotify Web API. El proyecto busca analizar tendencias, artistas, tracks y señales de popularidad asociadas a música electrónica en Colombia durante el periodo 2018–2025.

## Alcance inicial

- Fuente de datos: Spotify Web API.
- Mercado inicial: Colombia.
- Periodo de interés: 2018–2025.
- Dominio analítico: música electrónica y subgéneros relacionados.
- Enfoque arquitectónico: ELT con MongoDB como capa principal de almacenamiento inicial.
- Propósito: construir un proyecto sólido, entendible y publicable en GitHub como portafolio técnico.

## Arquitectura esperada

1. Extracción desde Spotify Web API.
2. Carga inicial de respuestas semiestructuradas en MongoDB.
3. Limpieza y transformación posterior.
4. Construcción de datasets analíticos.
5. Análisis exploratorio y visualización.
6. Dashboard final para comunicar hallazgos.

## Stack previsto

- Python
- Spotify Web API
- MongoDB
- Pandas
- Jupyter / VS Code
- Git y GitHub

## Estructura inicial del repositorio

```text
spotify-electronica-colombia/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── docs/
├── src/
├── notebooks/
├── config/
├── data/
├── tests/
├── dashboard/
├── architecture/
└── metadata/
```