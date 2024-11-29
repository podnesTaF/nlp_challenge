import chromadb
from chromadb.config import Settings
from src.utils.embeddings import create_embedding
import os

persist_directory = "../../data"
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory, exist_ok=True)



client = chromadb.PersistentClient(persist_directory)

collection_name = "doc_collection"
collection = client.get_or_create_collection(name=collection_name)


def add_document_to_chromadb(content, doc_id):
    """
    Add a document to ChromaDB.
    """
    try:
      # Create an embedding for the document content
      embedding = create_embedding(content)
      
      # Add the document, its metadata, and embedding to the collection
      collection.add(
            ids=[doc_id],  # Unique ID for the document
            documents=[content],
            metadatas=[{"doc_id": doc_id}],  # Single metadata dictionary for the document
            embeddings=[embedding]
        )
      print(f"Document {doc_id} added. Total documents in collection: {collection.count()}")
      return f"Document {doc_id} added to ChromaDB."
    except Exception as e:
      return f"Error adding document {doc_id} to ChromaDB: {e}"

def retrieve_relevant_docs_from_chromadb(query, top_k=3):
    """
    Retrieve relevant documents from ChromaDB based on the query.
    """
    query_embedding = create_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    relevant_docs = []
    for doc, meta in zip(results["documents"], results["metadatas"]):
        # Ensure doc is treated as a string
        doc_content = " ".join(doc) if isinstance(doc, list) else doc  # Combine if list, or use directly
        # Simple relevance filter (e.g., keyword check)
        if any(keyword in doc_content.lower() for keyword in query.lower().split()):  # Adjust for better NLP filtering
            relevant_docs.append({"document": doc_content, "metadata": meta})
    return relevant_docs


def remove_document_from_chromadb(doc_id):
    """
    Remove a document from ChromaDB by its unique identifier.
    """
    try:
        collection.delete(ids=[doc_id])
        return f"Document {doc_id} removed from ChromaDB."
    except Exception as e:
        return f"Error removing document {doc_id}: {e}"
    

def get_uploaded_documents():
    """
    Retrieve all documents currently stored in ChromaDB.
    """
    try:
        documents = collection.get(include=["documents", "metadatas"])
        return [
            {"name": id, "status": "Processed"}
            for meta,id in zip(documents["metadatas"], documents['ids'])
        ]
    except Exception as e:
        print(f"Error retrieving uploaded documents: {e}")
        return []