from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from evaluate_agent import run_evaluation, write_reports
from secured_graph import secured_app


def run_trace_bottleneck_analysis(queries: list[str]) -> dict[str, Any]:
    os.environ["AUTO_APPROVE_REFUNDS"] = "true"
    node_durations: dict[str, list[float]] = defaultdict(list)
    trace_rows: list[dict[str, Any]] = []

    for idx, query in enumerate(queries, start=1):
        config = {"configurable": {"thread_id": f"trace_case_{idx}"}}
        state = {"messages": [HumanMessage(content=query)]}
        last_time = time.perf_counter()

        try:
            for step in secured_app.stream(state, config=config, stream_mode="updates"):
                now = time.perf_counter()
                elapsed = now - last_time
                last_time = now

                node_name = next(iter(step.keys()))
                node_durations[node_name].append(elapsed)

                trace_rows.append(
                    {
                        "query_id": idx,
                        "query": query,
                        "node": node_name,
                        "elapsed_seconds": round(elapsed, 4),
                    }
                )
        except Exception as exc:
            trace_rows.append(
                {
                    "query_id": idx,
                    "query": query,
                    "node": "error",
                    "elapsed_seconds": 0.0,
                    "error": str(exc),
                }
            )

    avg_by_node = {
        node: round(sum(times) / len(times), 4)
        for node, times in node_durations.items()
        if times
    }

    slowest_node = "unknown"
    slowest_value = 0.0
    if avg_by_node:
        slowest_node = max(avg_by_node, key=avg_by_node.get)
        slowest_value = avg_by_node[slowest_node]

    return {
        "avg_node_latency_seconds": avg_by_node,
        "slowest_node": slowest_node,
        "slowest_avg_seconds": slowest_value,
        "trace_rows": trace_rows,
    }


def write_observability_files(trace_result: dict[str, Any]) -> None:
    langsmith_project = os.getenv("LANGSMITH_PROJECT", "capstonelab-diagnostics")
    has_langsmith = bool(os.getenv("LANGSMITH_API_KEY"))

    if has_langsmith:
        link_text = (
            "LangSmith tracing is enabled for this run.\n"
            f"Project: {langsmith_project}\n"
            "Open your LangSmith dashboard and share the project URL."
        )
    else:
        link_text = (
            "LangSmith API key was not detected in environment.\n"
            "Set LANGSMITH_API_KEY and rerun lab7_diagnostics.py to publish traces.\n"
            f"Suggested project name: {langsmith_project}"
        )

    with open("observability_link.txt", "w", encoding="utf-8") as f:
        f.write(link_text)

    slowest_node = trace_result["slowest_node"]
    slowest_avg = trace_result["slowest_avg_seconds"]
    bottleneck = (
        f"Trace analysis across 5 complex queries shows `{slowest_node}` as the slowest "
        f"node with an average latency of about {slowest_avg} seconds per execution. "
        "This suggests most runtime is spent in LLM reasoning/tool orchestration for that stage. "
        "A practical fix is to reduce token load (shorter prompts and retrieved context), cache "
        "repeat tool lookups (policy/search/order calls), and only invoke high-cost nodes when "
        "routing confidence is low."
    )
    with open("bottleneck_analysis.txt", "w", encoding="utf-8") as f:
        f.write(bottleneck)

    with open("reports/trace_analysis.json", "w", encoding="utf-8") as f:
        json.dump(trace_result, f, indent=2)


def main() -> None:
    load_dotenv()
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ.setdefault("LANGSMITH_PROJECT", "capstonelab-diagnostics")
    os.environ["AUTO_APPROVE_REFUNDS"] = "true"

    evaluation = run_evaluation("test_dataset.json")
    write_reports(evaluation)

    complex_queries = [
        "Refund order 1012 if policy allows and explain why.",
        "Give details and shipping status for order 1011.",
        "What are shipping priority rules and refund constraints for standard users?",
        "Track shipping for order 1015 and order 1016.",
        "Can you process refund for order 1004 right now?",
    ]
    trace_result = run_trace_bottleneck_analysis(complex_queries)
    write_observability_files(trace_result)

    print("Lab 7 artifacts generated:")
    print("- test_dataset.json")
    print("- evaluation_report.md")
    print("- observability_link.txt")
    print("- bottleneck_analysis.txt")
    print("- reports/evaluation_results.json")
    print("- reports/trace_analysis.json")


if __name__ == "__main__":
    main()
