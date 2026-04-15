from __future__ import annotations

import json
import os
from dataclasses import dataclass
from statistics import mean
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from secured_graph import run_secured_once

load_dotenv()


@dataclass
class EvalRow:
    case_id: int
    query: str
    ground_truth: str
    answer: str
    faithfulness: float
    relevancy: float
    tool_call_accuracy: float


def llm_score(
    judge: ChatOpenAI,
    query: str,
    ground_truth: str,
    answer: str,
    metric_name: str,
    rubric: str,
) -> float:
    prompt = f"""
You are an evaluator. Score the metric from 0 to 1.
Metric: {metric_name}
Rubric: {rubric}

Query:
{query}

Reference:
{ground_truth}

Model Answer:
{answer}

Return only a float between 0 and 1.
"""
    raw = judge.invoke(prompt).content.strip()
    try:
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        return 0.0


def infer_tool_call_accuracy(query: str, answer: str) -> float:
    """
    Lightweight proxy when explicit trace tool logs are unavailable.
    """
    q = query.lower()
    a = answer.lower()

    if "shipping" in q and ("status" in a or "warehouse" in a):
        return 1.0
    if ("order" in q or "details" in q) and "ord-" in a:
        return 1.0
    if "refund" in q and ("refund" in a or "approval" in a):
        return 1.0
    return 0.5


def run_evaluation(dataset_path: str = "test_dataset.json") -> dict[str, Any]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    rows: list[EvalRow] = []

    for item in dataset:
        case_id = int(item["id"])
        query = str(item["query"])
        ground_truth = str(item["ground_truth"])
        answer = run_secured_once(query, thread_id=f"eval_case_{case_id}")

        faithfulness = llm_score(
            judge,
            query,
            ground_truth,
            answer,
            "Faithfulness",
            "1.0 if answer is fully grounded and does not invent facts.",
        )
        relevancy = llm_score(
            judge,
            query,
            ground_truth,
            answer,
            "Answer Relevancy",
            "1.0 if answer directly addresses user query clearly.",
        )
        tool_acc = infer_tool_call_accuracy(query, answer)

        rows.append(
            EvalRow(
                case_id=case_id,
                query=query,
                ground_truth=ground_truth,
                answer=answer,
                faithfulness=faithfulness,
                relevancy=relevancy,
                tool_call_accuracy=tool_acc,
            )
        )

    result = {
        "average_faithfulness": round(mean(r.faithfulness for r in rows), 3),
        "average_relevancy": round(mean(r.relevancy for r in rows), 3),
        "average_tool_call_accuracy": round(mean(r.tool_call_accuracy for r in rows), 3),
        "cases_evaluated": len(rows),
        "rows": [r.__dict__ for r in rows],
    }
    return result


def write_reports(result: dict[str, Any]) -> None:
    os.makedirs("reports", exist_ok=True)

    with open("reports/evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    md = f"""# Evaluation Report

| Metric | Score |
|---|---:|
| Average Faithfulness | {result["average_faithfulness"]} |
| Average Relevancy | {result["average_relevancy"]} |
| Average Tool Call Accuracy | {result["average_tool_call_accuracy"]} |
| Cases Evaluated | {result["cases_evaluated"]} |
"""
    with open("evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    evaluation = run_evaluation("test_dataset.json")
    write_reports(evaluation)
    print("Evaluation complete. Outputs:")
    print("- reports/evaluation_results.json")
    print("- evaluation_report.md")
