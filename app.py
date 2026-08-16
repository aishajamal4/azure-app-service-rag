import os

from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

app = Flask(__name__)


# =========================
# Environment Variables
# =========================

SEARCH_ENDPOINT = os.environ["https://aisearchtraining0.search.windows.net"]
SEARCH_KEY = os.environ["bJ1BbJLQbBGXk5ogvdirr6ipd1mbP6nwN0LMoeE4i7AzSeCpgZKJ"]
SEARCH_INDEX = os.environ["knowledgesource-1786729607752-index"]

OPENAI_ENDPOINT = os.environ["https://yabulibdeh-0030-resource.openai.azure.com/openai/v1"]
OPENAI_KEY = os.environ["5KWkkew2YJdtqcCbtUcay0wEdwKGJdctOKWHd44D2FCLNGI8bYs0JQQJ99CHACfhMk5XJ3w3AAAAACOGSj9m"]
OPENAI_DEPLOYMENT = os.environ["gpt-5.4-mini"]


# =========================
# Azure AI Search
# =========================

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY)
)


# =========================
# Azure OpenAI
# =========================

openai_client = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_KEY,
    api_version="2025-04-01-preview"
)


# =========================
# Test endpoint
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "RAG API is running"
    })


# =========================
# RAG endpoint
# =========================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({
            "error": "Please provide a question"
        }), 400

    question = data["question"]

    # Search Azure AI Search
    results = search_client.search(
        search_text=question,
        top=5
    )

    context_parts = []

    for result in results:
        content = result.get("content")

        if content:
            context_parts.append(content)

    context = "\n\n".join(context_parts)

    if not context:
        return jsonify({
            "answer": "I could not find relevant information in the documents."
        })

    # Send context to Azure OpenAI
    response = openai_client.chat.completions.create(
        model=OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": """
You are a RAG assistant.

Answer the user's question using ONLY the provided context.

If the answer is not contained in the context,
say that you don't know.

Do not make up information.
"""
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{question}
"""
            }
        ],
        temperature=0
    )

    answer = response.choices[0].message.content

    return jsonify({
        "question": question,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )