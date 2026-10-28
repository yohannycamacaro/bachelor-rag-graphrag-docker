from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from ragchecker import RAGChecker, RAGResults


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run RAGChecker through the official OpenAI Python client."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--metrics", default="overall_metrics")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--max-output-tokens", type=int, default=600)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env.local")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is missing from .env.local")

    client = OpenAI(timeout=args.timeout, max_retries=1)
    usage = {"input_tokens": 0, "output_tokens": 0, "requests": 0}

    def invoke(prompts: list[str]) -> list[str]:
        responses: list[str] = []
        for prompt in prompts:
            result = client.responses.create(
                model=args.model,
                input=prompt,
                max_output_tokens=args.max_output_tokens,
            )
            usage["requests"] += 1
            if result.usage is not None:
                usage["input_tokens"] += result.usage.input_tokens
                usage["output_tokens"] += result.usage.output_tokens
            responses.append(result.output_text)
        return responses

    rag_results = RAGResults.from_json(args.input.read_text(encoding="utf-8"))
    evaluator = RAGChecker(
        custom_llm_api_func=invoke,
        batch_size_extractor=1,
        batch_size_checker=1,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    metrics = evaluator.evaluate(
        rag_results,
        metrics=args.metrics,
        save_path=str(args.output),
    )
    estimated_cost = None
    print(metrics)
    print(
        "Usage: "
        f"requests={usage['requests']}, "
        f"input_tokens={usage['input_tokens']}, "
        f"output_tokens={usage['output_tokens']}"
    )
    if args.model == "gpt-4.1-mini":
        estimated_cost = (
            usage["input_tokens"] * 0.40 / 1_000_000
            + usage["output_tokens"] * 1.60 / 1_000_000
        )
        print(f"Estimated OpenAI cost: ${estimated_cost:.4f}")
    saved = json.loads(args.output.read_text(encoding="utf-8"))
    saved["evaluation_metadata"] = {
        "model": args.model,
        "metric_group": args.metrics,
        "requests": usage["requests"],
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "estimated_openai_cost_usd": estimated_cost,
    }
    args.output.write_text(
        json.dumps(saved, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
