# Methodology and reproducibility record

## Controlled comparison

Classic RAG and GraphRAG receive the same questions and use knowledge derived from the same twelve official Docker documentation sources. The implementation isolates retrieval behaviour: candidate answers are deterministic compositions of retrieved evidence, not LLM generations.

## Questions and reference answers

The author derived troubleshooting cases from the selected documentation and organised them into six categories. The main set contains 48 questions, the challenge set 12 more demanding questions and the holdout set 12 questions not used during initial development.

The author wrote each reference answer from the source assigned to the question. Every record has `reference_answer`, `must_include` and `scoring_focus`. References were fixed before final evaluation and checked one-to-one against question IDs. No independent second Docker expert reviewed them; this limits construct validity.

## Retrieval methods

Classic RAG applies lexical overlap scoring to document chunks. GraphRAG identifies entry nodes and traverses typed relations among problems, components, causes, diagnostics, solutions and sources. Both return evidence with source identifiers.

## Automated and manual evaluation

The final evaluator used RAGChecker 0.1.9 through OpenAI client 2.54.0 with `gpt-4.1-mini`. It requested `overall_metrics`, used extractor/checker batch size 1, a 90-second timeout and maximum evaluator output of 600 tokens. No temperature parameter was set explicitly.

A small stratified qualitative sample checks correctness, completeness, traceability and required causal steps. It supports interpretation; it does not replace the full automated evaluation.

## Cost

`cost = input_tokens / 1,000,000 * input_price + output_tokens / 1,000,000 * output_price`

The main evaluation uses USD 0.40 per million input tokens and USD 1.60 per million output tokens. Exact counts and repair-run accounting are stored in `results/final/evaluation_metadata.json`.

