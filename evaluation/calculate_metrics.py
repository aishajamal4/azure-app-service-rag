import json
from collections import Counter


INPUT_FILE = "rag_evaluation.json"


def load_results():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_scores(results, metric):

    scores = []

    for item in results:

        evaluation = item.get("evaluation", {})

        score = evaluation.get(metric)

        if isinstance(score, (int, float)):
            scores.append(score)

    return scores


def print_metric(name, scores):

    if not scores:
        print(f"\n{name}: No scores available")
        return

    average = sum(scores) / len(scores)

    percentage = (average / 5) * 100

    print("-" * 50)

    print(f"\n{name}")

    print(
        f"Average: {average:.2f} / 5"
    )

    print(
        f"Percentage: {percentage:.1f}%"
    )

    print("\nDistribution:")

    counter = Counter(scores)

    for score in range(1, 6):

        count = counter.get(score, 0)

        percentage_count = (
            count / len(scores) * 100
        )

        print(
            f"  {score}/5 : "
            f"{count} questions "
            f"({percentage_count:.1f}%)"
        )


def find_low_scores(results, metric, threshold=3):

    failures = []

    for item in results:

        evaluation = item.get("evaluation", {})

        score = evaluation.get(metric)

        if isinstance(score, (int, float)):

            if score <= threshold:

                failures.append({
                    "question": item.get("question"),
                    "answer": item.get("answer"),
                    "score": score,
                    "reason": evaluation.get("reason")
                })

    return failures


def main():

    results = load_results()

    print("=" * 70)
    print("RAG EVALUATION REPORT")
    print("=" * 70)

    print(
        f"\nTotal evaluated questions: {len(results)}"
    )

    metrics = [
        "faithfulness",
        "answer_relevance",
        "context_relevance"
    ]

    for metric in metrics:

        scores = get_scores(
            results,
            metric
        )

        pretty_name = metric.replace(
            "_",
            " "
        ).title()

        print_metric(
            pretty_name,
            scores
        )

    # Find problematic questions

    print("\n" + "=" * 70)
    print("LOW-SCORE CASES")
    print("=" * 70)

    for metric in metrics:

        pretty_name = metric.replace(
            "_",
            " "
        ).title()

        failures = find_low_scores(
            results,
            metric,
            threshold=3
        )

        print(
            f"\n{pretty_name}: "
            f"{len(failures)} problematic questions"
        )

        for index, failure in enumerate(
            failures[:10],
            start=1
        ):

            print(
                f"\n{index}. "
                f"Score: {failure['score']}/5"
            )

            print(
                f"Question: "
                f"{failure['question']}"
            )

            print(
                f"Reason: "
                f"{failure['reason']}"
            )

    #print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
