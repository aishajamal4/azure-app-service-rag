import os
from dotenv import load_dotenv

from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


class ConversationalRAG:
    """
    Conversational RAG application using:
    - Azure OpenAI
    - Azure AI Search
    - Conversation memory
    """

    def __init__(self):
        self._load_configuration()
        self._create_clients()

        self.history = []
        self.sources = []

    # Configuration =====================================================

    def _load_configuration(self):
        load_dotenv()

        self.openai_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        self.openai_url = (
            "https://openai-training.openai.azure.com/openai/v1/"
        )

        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    # Clients ==========================================


    def _create_clients(self):

        self.openai = OpenAI(
            api_key=self.openai_key,
            base_url=self.openai_url
        )

        self.search = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.search_key)
        )

    # Conversation Management =====================================


    def remember(self, role, text):

        self.history.append({
            "role": role,
            "content": text
        })

    def reset(self):

        self.history.clear()
        self.sources.clear()

    # Azure AI Search ======================================


    def retrieve(self, question, limit=5):

        search_results = self.search.search(
            search_text=question,
            top=limit,
            select=[
                "uid",
                "snippet_parent_id",
                "blob_url",
                "snippet"
            ]
        )

        output = []

        for item in search_results:

            output.append({
                "id": item.get("uid"),
                "parent_id": item.get("snippet_parent_id"),
                "url": item.get("blob_url"),
                "text": item.get("snippet")
            })

        return output

    # Context Builder ======================================

    def make_context(self, results):

        if len(results) == 0:
            return (
                "There are no relevant documents available "
                "in the knowledge base."
            )

        sections = []

        for number, item in enumerate(results, start=1):

            section = (
                f"SOURCE {number}\n"
                f"Document ID: {item.get('id') or 'Unknown'}\n"
                f"Parent Document ID: "
                f"{item.get('parent_id') or 'Unknown'}\n"
                f"Source: {item.get('url') or 'Unknown'}\n"
                f"Content:\n{item.get('text') or ''}\n"
                f"{'-' * 40}"
            )

            sections.append(section)

        return "\n\n".join(sections)

    # Prompt ======================================

    def build_instructions(self, context):

        return f"""
You are an enterprise conversational RAG assistant.

Answer the user's question based primarily on the
retrieved knowledge-base documents provided below.

Rules:

- Do not invent information.
- Do not rely on general knowledge for company-specific
  information.
- If the documents do not contain enough information,
  say:
  "I couldn't find this information in the available documents."
- Use conversation history when necessary to understand
  references such as "it", "this", "that", or "the previous
  document".
- Mention the relevant source when appropriate.
- Do not claim that you searched the internet.
- Keep your answer clear and concise.

Retrieved Knowledge:

==================================================
{context}
==================================================
"""

    # LLM Generation ======================================

    def answer_question(self, question, context):

        system_message = {
            "role": "system",
            "content": self.build_instructions(context)
        }

        messages = [system_message]

        messages.extend(self.history)

        messages.append({
            "role": "user",
            "content": question
        })

        result = self.openai.responses.create(
            model=self.deployment,
            input=messages
        )

        return result.output_text

    # Complete RAG Pipeline ======================================

    def ask(self, question):

        self.remember("user", question)

        try:

            retrieved = self.retrieve(question)

            self.sources = retrieved

            context = self.make_context(retrieved)

            response = self.answer_question(
                question,
                context
            )

            self.remember(
                "assistant",
                response
            )

            return response

        except Exception as error:

            if self.history:
                self.history.pop()

            print("\n" + "=" * 60)
            print("RAG ERROR")
            print("=" * 60)
            print(error)
            print("=" * 60)

            return None
        

    # Sources Display ======================================

    def print_sources(self):

        if not self.sources:
            print("\nNo sources were retrieved.")
            return

        print("\n" + "=" * 70)
        print("RETRIEVED SOURCES")
        print("=" * 70)

        for position, source in enumerate(
            self.sources,
            start=1
        ):

            print(f"\nSOURCE {position}")
            print("-" * 70)

            print(
                "Document ID:",
                source.get("id") or "Unknown"
            )

            print(
                "Parent ID:",
                source.get("parent_id") or "Unknown"
            )

            print(
                "Blob URL:",
                source.get("url") or "N/A"
            )

            text = source.get("text") or ""

            if len(text) > 500:
                text = text[:500] + "..."

            print("Content:", text)

        print("=" * 70)

    # History Display ======================================

    def print_history(self):

        print("\n" + "=" * 70)
        print("CONVERSATION HISTORY")
        print("=" * 70)

        if not self.history:
            print("No conversation history.")
            print("=" * 70)
            return

        for number, item in enumerate(
            self.history,
            start=1
        ):

            print(f"\nMESSAGE {number}")
            print("-" * 70)
            print(f"Role: {item['role']}")
            print("Content:")
            print(item["content"])

        print("=" * 70)

    # Statistics ======================================

    def document_count(self):

        try:
            return self.search.get_document_count()

        except Exception as error:

            print("\nUnable to retrieve document count.")
            print(error)

            return None

    def print_statistics(self):

        print("\n" + "=" * 70)
        print("RAG STATISTICS")
        print("=" * 70)

        print(
            "Search Index:",
            self.index_name
        )

        print(
            "Conversation Messages:",
            len(self.history)
        )

        total = self.document_count()

        if total is not None:
            print(
                "Documents in Index:",
                total
            )

        print("=" * 70)

    # Command Processing ======================================

    def handle_command(self, command):

        commands = {
            "/history": self.print_history,
            "/sources": self.print_sources,
            "/stats": self.print_statistics,
            "/clear": self.reset
        }

        action = commands.get(command)

        if action is None:
            return False

        action()

        if command == "/clear":
            print("\nConversation history cleared.")

        return True

    # Interactive Application ======================================

    def run(self):

        print("\n" + "=" * 70)
        print("AZURE CONVERSATIONAL RAG")
        print("=" * 70)

        print(
            f"Search Index: {self.index_name}"
        )

        print("\nAvailable commands:")
        print("  /history  - Show conversation history")
        print("  /sources  - Show retrieved sources")
        print("  /stats    - Show RAG statistics")
        print("  /clear    - Clear conversation")
        print("  /exit     - Exit")

        print("=" * 70)

        while True:

            try:
                user_input = input("\nYou: ").strip()

            except (KeyboardInterrupt, EOFError):

                print("\n\nGoodbye!")
                break

            if not user_input:
                continue

            command = user_input.lower()

            if command == "/exit":
                print("\nGoodbye!")
                break

            if self.handle_command(command):
                continue

            print("\nSearching knowledge base...")

            result = self.ask(user_input)

            if result:

                print("\nAssistant:")
                print(result)

                if self.sources:
                    print(
                        "\nSources are available. "
                        "Type /sources to view them."
                    )


# Application Entry============================================================

if __name__ == "__main__":

    application = ConversationalRAG()

    application.run()
