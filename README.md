# Classic RAG vs GraphRAG for Docker Troubleshooting

Companion repository for the bachelor thesis:

> **Vergleich von klassischem RAG und GraphRAG bei relationalen und komplexen Troubleshooting-Fragen in technischer Dokumentation am Beispiel der Docker-Dokumentation**

This project examines when graph-based retrieval improves technical troubleshooting compared with classic document retrieval. Both approaches use the same curated Docker and Docker Compose knowledge base and receive the same questions.

## Research question

To what extent does GraphRAG improve retrieval and answer quality for relational and complex troubleshooting questions in technical documentation compared with classic RAG?

The comparison isolates retrieval and evidence composition. Candidate answers are generated deterministically from retrieved evidence. The OpenAI model is used only by RAGChecker as evaluator.

## Experimental design

- **Classic RAG:** lexical scoring over document chunks.
- **GraphRAG:** traversal over explicit problem, component, cause, diagnostic, solution and source relations.
- **Main set:** 48 questions, eight per category.
- **Challenge set:** 12 difficult questions, two per category.
- **Holdout set:** 12 additional questions not used during initial development.
- **Six categories:** simple factual, procedural, configuration conflict, relational troubleshooting, multi-hop and traceability.
- **Knowledge graph:** 94 nodes and 119 directed relations.
- **Sources:** 12 official Docker documentation pages.

## Results

| Set | Classic F1 | Graph F1 | Interpretation |
| --- | ---: | ---: | --- |
| Main, 48 questions | 35.2 | 32.7 | Classic RAG has higher precision and F1; GraphRAG has higher recall. |
| Challenge, 12 questions | 52.8 | 44.5 | GraphRAG leads only in relational and traceability questions. |
| Holdout, 12 questions | 37.5 | 34.7 | Classic RAG has a small F1 lead; GraphRAG has clearly higher recall. |

The evidence does not support universal superiority. Explicit relations help most when a question requires causal chains, multiple linked entities or traceable evidence. Classic retrieval can be more precise for direct, self-contained facts.

## Structure

```text
data/               Sources, graph, questions and reference answers
docs/               Methodology, experiment notes and dashboards
results/final/       Curated reproducibility outputs
src/rag_compare/     Retrieval and comparison implementation
tests/               Automated retrieval tests
tools/               Evaluation, analysis and validation scripts
run.ps1              Windows entry point
```

## Installation and local reproduction

Python 3.11 or newer is required.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
.\run.ps1 validate
.\run.ps1 compare
.\run.ps1 test
.\run.ps1 release-check
```

Optional evaluator dependencies:

```powershell
python -m pip install -e ".[evaluation]"
```

Copy `.env.example` to `.env.local` and add an API key only when RAGChecker must be rerun. Never commit that file.

Example queries:

```powershell
.\run.ps1 query --method classic --question "Why can my app container not reach the database container by service name?"
.\run.ps1 query --method graph --question "Why can my app container not reach the database container by service name?"
```

## Evaluation configuration

The final evaluation used RAGChecker `0.1.9`, OpenAI client `2.54.0`, evaluator model `gpt-4.1-mini`, `overall_metrics`, extractor/checker batch size `1`, a 90-second timeout and maximum output of 600 tokens. Main-set evaluator cost was approximately **USD 0.1539**, including a repair run for incomplete classic-RAG records.

Reference answers were written by the thesis author from the assigned official Docker sources before final evaluation. Each includes mandatory concepts and a scoring focus. Automated checks enforce one-to-one coverage, but no independent second expert reviewed them.

## Limitations

This is a controlled case study, not a general benchmark. Limitations include the small curated domain, lexical classic-RAG baseline, manually modelled graph, author-created references, limited manual sample and LLM-based evaluation variability.

No API keys or personal data are included in this repository.

