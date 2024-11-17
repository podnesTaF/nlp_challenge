import requests

def query_groq(user_input, messages, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",  # Replace with the appropriate model name
        "messages": [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error with Groq API: {response.text}"
