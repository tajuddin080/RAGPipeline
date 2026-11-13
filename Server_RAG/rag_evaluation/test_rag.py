import asyncio
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.genai.errors import APIError
from rag_evaluation.rag_test_cases import TEST_CASES


RESULTS_FILE = Path(__file__).with_name("results.csv")
RESULT_FIELDS = [
    "run_id",
    "evaluated_at",
    "test_id",
    "difficulty",
    "source",
    "question",
    "expected_output",
    "actual_output",
    "metric",
    "status",
    "score",
    "reason",
]


def create_metrics():
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        ContextualRecallMetric,
        ContextualRelevancyMetric,
        FaithfulnessMetric,
    )
    from deepeval.models import GeminiModel

    from app.utillities.utils import get_gemini_model

    gemini_model = get_gemini_model()
    judge = GeminiModel(
        model=gemini_model.model.removeprefix("models/"),
        api_key=gemini_model.google_api_key.get_secret_value(),
    )
    return [
        AnswerRelevancyMetric(model=judge, async_mode=False),
        FaithfulnessMetric(model=judge, async_mode=False),
        ContextualRelevancyMetric(model=judge, async_mode=False),
        ContextualRecallMetric(model=judge, async_mode=False),
    ]


async def collect_test_cases():
    from deepeval.test_case import LLMTestCase

    from app.rag.rag_task_query import rag_pipeline

    test_cases = []
    for test in TEST_CASES:
        result = await rag_pipeline(test["question"])
        print(f"\n[{test['id']} - {test['difficulty']}] {test['question']}")
        print(f"Expected source: {test['source']}")
        print(f"Retrieved sources: {result['sources']}")
        print(f"Answer:\n{result['answer']}")

        test_cases.append(
            LLMTestCase(
                input=test["question"],
                actual_output=result["answer"],
                expected_output=test["expected_output"],
                retrieval_context=result["context"],
            )
        )

    return test_cases


def save_metric_result(run_id, test, test_case, metric, error=None):
    status = "api_error" if error else "success"
    reason = (
        f"{type(error).__name__} ({error.code}): {error.message}"
        if error
        else metric.reason or ""
    )
    row = {
        "run_id": run_id,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "test_id": test["id"],
        "difficulty": test["difficulty"],
        "source": test["source"],
        "question": test["question"],
        "expected_output": test["expected_output"],
        "actual_output": test_case.actual_output,
        "metric": metric.__class__.__name__,
        "status": status,
        "score": "" if error else metric.score,
        "reason": reason,
    }

    write_header = not RESULTS_FILE.exists() or RESULTS_FILE.stat().st_size == 0
    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as results_file:
        writer = csv.DictWriter(results_file, fieldnames=RESULT_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def evaluate_test_cases(test_cases, metrics):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    print(f"\nAppending each metric result to: {RESULTS_FILE}")

    for case_index, (test, test_case) in enumerate(
        zip(TEST_CASES, test_cases), start=1
    ):
        scores = []
        print(f"\nEvaluating {test['id']} ({case_index}/{len(test_cases)})")
        for metric in metrics:
            try:
                metric.measure(test_case)
            except APIError as error:
                scores.append(None)
                save_metric_result(run_id, test, test_case, metric, error)
                print(
                    f"{metric.__class__.__name__}: API error {error.code} - "
                    f"{error.message}",
                    flush=True,
                )
            else:
                scores.append(metric.score)
                save_metric_result(run_id, test, test_case, metric)
                print(
                    f"{metric.__class__.__name__}: {metric.score:.2f} "
                    f"- {metric.reason}",
                    flush=True,
                )
        results.append((test, scores))

    metric_names = [metric.__class__.__name__ for metric in metrics]
    print(
        "\n| ID | Level | Test question | "
        + " | ".join(metric_names)
        + " |"
    )
    print("|---|---|---|" + "---:|" * len(metric_names))
    for test, scores in results:
        question = test["question"].replace("|", "\\|").replace("\n", " ")
        score_text = " | ".join(
            "API_ERROR" if score is None else f"{score:.2f}"
            for score in scores
        )
        print(
            f"| {test['id']} | {test['difficulty']} | {question} | {score_text} |"
        )

    return results


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    metrics = create_metrics()
    test_cases = asyncio.run(collect_test_cases())
    evaluate_test_cases(test_cases, metrics)


if __name__ == "__main__":
    main()
