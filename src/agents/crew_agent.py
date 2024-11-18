import yaml
from src.api.groq_api import query_groq
from src.api.chromadb_api import retrieve_relevant_docs_from_chromadb

class Agent:
    def __init__(self, config_path="../config/agents.yaml"):
        # Load the agent configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.name = self.config["agents"][0]["name"]
        self.description = self.config["agents"][0]["description"]

    def rag_pipeline(self, user_input, api_key):
      relevant_docs = retrieve_relevant_docs_from_chromadb(user_input)

      # Debug: Check the structure
      print(f"Debug relevant_docs: {relevant_docs}")

      # Handle the structure and prepare context
      context = "\n".join(
          [
              f"Reference {i+1} (Title: {doc['metadata'].get('title', 'No Title') if isinstance(doc['metadata'], dict) else 'No Metadata'}): {doc['document']}"
              for i, doc in enumerate(relevant_docs)
          ]
      )
      prompt = (
          f"Context:\n{context}\n\n"
          f"Question:\n{user_input}\n\n"
          f"Answer with references to the documents provided above."
      )

      # Generate response
      response = query_groq(prompt, [{"role": "system", "content": context}], api_key)
      return response, [
          doc["metadata"].get("title", "No Title") if isinstance(doc["metadata"], dict) else "No Metadata"
          for doc in relevant_docs
      ]