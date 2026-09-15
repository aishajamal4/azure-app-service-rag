import os
import json
from dotenv import load_dotenv
from openai import OpenAI


INPUT_FILE = "rag_eval_dataset.json"
OUTPUT_FILE = "rag_evaluation.json"


# Configuration ============================================


load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

AZURE_OPENAI_URL = (
    "https://openai-training.openai.azure.com/openai/v1/"
)


client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_URL
)


# Load Dataset ===========================================

def load_dataset(filename):

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# Build Context ===========================================

def build_context(contexts):

    sections = []

    for number, context in enumerate(
        contexts,
        start=1
    ):

        section = (
            f"SOURCE {number}\n"
            f"Document ID: {context.get('id', 'Unknown')}\n"
            f"Content:\n"
            f"{context.get('text', '')}\n"
            f"{'-' * 50}"
        )

        sections.append(section)

    return "\n\n".join(sections)


# ============================================================
# LLM Judge
# ============================================================

def evaluate_answer(question, answer, contexts):

    context_text = build_context(contexts)

    prompt = f"""
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.

Your job is to evaluate the quality of the generated answer using ONLY
the question, retrieved context, and answer provided below.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context_text}

GENERATED ANSWER:
{answer}


Evaluate the answer using these three criteria.

--------------------------------------------------
1. FAITHFULNESS
--------------------------------------------------

Does the generated answer contain claims that are supported by
the retrieved context?

Score from 1 to 5:

1 = The answer is completely unsupported or contradicts the context.
2 = Most of the answer is unsupported.
3 = Partially supported, but contains important unsupported claims.
4 = Mostly supported, with minor unsupported details.
5 = Fully supported by the retrieved context.


--------------------------------------------------
2. ANSWER RELEVANCE
--------------------------------------------------

Does the answer directly and appropriately answer the question?

Score from 1 to 5:

1 = Completely irrelevant.
2 = Mostly irrelevant or does not answer the question.
3 = Partially answers the question.
4 = Mostly answers the question with minor issues.
5 = Directly and completely answers the question.


--------------------------------------------------
3. CONTEXT RELEVANCE
--------------------------------------------------

Are the retrieved contexts relevant and useful for answering
the question?

Score from 1 to 5:

1 = The retrieved context is completely irrelevant.
2 = Mostly irrelevant.
3 = Some relevant information is present.
4 = Mostly relevant and useful.
5 = The retrieved context directly contains the information needed
    to answer the question.


IMPORTANT:

- Do not use outside knowledge.
- Judge only based on the provided context.
- Do not reward an answer for information that is not present
  in the retrieved context.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not include ```json.

Return exactly this structure:

{{
    "faithfulness": <1-5>,
    "answer_relevance": <1-5>,
    "context_relevance": <1-5>,
    "reason": "<short explanation>"
}}
"""

    response = client.responses.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result_text = response.output_text.strip()

    try:

        return json.loads(result_text)

    except json.JSONDecodeError:

        print("\nInvalid JSON returned by judge:")
        print(result_text)

        return {
            "faithfulness": None,
            "answer_relevance": None,
            "context_relevance": None,
            "reason": "Judge returned invalid JSON."
        }


# Main Evaluation===========================================

def evaluate_dataset():

    dataset = load_dataset(INPUT_FILE)

    results = []

    print("=" * 70)
    print("RAG EVALUATION")
    print("=" * 70)

    for index, item in enumerate(
        dataset,
        start=1
    ):

        question = item.get("question")
        answer = item.get("answer")
        contexts = item.get("contexts", [])

        print(
            f"\n[{index}/{len(dataset)}]"
        )

        print(
            f"Question: {question}"
        )

        if not answer:

            print("Skipping: no answer")

            continue

        try:

            evaluation = evaluate_answer(
                question=question,
                answer=answer,
                contexts=contexts
            )

            result = {
                "question": question,
                "answer": answer,
                "contexts": contexts,
                "evaluation": evaluation
            }

            results.append(result)

            print(
                "Faithfulness:",
                evaluation.get("faithfulness")
            )

            print(
                "Answer Relevance:",
                evaluation.get("answer_relevance")
            )

            print(
                "Context Relevance:",
                evaluation.get("context_relevance")
            )

            print(
                "Reason:",
                evaluation.get("reason")
            )

        except Exception as error:

            print("ERROR:")
            print(error)

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"Evaluated questions: {len(results)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    evaluate_dataset()
