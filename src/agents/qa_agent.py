from src.api.groq_api import query_groq
from src.api.chromadb_api import retrieve_relevant_docs_from_chromadb
from transformers import pipeline
from src.agents.web_search_agent import WebSearchAgent

class QuestionAnsweringAgent:
    def __init__(self, groq_api_key, web_search_api_key=None, search_engine_id=None):
        self.groq_api_key = groq_api_key
        self.summarizer = pipeline("summarization")
        self.web_search_agent = WebSearchAgent(web_search_api_key, search_engine_id) if web_search_api_key and search_engine_id else None

    def summarize_document(self, content, max_length=100):
        """
        Summarize a document for better LLM context.
        """
        try:
            summary = self.summarizer(content, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]["summary_text"]
        except Exception as e:
            return f"Error summarizing content: {e}"
        
    def respond_local(self, user_input):
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
        return query_groq(user_input, messages, self.groq_api_key)


    def respond_online(self, user_input):
      """
      Use only online search to generate responses.
      """
      if not self.web_search_agent:
          return "Online search is not configured."
      
      search_results = self.web_search_agent.search(user_input)
      if search_results:
          summaries = []
          for i, result in enumerate(search_results):
              content = f"{result['title']} - {result['snippet']}"
              summary = self.summarize_document(content)
              summaries.append(f"Online Reference {i + 1}: {summary} [Read more]({result['link']})")
          return "\n\n".join(summaries)
      else:
          return "No results found online."

    def respond(self, user_input, mode="local"):
        """
        Switch between local and online search based on mode.
        """
        if mode == "online":
            return self.respond_online(user_input)
        else:
            return self.respond_local(user_input)