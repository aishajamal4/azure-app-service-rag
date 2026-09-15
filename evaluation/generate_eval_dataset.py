import json
from app import ConversationalRAG


INPUT_FILE = "questions.json"
OUTPUT_FILE = "rag_eval_dataset.json"


def load_questions(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_dataset():
    # Create RAG application
    rag = ConversationalRAG()

    # Load questions
    questions = load_questions(INPUT_FILE)

    dataset = []

    #print("=" * 70)
    print("GENERATING RAG EVALUATION DATASET")
    #print("=" * 70)

    for index, item in enumerate(questions, start=1):

        question = item["question"]

        print(f"\n[{index}/{len(questions)}]")
        print(f"Question: {question}")

        try:
            # 1. Retrieve documents ---------------------------------------

            retrieved = rag.retrieve(
                question,
                limit=5
            )

            # 2. Build context ---------------------------------------

            context = rag.make_context(retrieved)

            # 3. Generate answer ---------------------------------------

            answer = rag.answer_question(
                question,
                context
            )

            # 4. Save evaluation sample ---------------------------------------
]
            sample = {
                "question": question,
                "answer": answer,
                "contexts": retrieved
            }

            dataset.append(sample)

            print("Retrieved:", len(retrieved))
            print("Answer:", answer)

        except Exception as error:

            print("ERROR:", error)

            sample = {
                "question": question,
                "answer": None,
                "contexts": [],
                "error": str(error)
            }

            dataset.append(sample)

    # Save dataset---------------------------------------


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dataset,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 70)
    print("DATASET GENERATED")
    #print("=" * 70)
    print(f"Questions: {len(questions)}")
    print(f"Output: {OUTPUT_FILE}")
    #print("=" * 70)


if __name__ == "__main__":
    generate_dataset()
