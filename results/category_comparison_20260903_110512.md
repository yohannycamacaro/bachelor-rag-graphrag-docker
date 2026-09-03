# Category comparison: Classic RAG vs GraphRAG

This report groups the experiment by question category. It is an automatic retrieval-level comparison, not yet a final LLM-based evaluation.

| Category | n | Avg. hops | Classic keyword | Graph keyword | Delta | Classic source | Graph source |
|---|---:|---:|---:|---:|---:|---:|---:|
| Konfigurationskonflikt | 6 | 3.00 | 0.442 | 0.567 | 0.125 | 1.000 | 0.833 |
| Einfache Faktenfrage | 6 | 1.00 | 0.500 | 0.611 | 0.111 | 0.917 | 0.833 |
| Multi-Hop-Frage | 6 | 4.00 | 0.167 | 0.458 | 0.292 | 1.000 | 0.833 |
| Prozedurale Frage | 4 | 1.75 | 0.542 | 0.604 | 0.062 | 1.000 | 1.000 |
| Relationale Troubleshooting-Frage | 5 | 2.80 | 0.300 | 0.750 | 0.450 | 1.000 | 1.000 |
| Nachvollziehbarkeit | 3 | 2.67 | 0.333 | 0.750 | 0.417 | 1.000 | 1.000 |

## Interpretation draft

A positive delta means that the graph-based retrieval covered more expected keywords than the classic text-chunk baseline in this question category. For the final thesis, these automatic values should be complemented with manual ratings for correctness, completeness, traceability and consistency.
