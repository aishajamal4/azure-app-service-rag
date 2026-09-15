# RAG-Based GenAI Agent

A Retrieval-Augmented Generation (RAG) based GenAI Agent developed as part of my **GenAI training at Watira**.

The project is designed to answer user questions based on a set of Word documents while using conversation history to maintain context across multiple interactions.

##  Project Overview

The agent combines **Azure AI Search** for document retrieval with **Azure OpenAI** for answer generation.

Instead of relying only on the LLM's knowledge, the system retrieves relevant information from the provided documents and uses it as context to generate grounded answers.

The project was also enhanced with **conversation history and context awareness**, allowing the agent to handle follow-up questions without requiring the user to repeat previous information.

##  Architecture

```text
Word Documents
      ↓
Azure AI Search
(Semantic / Hybrid Retrieval)
      ↓
Retrieved Context
      ↓
Azure OpenAI
      ↑
Conversation History
      ↓
Generated Answer
      ↓
Flask API
      ↓
Chat UI
```

## ✨ Main Features

*  **Document-based Question Answering**
*  **Semantic / Hybrid Search** using Azure AI Search
*  **Answer Generation** using Azure OpenAI
*  **Conversation History & Context Awareness**
*  **Separate conversation context per user/session**
*  **Follow-up question support**
*  **Flask REST API**
*  **RAG Evaluation using LLM-as-a-Judge**

##  How It Works

1. Word documents are processed and indexed in **Azure AI Search**.
2. The user sends a question through the chat interface.
3. The Flask backend processes the request.
4. Relevant conversation history is considered to understand the current context.
5. Azure AI Search retrieves relevant document content.
6. The retrieved context and conversation context are provided to **Azure OpenAI**.
7. The LLM generates a grounded answer.
8. The answer is returned to the user through the Flask API.

##  RAG Evaluation

The system was evaluated using an **LLM-as-a-Judge** approach.

The evaluation dataset contains **70 questions**, and the generated responses were evaluated using three metrics:

| Metric            |     Score |
| ----------------- | --------: |
| Faithfulness      | **94.3%** |
| Answer Relevance  | **90.3%** |
| Context Relevance | **92.3%** |

### Evaluation Metrics

* **Faithfulness:** Measures whether the generated answer is supported by the retrieved context.
* **Answer Relevance:** Measures whether the answer directly addresses the user's question.
* **Context Relevance:** Measures whether the retrieved context is relevant to the question.

## 🛠️ Technologies

* **Azure AI Search**
* **Azure OpenAI**
* **Flask**
* **Python**
* **RAG**
* **LLM-as-a-Judge**
* **Semantic / Hybrid Search**

## 📌 Project Status

The project is **still under development**.

Future improvements will focus on improving retrieval quality, conversation context handling, reliability, and overall RAG performance.

## 👩‍💻 Author

**Aisha Bani-Amer**

Computer Science Graduate | AI & ML | GenAI | RAG

---

*Developed as part of my GenAI training journey at Watira.*
