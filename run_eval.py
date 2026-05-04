"""
Headless evaluation gate for CI (Lab 10).

- Loads thresholds from eval_threshold_config.json (or EVAL_THRESHOLD_CONFIG_PATH).
- Runs the same scoring pipeline as Lab 7 (evaluate_agent.run_evaluation).
- Exits 0 when all averages meet thresholds, else 1.

Environment (works locally with .env and in GitHub Actions with secrets):
  OPENAI_API_KEY   required
  EVAL_DATASET_PATH   optional override (default: test_dataset.json next to cwd)
  EVAL_THRESHOLD_CONFIG_PATH   optional override
  AUTO_APPROVE_REFUNDS   set to true by default here for non-interactive runs
"""
from __future__ import annotations

import json
import os
import sys


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)

    os.environ.setdefault("AUTO_APPROVE_REFUNDS", "true")
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")

    # Import after env so subgraphs behave in headless CI
    from dotenv import load_dotenv

    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    dataset_rel = os.environ.get("EVAL_DATASET_PATH", "test_dataset.json")
    threshold_rel = os.environ.get("EVAL_THRESHOLD_CONFIG_PATH", "eval_threshold_config.json")
    dataset_path = dataset_rel if os.path.isabs(dataset_rel) else os.path.join(root, dataset_rel)
    threshold_path = (
        threshold_rel if os.path.isabs(threshold_rel) else os.path.join(root, threshold_rel)
    )

    if not os.path.isfile(dataset_path):
        print(f"ERROR: dataset not found: {dataset_path}", file=sys.stderr)
        return 1
    if not os.path.isfile(threshold_path):
        print(f"ERROR: threshold config not found: {threshold_path}", file=sys.stderr)
        return 1

    with open(threshold_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    min_faith = float(cfg["min_faithfulness"])
    min_rel = float(cfg["min_relevancy"])
    min_tool = float(cfg["min_tool_call_accuracy"])

    from evaluate_agent import run_evaluation, write_reports

    print(f"Running evaluation on {dataset_path} ...")
    result = run_evaluation(dataset_path)
    write_reports(result)

    f_avg = float(result["average_faithfulness"])
    r_avg = float(result["average_relevancy"])
    t_avg = float(result["average_tool_call_accuracy"])

    print(
        json.dumps(
            {
                "average_faithfulness": f_avg,
                "average_relevancy": r_avg,
                "average_tool_call_accuracy": t_avg,
                "cases_evaluated": result["cases_evaluated"],
            },
            indent=2,
        )
    )
    summary = (
        f"Faithfulness={f_avg} (min {min_faith}) | "
        f"Relevancy={r_avg} (min {min_rel}) | "
        f"ToolAcc={t_avg} (min {min_tool})"
    )
    print(summary)

    failed: list[str] = []
    if f_avg < min_faith:
        failed.append("faithfulness")
    if r_avg < min_rel:
        failed.append("relevancy")
    if t_avg < min_tool:
        failed.append("tool_call_accuracy")

    if failed:
        print(f"EVAL GATE FAILED below threshold: {', '.join(failed)}", file=sys.stderr)
        return 1

    print("EVAL GATE PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
