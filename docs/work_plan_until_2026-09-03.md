# Plan de trabajo hasta la reunion del 03.09.2026

Fecha actual: 26.08.2026

Objetivo para la reunion:

Mostrar que el tema ya esta delimitado, que existe una base de datos inicial,
que hay un prototipo comparativo y que los siguientes pasos son realistas para
una Bachelorarbeit de 8 semanas.

## Miercoles 26.08.2026

Estado: preparado.

Tareas completadas:

- definir alcance Docker;
- ampliar fuentes oficiales;
- ampliar casos tecnicos;
- ampliar preguntas de evaluacion a 30;
- ampliar grafo inicial;
- generar informe de avance.

Pendiente opcional:

- leer con calma `docs/progress_report_2026-08-26.md`;
- marcar 2 preguntas que te gusten para explicarlas a la profe.

## Jueves 27.08.2026

Objetivo:

Entender los 30 casos sin entrar todavia en codigo dificil.

Tareas:

- leer `docs/docker_case_catalog.md`;
- elegir 3 casos principales para la reunion:
  - service discovery;
  - `.env` vs runtime environment;
  - startup order/healthcheck;
- escribir en tus palabras por que esos casos son relacionales;
- anotar dudas tecnicas.

Resultado esperado:

- 3 ejemplos listos para explicar oralmente.

## Viernes 28.08.2026

Objetivo:

Mejorar la explicacion teorica.

Tareas:

- leer la idea basica de RAG;
- leer la idea basica de LightRAG;
- escribir media pagina sobre la diferencia entre Classic RAG y LightRAG;
- revisar que la pregunta de investigacion todavia encaje con Docker support.

Resultado esperado:

- explicacion teorica corta para la presentacion.

## Sabado 29.08.2026

Objetivo:

Revisar resultados iniciales.

Tareas:

- ejecutar `.\bachelor_rag_project\run.ps1 status`;
- ejecutar Classic y Graph sobre todas las preguntas;
- abrir los CSV generados en `results`;
- seleccionar 2 preguntas donde graph retrieval parezca mejor;
- seleccionar 1 pregunta donde todavia haya ruido o limite.

Resultado esperado:

- ejemplos honestos: una ventaja clara y una limitacion.

## Domingo 30.08.2026

Objetivo:

Preparar evaluacion cientifica.

Tareas:

- revisar `experiments/manual_scoring_template.csv`;
- decidir criterios:
  - correctness;
  - completeness;
  - traceability;
  - consistency;
  - usefulness;
- preparar escala 1-5;
- puntuar manualmente 5 preguntas como prueba.

Resultado esperado:

- mini tabla de evaluacion piloto.

## Lunes 31.08.2026

Objetivo:

Preparar material de reunion.

Tareas:

- actualizar presentacion con el estado actual;
- incluir numeros:
  - 11 fuentes;
  - 17 casos;
  - 30 preguntas;
  - 52 nodos;
  - 42 relaciones;
- incluir una diapositiva "Offene Fragen".

Resultado esperado:

- presentacion lista para mostrar.

## Martes 01.09.2026

Objetivo:

Ensayar.

Tareas:

- preparar explicacion de 3 minutos;
- preparar explicacion de 8 minutos;
- practicar en aleman;
- revisar preguntas para la profe.

Resultado esperado:

- puedes explicar el tema sin leer todo.

## Miercoles 02.09.2026

Objetivo:

Ultima revision.

Tareas:

- revisar presentacion;
- revisar `progress_report_2026-08-26.md`;
- abrir el proyecto y comprobar que `run.ps1 status` funciona;
- preparar una carpeta o pestanas abiertas para la reunion.

Resultado esperado:

- todo listo y sin improvisacion de ultimo minuto.

## Jueves 03.09.2026

Objetivo:

Reunion con Prof. Kastsian.

Mostrar:

- problema real;
- pregunta de investigacion;
- caso Docker support;
- dataset inicial;
- prototipo comparativo;
- resultados preliminares;
- preguntas abiertas.

Frase clave:

> Ich moechte nicht allgemein zeigen, dass GraphRAG immer besser ist, sondern
> untersuchen, bei welchen technischen Supportfragen ein graphbasierter Ansatz
> gegenueber klassischem RAG Vorteile bringt.
