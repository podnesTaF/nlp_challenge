import chromadb
from chromadb.config import Settings
from src.utils.embeddings import create_embedding

chroma_client = chromadb.Client(Settings(persist_directory="../data/.chroma_db"))
collection = chroma_client.create_collection(name="course_documents")

def add_document_to_chromadb(text, doc_id):
    embedding = create_embedding(text) 
    collection.add(documents=[text], metadatas=[{"doc_id": doc_id}], embeddings=[embedding])
    return f"Document {doc_id} added to ChromaDB."

def retrieve_relevant_docs_from_chromadb(query):
    query_embedding = create_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    return [doc["document"] for doc in results["documents"]]