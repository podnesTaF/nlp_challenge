import requests

class WebSearchAgent:
    def __init__(self, api_key, search_engine_id):
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def search(self, query, num_results=3):
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": num_results
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("items", [])
            return [{"title": item["title"], "snippet": item["snippet"], "link": item["link"]} for item in results]
        else:
            return [{"error": f"Error fetching search results: {response.text}"}]