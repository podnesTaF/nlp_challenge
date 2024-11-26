import yaml
from src.api.groq_api import query_groq
from src.api.chromadb_api import retrieve_relevant_docs_from_chromadb
from transformers import pipeline

class Agent:
    def __init__(self, config_path="../config/agents.yaml"):
        # Load the agent configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.name = self.config["agents"][0]["name"] 
        self.description = self.config["agents"][0]["description"]
        self.summarizer = pipeline("summarization") 

    def summarize_document(self, doc_content, max_length=100):
        """
        Summarize the content of a document for better LLM context.
        """
        summary = self.summarizer(doc_content, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]["summary_text"]

    def create_prompt(self, user_input, summaries=None):
      """
      Create a structured prompt with summaries and user query.
      If no summaries are provided, create a simple query.
      """
      if summaries:
          context = "\n".join([f"{summary['content']}" for summary in summaries])
          prompt = (
              f"Based on the following references:\n{context}\n\n"
              f"Question:\n{user_input}\n\n"
              f"Answer in detail and reference the summaries provided."
          )
      else:
          # Fallback prompt without references
          prompt = f"Question:\n{user_input}\n\nAnswer based on your general knowledge."
      return prompt

    def respond(self, user_input, api_key, uploaded_files):
      if uploaded_files:
          # Retrieve top relevant documents
          top_docs = retrieve_relevant_docs_from_chromadb(user_input)

          if top_docs:
              summaries = [
                  {"role": "system", "content": f"Reference {i+1}: {self.summarize_document(doc['document'])}"}
                  for i, doc in enumerate(top_docs)
              ]
              messages = summaries + [{"role": "user", "content": user_input}]
          else:
              messages = [
                  {"role": "system", "content": "No relevant documents were found. Answer based on general knowledge."},
                  {"role": "user", "content": user_input},
              ]
      else:
          messages = [
              {"role": "system", "content": "No relevant documents were found. Answer based on general knowledge."},
              {"role": "user", "content": user_input},
          ]

      # Generate response using Groq API
      response = query_groq(user_input, messages, api_key)
      return response
