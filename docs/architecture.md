# Arquitectura del proyecto

## 1. Propósito de la arquitectura

Este proyecto implementa un flujo end-to-end de ingeniería de datos para recolectar, almacenar, transformar y analizar metadatos de música electrónica en Colombia usando la Spotify Web API como fuente principal. La arquitectura está diseñada para priorizar claridad, trazabilidad y reproducibilidad.

El proyecto adopta un enfoque **ELT (Extract, Load, Transform)** en lugar de una implementación ETL clásica. La razón principal es que la Spotify Web API entrega datos en formato JSON semiestructurado, por lo que resulta más natural y defendible almacenar primero las respuestas en una base documental antes de transformarlas para análisis posterior. Spotify además exige autorización para todas las llamadas Web API y ofrece endpoints de catálogo que devuelven metadatos de artistas, álbumes y tracks, lo que encaja bien con una capa de aterrizaje documental. [web:440][web:26]

## 2. Decisión arquitectónica principal

### Enfoque elegido

La arquitectura inicial del proyecto sigue esta secuencia:

1. Extracción de metadatos desde Spotify Web API.
2. Carga inicial en MongoDB como capa landing/raw.
3. Transformación posterior de los documentos almacenados.
4. Generación de colecciones curadas para análisis.
5. Consumo analítico desde notebooks y dashboard.

### Justificación

Se eligió MongoDB como capa inicial de almacenamiento porque:

- Spotify Web API devuelve respuestas JSON con estructuras anidadas y campos variables según endpoint. [web:440]
- El enfoque ELT permite preservar la respuesta original para trazabilidad y auditoría técnica.
- Una base documental reduce la fricción inicial respecto a una normalización relacional temprana.
- El proyecto busca mostrar criterio realista de ingeniería de datos para fuentes semiestructuradas.

## 3. Evolución respecto al diseño académico base

El documento de investigación original plantea una lógica ETL con PostgreSQL como punto de carga principal. En este proyecto, esa lógica se reinterpreta hacia un diseño ELT con MongoDB como almacenamiento inicial.

Esto no cambia el objetivo analítico del proyecto. Lo que cambia es el orden técnico del procesamiento:

- **Diseño original**: extraer, transformar, normalizar y cargar en PostgreSQL.
- **Diseño del proyecto**: extraer, cargar en MongoDB, transformar después y preparar una capa analítica derivada.

La capa relacional no queda descartada para siempre, pero no forma parte de la fase inicial del MVP.

## 4. Componentes de la arquitectura

### 4.1 Fuente de datos

La fuente principal es la **Spotify Web API**, utilizada mediante autenticación **Client Credentials Flow** para acceder a endpoints de catálogo sin datos de usuario. Este flujo permite autenticación servidor-a-servidor y requiere obtener un access token antes de llamar a la API. [web:26][web:451]

### 4.2 Capa de extracción

La capa de extracción estará implementada en Python y tendrá estas responsabilidades:

- autenticarse contra Spotify,
- construir consultas con parámetros definidos,
- manejar paginación,
- controlar rate limiting y reintentos,
- registrar metadatos de ejecución.

El endpoint inicial más probable para el MVP es `search`, ya que permite buscar elementos del catálogo por palabra clave y recuperar metadatos de tracks, artistas o álbumes. [web:442][web:453]

### 4.3 Capa de aterrizaje raw

La primera persistencia de datos se hará en MongoDB, almacenando respuestas crudas o mínimamente enriquecidas. Esta capa preserva los documentos originales para trazabilidad, depuración y reprocesamiento.

Colecciones candidatas de esta capa:

- `raw_search_results`
- `raw_tracks`
- `raw_artists`
- `ingestion_runs`

### 4.4 Capa curated

Después de la carga raw, se construirán colecciones curadas con estructura más estable y orientada al análisis. En esta etapa se aplicarán:

- deduplicación,
- flattening de campos anidados,
- estandarización de nombres y tipos,
- validación mínima de campos críticos,
- descarte de registros incompletos según reglas definidas.

Colecciones candidatas:

- `curated_tracks`
- `curated_artists`
- `curated_release_summary`

### 4.5 Capa analítica

La capa analítica estará orientada a responder preguntas del proyecto, por ejemplo:

- tracks de música electrónica con mayor popularity,
- artistas más frecuentes o dominantes,
- comportamiento por año de lanzamiento,
- patrones de distribución por subgénero o etiquetas asociadas,
- ranking de registros disponibles en mercado Colombia.

Esta capa puede materializarse como:
- colecciones agregadas en MongoDB,
- exportaciones tabulares para análisis,
- datasets derivados usados por notebooks o dashboard.

### 4.6 Capa de análisis y visualización

Los resultados serán consumidos desde:

- notebooks para EDA y validación analítica,
- scripts analíticos reproducibles,
- dashboard final para comunicar hallazgos.

El dashboard no será una fuente de transformación primaria; será una capa de consumo sobre datos ya preparados.

## 5. Flujo general del dato

El flujo esperado del pipeline es el siguiente:

1. El sistema carga variables de entorno y parámetros de configuración.
2. Se solicita un access token a Spotify.
3. Se ejecutan consultas al catálogo usando parámetros controlados.
4. Las respuestas JSON se almacenan en colecciones raw.
5. Se ejecutan transformaciones posteriores sobre esos documentos.
6. Se generan colecciones curadas y salidas analíticas.
7. Los resultados se consumen desde notebooks y dashboard.

## 6. Capas de datos

Para dar claridad al proyecto, se usará una convención de capas inspirada en `raw`, `curated` y `analytics`.

### Raw
Contiene la respuesta original de la API o una versión casi cruda, con mínimos metadatos técnicos como timestamp de ingesta, query ejecutada y `run_id`.

### Curated
Contiene documentos limpios, deduplicados y estructurados para análisis.

### Analytics
Contiene agregaciones, resúmenes y datasets finales para consumo analítico y visualización.

## 7. Principios de diseño

La arquitectura sigue estos principios:

- **Trazabilidad**: conservar la relación entre dato crudo y dato transformado.
- **Reproducibilidad**: permitir reruns controlados de la ingesta.
- **Separación de responsabilidades**: extraer, almacenar, transformar y analizar como etapas diferenciadas.
- **Simplicidad defendible**: evitar complejidad innecesaria en un primer proyecto end-to-end.
- **Documentación primero**: cada decisión técnica relevante debe quedar explicada.

## 8. Decisiones técnicas iniciales

### Base de datos
MongoDB como capa principal de aterrizaje y almacenamiento inicial.

### Lenguaje principal
Python.

### Configuración
Variables de entorno para secretos y parámetros sensibles; archivos de configuración para parámetros operativos reproducibles.

### Persistencia de metadata operativa
Cada corrida de ingesta debe registrar:
- `run_id`
- timestamp de inicio y fin
- endpoint usado
- parámetros de consulta
- cantidad de documentos recuperados
- errores y reintentos

## 9. Riesgos arquitectónicos

Los principales riesgos del diseño son:

- dependencia de límites y cambios de comportamiento de la Spotify API, incluyendo rate limits. [web:13]
- sesgo de muestreo derivado del uso de queries por palabras clave o criterios de selección.
- duplicados y solapamientos entre consultas.
- sobrecrecimiento de colecciones raw si no se controlan corridas y deduplicación.
- tentación de convertir la fase inicial en una arquitectura demasiado compleja.

## 10. Alcance técnico de la fase inicial

Esta primera fase no incluye:

- orquestación avanzada con Airflow,
- despliegue cloud completo,
- data warehouse formal,
- streaming,
- capa relacional obligatoria,
- machine learning.

El objetivo de la fase inicial es construir un pipeline **claro, ejecutable, bien documentado y defendible**.

## 11. Próxima evolución

Una vez estabilizada la ingesta y la capa curated, el proyecto puede evolucionar hacia:

- exportaciones tabulares más estables,
- una capa relacional o analítica secundaria,
- pruebas automáticas más amplias,
- contenedorización,
- automatización por jobs programados,
- monitoreo de calidad de datos.

## 12. Resumen arquitectónico

La arquitectura de este proyecto prioriza una lógica ELT con MongoDB como landing zone para datos semiestructurados provenientes de Spotify. Sobre esa base, se construyen transformaciones posteriores, una capa analítica y un dashboard final, manteniendo una narrativa técnica clara y apropiada para un proyecto de portafolio.