import os
import requests
from crewai.tools import BaseTool
from typing import Type
from crewai import Agent, Task
from pydantic import BaseModel, Field

google_api_key = os.getenv("GOOGLE_API_KEY")
search_engine_id = os.getenv("SEARCH_ENGINE_ID")

class WebSearchToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    input: str = Field(..., description="input to query")

class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = (
        "Query a phrase in google web search"
    )
    args_schema: Type[BaseModel] = WebSearchToolInput

    def _run(self, input: str) -> str:
        # Implementation goes here
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": search_engine_id,
            "q": input,
            "num": 5
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("items", [])
            return [{"title": item["title"], "snippet": item["snippet"], "link": item["link"]} for item in results]
        else:
            return [{"error": f"Error fetching search results: {response.text}"}]




def initiate_web_agent(llm):
      return Agent(
          role="Web Search Agent",
          goal="Search for information online using Google Custom Search.",
          tools=[WebSearchTool()],
          verbose=True,
          allow_delegation=True,
          llm=llm,
          backstory="You are an expert in finding accurate and relevant information online using Google Search."
      )


def create_web_search_task(query: str, agent: Agent) -> Task:
    """
    Create a task for performing a web search using the WebSearchAgent.
    """
    return Task(
        description=f"Perform a web search for the given query: {query}",
        expected_output="Relevant web search results including titles, snippets, and links.",
        agent=agent,
        config={"input": query}
    )