Betreff: Aktueller Arbeitsstand zur Bachelorarbeit

Sehr geehrte Frau Prof. Kastsian,
sehr geehrter Herr Prof. Kitzelmann,

ich möchte Ihnen gerne einen kurzen aktuellen Arbeitsstand zu meiner geplanten
Bachelorarbeit schicken.

Nach unserem letzten Gespräch habe ich das Thema weiter konkretisiert. Der
aktuelle Arbeitstitel lautet:

"Vergleich von klassischem RAG und GraphRAG bei relationalen und komplexen
Troubleshooting-Fragen in technischer Dokumentation anhand einer kontrollierten
Docker-Compose-Wissensbasis."

Die Forschungsfrage habe ich aktuell wie folgt formuliert:

"Inwieweit verbessert GraphRAG gegenüber klassischem RAG die Antwortqualität
bei technischen Troubleshooting-Fragen, die relationale Zusammenhänge zwischen
Problem, Komponente, Ursache, Diagnose und Lösung erfordern?"

Ich habe inzwischen einen ersten kontrollierten Prototyp aufgebaut. Dieser
enthält aktuell 12 Docker-Dokumentationsquellen, 23 technische
Troubleshooting-Fälle, 48 Testfragen in sechs ausgeglichenen Kategorien sowie
einen Wissensgraphen mit 94 Knoten und 119 Relationen. Die Fragen wurden
manuell aus typischen Troubleshooting-Situationen der offiziellen
Docker-Dokumentation abgeleitet.

Eine erste retrieval-basierte Voranalyse zeigt bisher, dass der graphbasierte
Ansatz vor allem bei relationalen Troubleshooting-Fragen,
Nachvollziehbarkeitsfragen und Multi-Hop-Fragen Vorteile gegenüber dem
klassischen Ansatz zeigt. Bei prozeduralen Fragen und Konfigurationskonflikten
ist der Unterschied aktuell deutlich kleiner. Ich verstehe diese Ergebnisse
noch nicht als finale Evaluation, sondern als Zwischenschritt für die weitere
Ausarbeitung.

Als nächste Schritte möchte ich die Literaturrecherche zu RAG, GraphRAG,
LightRAG und RAG-Evaluation weiter vertiefen, Referenzantworten für den
Fragenkatalog erstellen und die finale Bewertungsmethode festlegen.

Ich wäre Ihnen sehr dankbar für eine kurze Rückmeldung, ob diese
Konkretisierung der Forschungsfrage und des Anwendungsfalls aus Ihrer Sicht in
die richtige Richtung geht. Besonders offen ist für mich noch, ob der Fokus
eher auf dem kontrollierten Vergleich des eigenen Prototyps liegen sollte oder
ob zusätzlich ein bestehendes Framework wie LightRAG integriert werden sollte.

Mit freundlichen Grüßen
Yohanny Camacaro
