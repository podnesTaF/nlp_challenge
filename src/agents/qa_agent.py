from src.api.groq_api import query_groq
from src.api.chromadb_api import retrieve_relevant_docs_from_chromadb
from transformers import pipeline

class QuestionAnsweringAgent:
    def __init__(self):
        self.summarizer = pipeline("summarization")

    def summarize_document(self, content, max_length=100):
        """
        Summarize a document for better LLM context.
        """
        try:
            summary = self.summarizer(content, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]["summary_text"]
        except Exception as e:
            return f"Error summarizing content: {e}"

    def respond(self, user_input, api_key):
        """
        Respond to a user's question by retrieving relevant documents and generating a response.
        """
        relevant_docs = retrieve_relevant_docs_from_chromadb(user_input)
        if relevant_docs:
            # Summarize the documents
            summaries = [
                {"role": "system", "content": f"Reference {i+1}: {self.summarize_document(doc['document'])}"}
                for i, doc in enumerate(relevant_docs)
            ]
            messages = summaries + [{"role": "user", "content": user_input}]
        else:
            messages = [
                {"role": "system", "content": "No relevant documents were found. Answer based on general knowledge."},
                {"role": "user", "content": user_input},
            ]

        return query_groq(user_input, messages, api_key)