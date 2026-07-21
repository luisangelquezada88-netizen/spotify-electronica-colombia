# Fuente de datos: Spotify Web API

## 1. Descripción general

La fuente principal de datos de este proyecto es la **Spotify Web API**, una API REST que permite recuperar metadatos del catálogo de Spotify, incluyendo información sobre tracks, artistas, álbumes, mercados y otros objetos asociados al ecosistema musical de la plataforma. La API devuelve respuestas en formato JSON y está orientada a integraciones que consumen datos del catálogo o interactúan con funciones de usuario según el tipo de autorización usado. 

Para este proyecto, la fuente se utilizará únicamente como proveedor de **metadatos de catálogo**, no de comportamiento individual de usuarios.

## 2. Pertinencia de la fuente para el proyecto

La Spotify Web API es pertinente para este proyecto porque:

- ofrece acceso estructurado a metadatos musicales de catálogo,
- permite recuperar información de tracks, artistas y álbumes,
- expone campos útiles para análisis exploratorio,
- devuelve datos en JSON, lo que encaja con una arquitectura ELT sobre MongoDB,
- permite construir un caso aplicado de extracción y modelado de datos desde una API real. 

## 3. Tipo de datos disponibles

La API entrega principalmente:

- identificadores únicos de objetos de Spotify,
- nombres de tracks, artistas y álbumes,
- URLs y URIs del catálogo,
- atributos de disponibilidad por mercados en algunos objetos,
- popularidad para ciertos objetos,
- fechas de lanzamiento,
- relaciones entre tracks, artistas y álbumes,
- enlaces a recursos relacionados dentro de la propia API.

La estructura exacta depende del endpoint consultado.

## 4. Tipo de acceso utilizado en este proyecto

Este proyecto utilizará el flujo **Client Credentials** para autenticación.

Este flujo es adecuado porque:

- es un mecanismo servidor-a-servidor,
- no requiere login interactivo del usuario final,
- sirve para consumir endpoints que no dependen de permisos de usuario,
- encaja con un proyecto orientado a metadatos públicos de catálogo.

Como contrapartida, este flujo **no permite** acceder a información privada o personalizada de usuarios.

## 5. Requisitos de autenticación

Todas las llamadas a Spotify Web API requieren autorización.

Para obtener acceso se necesita:

- una aplicación registrada en Spotify for Developers,
- un `Client ID`,
- un `Client Secret`,
- una solicitud de token al endpoint de autenticación.

La obtención del token se realiza mediante una solicitud `POST` al endpoint:

`https://accounts.spotify.com/api/token`

usando `grant_type=client_credentials` y un cuerpo `application/x-www-form-urlencoded`. [web:451][web:26]

## 6. Consideraciones del modo de desarrollo

Las aplicaciones nuevas comienzan en **Development Mode**. Spotify documenta que este modo tiene restricciones más fuertes que el modo de cuota extendida y, en 2026, endureció reglas para nuevas integraciones.

Aspectos importantes para este proyecto:

- las apps nuevas comienzan en development mode,
- development mode tiene menor cuota que extended quota mode,
- Spotify introdujo restricciones adicionales en 2026 para nuevos Client IDs,
- el acceso disponible puede depender del estado de la app y del tipo de endpoint. 

Por eso, antes de programar extracción masiva, el proyecto debe validar el acceso real de la app creada.

## 7. Base URL y forma de consumo

La base URL general documentada para la Web API es:

`https://api.spotify.com`

Los recursos se consumen mediante solicitudes HTTP estándar y devuelven respuestas JSON en UTF-8. La API utiliza verbos como `GET`, `POST`, `PUT` y `DELETE`, aunque en este proyecto la operación dominante será `GET` porque la finalidad es recuperar metadatos. [web:440]

## 8. Endpoints relevantes para el proyecto

### 8.1 Search

El endpoint `search` permite recuperar información del catálogo a partir de una cadena de búsqueda y tipos de objeto como `track`, `artist` o `album`. Es el candidato principal para el MVP porque facilita construir una primera estrategia de ingesta basada en términos controlados.

Uso general:
- permite búsquedas por palabra clave,
- soporta selección de tipo de objeto,
- suele devolver resultados paginados,
- es útil para una fase exploratoria inicial.

### 8.2 Get Track / Get Several Tracks

Estos endpoints permiten recuperar metadatos de tracks a partir de IDs ya conocidos. Son útiles cuando la estrategia de extracción se divide en dos pasos: primero búsqueda, luego hidratación o enriquecimiento por ID.

### 8.3 Get Artist

El endpoint de artista permite obtener metadatos adicionales por artista, incluyendo nombre, URLs y algunos campos asociados al objeto artista. Spotify documenta además que algunos atributos del artista están deprecados, como `genres` y `popularity` en esa referencia, por lo que no conviene depender ciegamente de todos los campos históricos.

### 8.4 Get Available Markets

Este endpoint devuelve la lista de mercados donde Spotify está disponible y puede ser útil para validar el uso del código `CO` como parte del contexto geográfico del proyecto.

## 9. Paginación

Spotify documenta que algunos endpoints soportan paginación mediante los parámetros `limit` y `offset`.

Esto implica que el pipeline debe:

- controlar el tamaño de lote por request,
- iterar resultados cuando existan páginas adicionales,
- registrar el avance por consulta,
- evitar asumir que una respuesta contiene todos los resultados disponibles.

La paginación es un aspecto central para la capa de extracción y no debe dejarse implícita.

## 10. Rate limits

Spotify aplica límites de uso sobre una ventana rodante de 30 segundos. Cuando una app excede ese límite, la API responde con código `429 Too Many Requests`. 

Implicaciones directas para el proyecto:

- no se debe implementar extracción agresiva,
- deben usarse pausas controladas entre requests,
- el cliente debe respetar `Retry-After` cuando aparezca,
- debe existir manejo de reintentos y logging de errores.

El límite varía según el modo de cuota de la aplicación.

## 11. Códigos de error relevantes

La documentación general de Spotify Web API indica, entre otros, estos códigos relevantes para el proyecto: 

- `401 Unauthorized`: token ausente, inválido o rechazado.
- `403 Forbidden`: acceso denegado para el recurso o contexto.
- `404 Not Found`: recurso no encontrado.
- `429 Too Many Requests`: se excedió el rate limit.

Estos códigos deben quedar contemplados desde el diseño de la capa de extracción.

## 12. Campos potencialmente útiles para el análisis

Dependiendo del endpoint y del objeto, algunos campos de interés potencial son:

### En tracks
- `id`
- `name`
- `popularity`
- `artists`
- `album`
- `external_urls`
- `available_markets`
- `uri`

### En artistas
- `id`
- `name`
- `external_urls`
- `images`
- `uri`

### En álbumes
- `id`
- `name`
- `release_date`
- `artists`
- `total_tracks`
- `external_urls`
- `uri`

La disponibilidad exacta de cada campo debe validarse empíricamente en la primera corrida del proyecto. 

## 13. Restricciones analíticas de la fuente

La Spotify Web API es útil, pero no debe interpretarse como una fuente exhaustiva de comportamiento del mercado colombiano.

Limitaciones importantes:

- los resultados dependen del catálogo accesible y del endpoint consultado,
- la clasificación temática por género o subgénero no siempre es directa,
- algunos campos pueden estar vacíos o ser inconsistentes entre objetos,
- métricas como `popularity` no equivalen a un conteo observable de reproducciones reales,
- el parámetro de mercado no convierte automáticamente los datos en una medición exacta del consumo de un país. [web:503][web:442]

## 14. Riesgos de uso en este proyecto

Los principales riesgos de usar esta fuente son:

- sesgo por estrategia de búsqueda,
- límites de acceso derivados de development mode,
- dependencia de cambios recientes en la plataforma,
- posibles campos deprecados o no disponibles,
- sobreinterpretación de señales como popularity,
- duplicación de resultados entre consultas.

## 15. Implicaciones para el diseño del pipeline

Debido a las características de la fuente, el pipeline debe diseñarse con estas reglas:

- autenticación desacoplada del resto de la extracción,
- parámetros de búsqueda centralizados,
- requests pequeñas y controladas,
- almacenamiento raw antes de transformar,
- persistencia de metadata de corrida,
- validación de campos críticos antes de curar,
- control explícito de paginación y reintentos.

Estas implicaciones justifican la elección de un enfoque ELT con MongoDB como capa de aterrizaje inicial.

## 16. Decisiones derivadas para el MVP

A partir de esta fuente, el MVP del proyecto debe:

- comenzar con pocos términos de búsqueda,
- usar endpoints simples y bien documentados,
- evitar depender de campos inestables o secundarios,
- registrar siempre `query`, `timestamp`, `run_id` y `endpoint`,
- evaluar la calidad del dato antes de ampliar volumen.

La prioridad del MVP es la claridad y la reproducibilidad, no la cobertura masiva.

## 17. Cumplimiento y uso responsable

El proyecto debe respetar las políticas, límites y condiciones de uso vigentes de Spotify for Developers. Esto incluye evitar patrones de extracción agresivos, documentar limitaciones del entorno de desarrollo y no presentar el proyecto como una réplica oficial de métricas de consumo o ranking de Spotify. 

## 18. Resumen de la fuente

La Spotify Web API es una fuente adecuada para este proyecto porque ofrece metadatos estructurados del catálogo musical en formato JSON y permite construir un caso realista de ingeniería de datos sobre una fuente semiestructurada. Su uso, sin embargo, exige atención especial a autenticación, paginación, restricciones de cuota, cambios recientes en development mode y limitaciones analíticas de los campos disponibles. 