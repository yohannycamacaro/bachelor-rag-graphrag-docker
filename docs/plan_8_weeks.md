# Plan de trabajo para completar la tesis en 8 semanas

Este plan asume que el tema queda asi:

> Classic RAG vs LightRAG for Docker technical support questions.

La regla principal: cada semana debe producir algo medible o escribible.

## Semana 1: Scope, fuentes y pregunta final

Objetivo:

- cerrar la pregunta de investigacion;
- decidir que partes de Docker entran;
- preparar las fuentes oficiales;
- definir que significa "mejor respuesta".

Resultado esperado:

- pregunta final aprobada;
- lista de fuentes;
- primera estructura de la tesis;
- version 1 del catalogo de preguntas.

Conceptos que debes dominar:

- que es RAG;
- que es GraphRAG;
- que es LightRAG;
- que es una base de conocimiento tecnica;
- diferencia entre documento, chunk, embedding, retrieval y respuesta generada.

## Semana 2: Dataset y casos tecnicos

Objetivo:

- convertir la documentacion de Docker en una base de conocimiento pequena;
- crear 30 a 50 preguntas de soporte;
- separar preguntas simples y relacionales.

Resultado esperado:

- `docker_support_notes.md` ampliado;
- `docker_support_graph.json` ampliado;
- `docker_support_questions.jsonl` con suficientes casos;
- tabla con casos tecnicos.

Estado actual al 26.08.2026:

- 11 fuentes oficiales Docker registradas;
- 17 casos tecnicos documentados;
- 30 preguntas de evaluacion creadas;
- grafo inicial ampliado con nodos y relaciones para problemas, causas y
  soluciones.

Casos tecnicos principales:

- Docker daemon no responde;
- contenedores no se encuentran por service name;
- confusion entre host port y container port;
- variables `.env` no aparecen en el container;
- precedencia de variables en Compose;
- datos desaparecen por falta de volumen;
- red externa de Compose no existe;
- problemas de DNS;
- IPs dinamicas en Compose;
- aislamiento por redes custom.

## Semana 3: Baseline Classic RAG

Objetivo:

- construir el sistema RAG clasico;
- indexar documentos;
- recuperar evidencias por pregunta;
- generar respuestas.

Resultado esperado:

- prototipo Classic RAG ejecutable;
- resultados guardados para el set de preguntas;
- descripcion tecnica para la tesis.

## Semana 4: LightRAG

Objetivo:

- instalar o integrar LightRAG;
- usar la misma base documental;
- generar respuestas para las mismas preguntas.

Resultado esperado:

- prototipo LightRAG ejecutable;
- resultados guardados;
- descripcion de configuracion y limitaciones.

## Semana 5: Evaluacion

Objetivo:

- definir la escala final de evaluacion;
- evaluar respuestas de ambos sistemas;
- justificar criterios con literatura.

Criterios recomendados:

- correctness;
- completeness;
- traceability;
- consistency;
- usefulness for technical support.

Resultado esperado:

- tabla de puntuaciones;
- ejemplos de respuestas buenas y malas;
- notas de evaluacion manual.

## Semana 6: Analisis

Objetivo:

- comparar resultados;
- identificar donde LightRAG ayuda y donde no;
- preparar graficos.

Resultado esperado:

- graficos por criterio;
- analisis por tipo de pregunta;
- respuesta preliminar a la pregunta de investigacion.

## Semana 7: Escritura fuerte

Objetivo:

- escribir Einleitung, Grundlagen, Methodik, Implementierung y Evaluation.

Resultado esperado:

- borrador casi completo;
- citas en Zotero;
- figuras y tablas insertadas.

## Semana 8: Revision y entrega

Objetivo:

- mejorar texto;
- revisar formato THB;
- revisar bibliografia;
- preparar entrega.

Resultado esperado:

- PDF final;
- codigo limpio;
- anexos/resultados organizados;
- version para Kolloquium.
