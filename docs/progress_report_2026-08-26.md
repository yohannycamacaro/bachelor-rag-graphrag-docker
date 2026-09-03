# Fortschrittsbericht vom 26.08.2026

## Kurzfassung auf Deutsch

Der aktuelle Arbeitsstand besteht aus einem eingegrenzten Anwendungsfall, einer
kleinen Docker-Support-Wissensbasis, einem Fragenkatalog und einem ersten
technischen Vergleichsprototyp.

Untersucht werden technische Supportfragen zu Docker-basierten
Entwicklungsumgebungen. Der Fokus liegt auf Fragen, bei denen mehrere
Zusammenhaenge kombiniert werden muessen, zum Beispiel:

- Fehlermeldung;
- betroffene Docker-Komponente;
- moegliche Ursache;
- Diagnose;
- Loesungsschritt.

Der aktuelle Prototyp vergleicht:

1. Classic Retrieval als dokumentenbasierte RAG-Vorstufe;
2. Graph Retrieval als vereinfachte Vorstufe fuer einen spaeteren
   LightRAG/GraphRAG-Ansatz.

## Resumen en espanol

Ya tenemos una base experimental inicial. El proyecto no esta intentando
demostrar todavia que LightRAG es mejor, sino preparar una comparacion justa.

Lo que ya existe:

- 11 fuentes oficiales de Docker registradas;
- 17 casos tecnicos de soporte documentados;
- 30 preguntas de evaluacion;
- un grafo inicial con problemas, componentes, causas y soluciones;
- un script que permite ejecutar preguntas con dos enfoques;
- una plantilla para evaluar manualmente las respuestas.

## Datos actuales del proyecto

Estado generado con `run.ps1 status`:

```text
Sources: 11
Docker support cases: 17
Test questions: 30
  - relational: 24
  - simple: 6
Graph nodes: 52
Graph relations: 42
```

## Resultado preliminar

Se ejecuto una primera comparacion sobre las 30 preguntas usando una metrica
simple de cobertura de palabras clave esperadas.

Resultado inicial:

```text
Classic retrieval: average keyword coverage 0.309
Graph retrieval:   average keyword coverage 0.597
```

Importante:

Esta metrica no es la evaluacion final de la tesis. Solo muestra que la
estructura tipo grafo ya puede recuperar relaciones utiles en varios casos. La
evaluacion final debera incluir criterios manuales como correctness,
completeness, traceability y consistency.

## Ejemplo para explicar en la reunion

Pregunta:

> My app container cannot reach the database container by service name in Docker
> Compose. What should I check?

Classic retrieval:

- recupera secciones de texto relacionadas con networking y ports;
- puede mezclar informacion de varias secciones;
- la relacion causa-solucion no siempre queda explicita.

Graph retrieval:

- recupera relaciones como:
  `service name cannot be reached -> may be caused by -> services are not on the same network`;
- conecta el problema con:
  - Compose default network;
  - same network;
  - host port vs container port;
  - service name and container port.

Interpretacion:

Este ejemplo muestra por que el caso Docker support es adecuado: muchas
preguntas no son simples busquedas de texto, sino preguntas relacionales.

## Was ich im Treffen sagen kann

> Ich habe den Anwendungsfall auf eine technische Support-Wissensbasis zu Docker
> eingegrenzt. Dazu habe ich eine kleine kontrollierte Datenbasis aus der
> offiziellen Docker-Dokumentation erstellt. Der aktuelle Fragenkatalog umfasst
> 30 Supportfragen, davon 24 relationale Fragen. Ein erster Prototyp vergleicht
> dokumentenbasiertes Retrieval mit einem graphbasierten Retrieval. Die
> bisherigen Ergebnisse sind nur vorlaeufig, zeigen aber, dass der
> graphbasierte Ansatz besonders bei Fragen mit Beziehungen zwischen Problem,
> Komponente, Ursache und Loesung interessant ist.

## Offene Punkte bis zum Treffen

- Classic RAG technisch verbessern, zum Beispiel mit Embeddings statt nur
  lexikalischer Suche.
- LightRAG genauer recherchieren und entscheiden, wie es praktisch integriert
  wird.
- Bewertungsrubrik finalisieren.
- Zwei bis drei Beispielantworten fuer die Praesentation auswaehlen.
- Forschungsfrage gemeinsam mit der Professorin final schaerfen.
