# Bachelorarbeit Project: Classic RAG vs GraphRAG for Docker Troubleshooting

Este proyecto es el laboratorio inicial para la Bachelorarbeit. El objetivo es
comparar, de forma controlada, como se comportan dos enfoques de recuperacion de
informacion en preguntas tecnicas de troubleshooting.

Tema provisional:

> Vergleich von klassischem RAG und GraphRAG fuer technische
> Troubleshooting-Fragen: Eine Fallstudie zu Docker Compose.

La idea no es construir un producto enorme, sino preparar una comparacion justa:

- misma base de conocimiento tecnica;
- mismas preguntas de prueba;
- categorias de preguntas claras;
- dos estrategias de recuperacion;
- resultados guardados por pregunta y por categoria.

## Que contiene ahora

- `data/raw/docker_support_notes.md`: mini base de conocimiento creada a partir
  de documentacion oficial de Docker, escrita en nuestras propias palabras.
- `data/sources.json`: enlaces oficiales usados como fuentes.
- `data/knowledge/docker_support_graph.json`: relaciones tipo grafo
  `problema -> componente -> causa -> diagnostico -> solucion -> fuente`.
- `data/questions/docker_support_questions.jsonl`: preguntas de prueba.
- cada pregunta incluye categoria, dificultad y numero esperado de relaciones.
- `docs/docker_case_catalog.md`: catalogo legible de 23 casos tecnicos.
- `docs/question_design_methodology.md`: explicacion metodologica de como se
  construyeron las preguntas y por que estan divididas por categoria.
- `docs/post_meeting_direction_2026-09-03.md`: nueva direccion despues del
  feedback de los tutores.
- `docs/meeting_preparation_2026-09-03.md`: resumen para la reunion con la
  profesora.
- `docs/progress_report_2026-08-26.md`: informe de avance actual.
- `docs/work_plan_until_2026-09-03.md`: plan diario hasta la reunion.
- `src/rag_compare`: codigo del experimento.
- `results`: carpeta donde se guardan respuestas.
- `experiments/manual_scoring_template.csv`: plantilla para evaluar respuestas.

## Como probarlo

Desde la carpeta principal puedes usar el helper de PowerShell:

```powershell
.\bachelor_rag_project\run.ps1 sources
```

Ver las preguntas:

```powershell
.\bachelor_rag_project\run.ps1 questions
```

Ver preguntas agrupadas por categoria:

```powershell
.\bachelor_rag_project\run.ps1 categories
```

Ver el estado del dataset:

```powershell
.\bachelor_rag_project\run.ps1 status
```

Ver nodos y relaciones del grafo en la terminal:

```powershell
.\bachelor_rag_project\run.ps1 graph
```

Ver estadisticas del grafo:

```powershell
.\bachelor_rag_project\run.ps1 graph-stats
```

Generar una vista visual del grafo:

```powershell
.\bachelor_rag_project\view_graph.ps1
```

El archivo visual se crea en:

```text
bachelor_rag_project\docs\docker_support_graph_view.html
```

Generar un grafico de la comparacion por categorias:

```powershell
.\bachelor_rag_project\run.ps1 chart
```

El archivo visual se crea en:

```text
bachelor_rag_project\docs\category_comparison_chart.png
```

Probar una pregunta con RAG clasico:

```powershell
.\bachelor_rag_project\run.ps1 query --method classic --question "Why can my app container not reach the database container by service name?"
```

Probar la misma pregunta con recuperacion tipo grafo:

```powershell
.\bachelor_rag_project\run.ps1 query --method graph --question "Why can my app container not reach the database container by service name?"
```

Ejecutar varias preguntas y guardar resultados:

```powershell
.\bachelor_rag_project\run.ps1 run-testset --method classic --limit 5
.\bachelor_rag_project\run.ps1 run-testset --method graph --limit 5
```

Ejecutar la comparacion completa por categorias:

```powershell
.\bachelor_rag_project\run.ps1 compare
```

Crear una plantilla para evaluacion manual:

```powershell
.\bachelor_rag_project\run.ps1 manual-template
```

Si prefieres llamar Python directamente, tambien funciona:

```powershell
python .\bachelor_rag_project\run_compare.py sources
```

## Importante

Esta primera version no usa todavia un LLM real como capa de generacion final.
Sirve para dejar preparada y verificable la base experimental: documentos,
preguntas, categorias, evidencias y resultados comparables.

Estado actual despues del feedback de los tutores:

- 12 fuentes oficiales o tecnicas registradas.
- 23 casos tecnicos controlados.
- 48 preguntas de prueba.
- 6 categorias con 8 preguntas cada una.
- 93 nodos en el grafo.
- 118 relaciones en el grafo.
- Nuevas relaciones: `requires`, `conflicts_with`, `distinguished_from` y
  `documented_in`.

Despues anadiremos:

1. generacion de respuestas con un modelo;
2. integracion real o adaptada con GraphRAG/LightRAG;
3. evaluacion manual y/o semiautomatica;
4. tablas y graficos finales para la tesis.

## Pregunta de investigacion provisional

Version corta:

> Verbessert GraphRAG gegenueber klassischem RAG die Antwortqualitaet bei
> relationalen und komplexen technischen Troubleshooting-Fragen?

Version mas precisa:

> Inwieweit verbessert GraphRAG gegenueber klassischem RAG die
> Antwortqualitaet bei technischen Troubleshooting-Fragen, die relationale
> Zusammenhaenge zwischen Problem, Komponente, Ursache und Loesung erfordern?

## Aktueller automatischer Zwischenbefund

Die erste retrieval-basierte Auswertung zeigt Vorteile fuer den graphbasierten
Ansatz vor allem bei:

- relationalen Troubleshooting-Fragen;
- Multi-Hop-Fragen;
- Fragen zur Nachvollziehbarkeit;
- Konfigurationskonflikten.

Bei prozeduralen Fragen ist der Vorteil nicht sichtbar. Das ist wichtig, weil
die Arbeit dadurch differenziert argumentieren kann: GraphRAG ist nicht
automatisch immer besser, sondern vor allem bei Fragen mit relevanten
technischen Beziehungen.
