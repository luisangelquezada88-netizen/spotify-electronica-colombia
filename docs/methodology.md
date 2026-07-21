# Metodología del proyecto

## 1. Propósito metodológico

Este proyecto busca construir un pipeline end-to-end de ingeniería de datos para recolectar, almacenar, transformar y analizar metadatos de música electrónica en Colombia usando la Spotify Web API como fuente principal.

La metodología del proyecto combina una lógica de ingeniería de datos aplicada con una orientación analítica descriptiva. El objetivo no es entrenar un modelo predictivo ni replicar el comportamiento total del mercado musical colombiano, sino construir un flujo técnico realista, reproducible y bien documentado que permita explorar patrones de catálogo musical y generar un caso sólido de portafolio.

## 2. Enfoque metodológico general

El proyecto adopta un enfoque **ELT (Extract, Load, Transform)**:

1. **Extract**: obtención de metadatos desde Spotify Web API.
2. **Load**: almacenamiento inicial de respuestas JSON en MongoDB.
3. **Transform**: limpieza, validación, estandarización y preparación posterior para análisis.

Este enfoque se elige porque la fuente principal entrega datos semiestructurados y porque el objetivo del proyecto es preservar primero el dato original antes de transformarlo.

## 3. Tipo de proyecto

Este proyecto debe entenderse como:

- un caso aplicado de ingeniería de datos,
- un proyecto de portafolio técnico,
- un ejercicio de análisis descriptivo sobre metadatos de catálogo,
- una implementación reproducible orientada a GitHub.

No se plantea como:
- estudio estadístico representativo del consumo nacional,
- sistema de recomendación,
- producto comercial,
- solución basada en datos personales de usuarios.

## 4. Pregunta orientadora del proyecto

La pregunta orientadora del proyecto es:

**¿Cómo diseñar e implementar un pipeline ELT reproducible, claro y bien documentado que permita recolectar y analizar metadatos de música electrónica asociada al mercado colombiano usando la Spotify Web API y MongoDB como capa de aterrizaje inicial?**

## 5. Objetivos del proyecto

### Objetivo general

Diseñar e implementar un pipeline end-to-end de ingeniería de datos basado en la Spotify Web API para recolectar, almacenar, transformar y analizar metadatos de música electrónica en Colombia bajo un enfoque ELT con MongoDB.

### Objetivos específicos

- Diseñar una arquitectura de datos clara y defendible para un proyecto de portafolio.
- Implementar un proceso de autenticación y extracción desde la Spotify Web API.
- Cargar respuestas semiestructuradas en MongoDB como capa raw.
- Transformar los datos en colecciones curadas orientadas al análisis.
- Realizar análisis exploratorio sobre metadatos relevantes del dominio.
- Construir una capa final de visualización o dashboard.
- Documentar decisiones técnicas, limitaciones y posibles mejoras futuras.

## 6. Alcance del proyecto

### Alcance temático

El proyecto se centra en **música electrónica y subgéneros asociados**, usando criterios de búsqueda y filtrado definidos para construir una muestra analítica útil.

### Alcance geográfico

El mercado inicial es **Colombia**, usando el parámetro de mercado cuando aplique y documentando claramente los límites de lo que ese parámetro representa dentro de la API.

### Alcance temporal

El rango de interés del proyecto es **2018–2025**.

### Alcance técnico

La fase inicial del proyecto cubre:

- autenticación,
- extracción de metadatos,
- carga raw en MongoDB,
- transformación posterior,
- análisis exploratorio,
- dashboard final.

### Fuera de alcance en esta fase

- machine learning,
- orquestación avanzada,
- streaming,
- data warehouse formal,
- despliegue productivo cloud completo,
- datos de comportamiento individual de usuarios.

## 7. Unidad de análisis

La unidad principal de análisis será el **track** como objeto de catálogo.

Dependiendo del enriquecimiento posterior, también se podrán derivar unidades secundarias de análisis:

- artista,
- álbum,
- año de lanzamiento,
- conjunto de tracks por consulta o corrida de ingesta.

## 8. Fuente de datos

La fuente principal del proyecto es la **Spotify Web API**, una API REST que entrega metadatos JSON sobre artistas, álbumes y tracks. Todas las llamadas requieren autorización, y en este proyecto se utilizará el flujo **Client Credentials** porque el objetivo se limita a endpoints de catálogo sin datos de usuario. 

## 9. Estrategia de extracción inicial

La estrategia metodológica inicial no será “extraer todo”, sino ejecutar un **MVP controlado de ingesta**.

Ese MVP deberá:

- usar un conjunto acotado de términos o criterios de consulta,
- limitar volumen por corrida,
- registrar parámetros exactos de la ejecución,
- almacenar resultados raw sin transformaciones destructivas,
- evaluar primero calidad y estructura antes de escalar.

La primera fase de extracción será por tanto **exploratoria y controlada**, no masiva.

## 10. Criterios de selección inicial

Los registros iniciales se seleccionarán siguiendo criterios combinados como:

- relación temática con música electrónica,
- disponibilidad de metadatos relevantes en Spotify,
- pertinencia para el mercado colombiano,
- pertenencia al rango temporal 2018–2025 cuando el campo esté disponible,
- utilidad analítica para responder preguntas del proyecto.

La metodología debe dejar claro que estos criterios construyen una **muestra analítica intencional**, no una muestra probabilística representativa de toda la música escuchada en Colombia.

## 11. Rol de la popularity

La variable `popularity` podrá usarse como señal analítica inicial cuando esté disponible en los objetos recuperados, pero debe interpretarse con cuidado.

Dentro del proyecto:

- `popularity` no representa directamente reproducciones reales,
- no equivale a ranking oficial del mercado colombiano,
- no reemplaza métricas de consumo observacional,
- sí puede servir como proxy comparativa interna dentro del catálogo consultado.

Si se usa como criterio analítico, debe documentarse siempre como una medida de plataforma y no como una verdad absoluta sobre preferencia musical.

## 12. Restricciones metodológicas

Este proyecto está condicionado por varias restricciones derivadas de la fuente:

### 12.1 Autorización y tipo de acceso

Todas las llamadas a la Spotify Web API requieren autorización. El flujo Client Credentials es servidor-a-servidor y no permite acceder a información privada o personalizada de usuarios. 

### 12.2 Rate limits

Spotify aplica límites de uso en una ventana rodante de 30 segundos y puede responder con `429 Too Many Requests` cuando una aplicación excede esos límites. La documentación recomienda implementar backoff y respetar `Retry-After`. [web:13]

### 12.3 Restricciones por modo de desarrollo

Spotify anunció cambios en 2026 para Development Mode, incluyendo límites para nuevos Client IDs y acceso restringido a un conjunto más pequeño de endpoints soportados. Esto obliga a documentar con precisión qué endpoints están disponibles y validar el alcance real del proyecto al momento de implementación. 
### 12.4 Limitaciones de cobertura

El proyecto depende de cómo Spotify organiza y expone su catálogo y metadatos. No toda clasificación por género es perfecta, no todos los objetos contienen los mismos atributos, y algunos campos pueden estar vacíos, deprecados o ser insuficientes para análisis profundos. 

## 13. Criterios de calidad de datos

La metodología de transformación debe incluir al menos estos controles mínimos:

- identificación única del track,
- eliminación o control de duplicados,
- validación de campos críticos no nulos,
- normalización de estructuras anidadas relevantes,
- registro de errores o anomalías por corrida.

Ejemplos de campos críticos:
- `id`
- `name`
- `artists`
- `album`
- `external_urls.spotify`
- `available_markets` cuando aplique

## 14. Estrategia de procesamiento

La estrategia de procesamiento seguirá estas etapas:

### Etapa 1: extracción
Autenticación, construcción de requests, paginación, control de límites y almacenamiento raw.

### Etapa 2: landing raw
Persistencia de respuestas JSON y metadata de corrida en MongoDB.

### Etapa 3: curación
Limpieza, deduplicación, flattening y estandarización de documentos.

### Etapa 4: preparación analítica
Construcción de vistas, agregaciones o datasets derivados.

### Etapa 5: análisis y visualización
Consumo desde notebooks y dashboard final.

## 15. Supuestos metodológicos

El proyecto asume que:

- los metadatos ofrecidos por Spotify son suficientes para un caso analítico descriptivo inicial,
- el mercado colombiano puede usarse como filtro de trabajo razonable, aunque no capture por sí solo toda la complejidad del consumo musical en Colombia,
- una muestra controlada y bien documentada puede ser más valiosa para portafolio que una recolección masiva poco defendible,
- la claridad de la implementación es prioritaria frente a la complejidad excesiva.

## 16. Riesgos metodológicos

Los principales riesgos metodológicos son:

- sesgo por selección de términos de búsqueda,
- ruido en clasificación temática de subgéneros,
- duplicación entre consultas,
- dependencia de disponibilidad de campos de la API,
- interpretar de forma excesiva métricas como `popularity`,
- escalar el volumen demasiado pronto sin validar calidad.

## 17. Criterio de MVP

El MVP metodológico del proyecto debe cumplir con estas condiciones:

- una extracción pequeña pero reproducible,
- persistencia raw en MongoDB,
- una transformación mínima documentada,
- una primera colección curated,
- al menos un análisis exploratorio defendible,
- una narrativa clara de limitaciones y decisiones técnicas.

Si una decisión aumenta complejidad pero no mejora claridad, trazabilidad o valor de portafolio, debe posponerse para fases posteriores.

## 18. Valor metodológico para portafolio

La metodología está diseñada no solo para obtener datos, sino para demostrar criterio técnico en:

- definición de alcance,
- manejo de restricciones reales de API,
- modelado de una fuente semiestructurada,
- trazabilidad del pipeline,
- documentación de decisiones,
- construcción gradual de un proyecto end-to-end.

## 19. Próximos pasos metodológicos

Después de esta definición metodológica, el siguiente bloque del proyecto debe cubrir:

1. documentación detallada de la fuente (`data-source.md`),
2. diagramas de arquitectura y flujo,
3. definición operativa del MVP de extracción,
4. diseño inicial de colecciones MongoDB,
5. implementación del módulo de autenticación y extracción.

## 20. Resumen metodológico

Este proyecto sigue una metodología aplicada y gradual para construir un pipeline ELT de metadatos musicales basado en Spotify. El foco está en la claridad del diseño, la reproducibilidad técnica, el manejo consciente de restricciones y la generación de un caso de portafolio sólido y defendible.