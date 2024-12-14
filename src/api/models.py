from langchain_community.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Groq
def initialize_groq_llm():
    return ChatGroq(
        temperature=0,
        groq_api_key=groq_api_key,
        model="groq/llama3-8b-8192",
    )

# Initialize OpenAI
def initialize_openai_llm():
    return ChatOpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        model="gpt-4o"
    )