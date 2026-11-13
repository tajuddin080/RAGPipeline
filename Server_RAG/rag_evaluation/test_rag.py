import asyncio


TEST_QUESTIONS = [
    {
        "question": (
            "What is the maximum domestic flight reimbursement, and who approves "
            "travel requests that exceed the policy limits?"
        ),
        "source": "financial_policy.txt",
        "expected_output": (
            "The maximum domestic flight reimbursement is INR 25,000. Travel requests "
            "above the policy limits require Finance Director approval."
        ),
    },
    {
        "question": (
            "How many goals should an employee set during each review cycle, "
            "and what framework should those goals follow?"
        ),
        "source": "hr_policy.md",
        "expected_output": (
            "Employees should set 3 to 7 goals per review cycle using the SMART "
            "framework: Specific, Measurable, Achievable, Relevant, and Time-bound."
        ),
    },
    {
        "question": (
            "From the onboarding policy, return a Markdown table with the item "
            "and lead time required for the Payroll profile."
        ),
        "source": "onboarding_policy.pdf",
        "expected_output": (
            "| Item | Responsible team | Lead time required |\n"
            "|---|---|---|\n"
            "| Payroll profile created | Payroll | 7 business days |"
        ),
    },
    {
        "question": "What is the employee notice period for a Grade G4 employee?",
        "source": "resignation_policy.pdf",
        "expected_output": (
            "A Grade G4 employee has a 60-day employee notice period."
        ),
    },
    {
        "question": "How long does HR have to communicate a grievance resolution?",
        "source": "hr_policy.md",
        "expected_output": (
            "HR communicates the grievance resolution within 20 working days."
        ),
    },
]


async def collect_test_cases():
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        ContextualRelevancyMetric,
        FaithfulnessMetric,
        GEval,
    )
    from deepeval.models import GeminiModel
    from deepeval.test_case import LLMTestCase, SingleTurnParams

    from app.rag.rag_task_query import rag_pipeline
    from app.utillities.utils import get_gemini_model

    gemini_model = get_gemini_model()
    judge = GeminiModel(
        model=gemini_model.model.removeprefix("models/"),
        api_key=gemini_model.google_api_key.get_secret_value(),
    )
    metrics = [
        AnswerRelevancyMetric(model=judge),
        FaithfulnessMetric(model=judge),
        ContextualRelevancyMetric(model=judge),
        GEval(
            name="Answer semantic similarity",
            criteria=(
                "Compare actual_output with expected_output for semantic "
                "equivalence. Reward answers that preserve the key facts and "
                "penalize missing or incorrect facts. Do not require identical "
                "wording. For the table question, compare the values and meaning."
            ),
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
            model=judge,
        ),
    ]

    test_cases = []
    for test in TEST_QUESTIONS:
        result = await rag_pipeline(test["question"])
        print(f"\nQuestion: {test['question']}")
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

    return test_cases, metrics


if __name__ == "__main__":
    test_cases, metrics = asyncio.run(collect_test_cases())
    for index, test_case in enumerate(test_cases, start=1):
        print(f"\nEvaluating test case {index}/{len(test_cases)}")
        for metric in metrics:
            metric.measure(test_case)
            print(
                f"{metric.__class__.__name__}: "
                f"{metric.score:.2f} - {metric.reason}"
            )
