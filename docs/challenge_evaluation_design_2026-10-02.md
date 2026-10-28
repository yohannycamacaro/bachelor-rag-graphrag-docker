# Erweiterte Evaluation nach dem Betreuungsgespraech

Stand: 02.10.2026

## Ziel

Die bisherige Baseline mit 48 Fragen bleibt unveraendert. Zusaetzlich wird ein
separates Challenge-Set verwendet, um Unterschiede zwischen Classic RAG und
GraphRAG bei anspruchsvolleren Fragen sichtbarer zu machen.

## Aufbau

- 12 neue Fragen;
- 2 Fragen pro bestehender Kategorie;
- hoehere erwartete Relationstiefe;
- dieselbe Docker-Compose-Wissensbasis fuer beide Methoden;
- eigene Referenzantworten und Mindestinhalte;
- getrennte Ergebnisdateien, damit die urspruengliche Evaluation reproduzierbar
  bleibt.

## Auswertung pro Kategorie

Fuer jede der sechs Kategorien werden Classic RAG und GraphRAG mit denselben
Fragen verglichen. Die automatische Auswertung umfasst Precision, Recall und F1
mit RAGChecker. Ergaenzend werden konkrete Antwortpaare qualitativ betrachtet.

## Beispiele fuer die Abschlussprasentation

Der Experimentlauf erzeugt zunaechst ein Antwortpaar pro Kategorie. Nach der
RAGChecker-Auswertung werden zwei besonders anschauliche Beispiele ausgewaehlt:

1. ein Fall, in dem GraphRAG durch explizite Beziehungen einen klaren Vorteil
   zeigt;
2. ein Fall, in dem Classic RAG kompakter oder praeziser bleibt.

Damit zeigt die Praesentation nicht nur aggregierte Zahlen, sondern auch, wie
sich die Methoden bei einer konkreten technischen Frage unterscheiden.
