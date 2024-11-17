import yaml
from src.api.groq_api import query_groq
from src.api.chromadb_api import retrieve_relevant_docs_from_chromadb

class Agent:
    def __init__(self, config_path="../config/agents.yaml"):
        # Load the agent configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.name = self.config["agents"][0]["name"]  # Assuming single agent for now
        self.description = self.config["agents"][0]["description"]

    def respond(self, user_input, api_key):
        """
        Process user input, retrieve context, and generate a response using Groq API.
        """
        # Retrieve relevant documents from ChromaDB
        relevant_docs = retrieve_relevant_docs_from_chromadb(user_input)
        context = [{"role": "system", "content": f"Reference Document: {doc}"} for doc in relevant_docs]

        # Prepare message history
        messages = [{"role": "user", "content": user_input}] + context

        # Generate response using Groq API
        response = query_groq(user_input, messages, api_key)
        return response
