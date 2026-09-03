# Diseno de comparacion

## Nueva direccion despues del Betreuer:innen-Gespraech

El foco de la Bachelorarbeit se ajusta a una pregunta mas concreta:

> Vergleich von klassischem RAG und GraphRAG fuer technische
> Troubleshooting-Fragen: Eine Fallstudie zu Docker Compose.

La investigacion no debe demostrar que GraphRAG siempre es mejor, sino
identificar en que tipo de preguntas tecnicas aporta una ventaja.

## Que comparamos

No comparamos MCP contra RAG. Tampoco comparamos Docker como tecnologia.

Comparamos dos formas de usar conocimiento tecnico para responder preguntas:

1. Classic RAG: recupera fragmentos relevantes desde documentos.
2. GraphRAG/LightRAG: usa representaciones graph-based para capturar
   relaciones entre problemas, componentes, causas, diagnostico y soluciones.

## Por que Docker support

Docker support funciona bien para la tesis porque contiene problemas reales:

- error messages;
- componentes tecnicos;
- causas posibles;
- pasos de diagnostico;
- soluciones;
- relaciones entre configuracion, red, entorno y almacenamiento.

Esto permite evaluar si un enfoque graph-based ayuda especialmente cuando una
pregunta requiere conectar varios elementos.

## Pregunta de investigacion

> Inwieweit verbessert GraphRAG gegenueber klassischem RAG die
> Antwortqualitaet bei technischen Troubleshooting-Fragen, die relationale
> Zusammenhaenge zwischen Problem, Komponente, Ursache und Loesung erfordern?

## Hipotesis de trabajo

GraphRAG/LightRAG podria mejorar frente a Classic RAG en preguntas
relacionales y complejas, por ejemplo cuando la respuesta necesita conectar:

`problem -> affected component -> cause -> diagnostic step -> solution`

Classic RAG podria ser suficiente en preguntas directas, por ejemplo cuando una
respuesta esta claramente en una sola seccion de documento.

## Tipos de preguntas para la evaluacion

### A. Preguntas factuales simples

Ejemplo:

> What is the role of DOCKER_HOST in Docker daemon connection problems?

Estas preguntas suelen estar cubiertas por una seccion documental concreta.

### B. Preguntas procedurales

Ejemplo:

> How can I check which environment values Docker Compose uses for
> interpolation?

Estas preguntas buscan un comando, una comprobacion o un procedimiento.

### C. Preguntas relacionales de troubleshooting

Ejemplo:

> My app container cannot reach the database container by service name in Docker
> Compose. What should I check?

Estas preguntas pueden requerir conectar red, DNS interno, service name,
container port y custom networks.

### D. Preguntas multi-hop

Ejemplo:

> Why does my web service start before the database is ready although
> depends_on is configured?

Estas preguntas necesitan varios pasos: dependency order, readiness,
healthcheck y condicion `service_healthy`.

### E. Preguntas sobre conflictos de configuracion

Ejemplo:

> Why does Docker Compose use a different environment variable value than the
> one in my .env file?

Estas preguntas dependen de reglas de precedencia y de varias fuentes de
configuracion.

### F. Preguntas de trazabilidad

Ejemplo:

> Why should another Compose service use db:5432 instead of localhost:8001?

Estas preguntas evaluan si el sistema puede explicar de forma trazable el
camino desde el problema hasta la solucion.

## Relaciones que queremos modelar

Posibles relaciones en el grafo:

- `affects`: un problema afecta a una componente;
- `may_be_caused_by`: un problema puede tener una causa;
- `diagnosed_by`: una causa o problema se diagnostica con un paso concreto;
- `solved_by`: una causa se resuelve con una solucion;
- `requires`: una solucion requiere una condicion tecnica;
- `conflicts_with`: una configuracion entra en conflicto con otra;
- `documented_in`: una idea esta respaldada por una fuente;
- `related_to`: dos componentes estan conectadas tecnicamente.

La pregunta no es cuantas relaciones maximas soporta GraphRAG, sino cuantas
relaciones utiles se necesitan para mejorar la respuesta en una categoria de
preguntas concreta.

## Resultado esperado para la tesis

La tesis no debe afirmar que LightRAG siempre es mejor.

La respuesta cientifica esperada sera algo como:

> LightRAG zeigt vor allem dann Vorteile, wenn Support-Anfragen mehrere
> technische Beziehungen zwischen Problem, Komponente, Ursache und Loesung
> enthalten. Bei einfachen faktischen Fragen kann klassisches RAG ausreichend
> sein.
