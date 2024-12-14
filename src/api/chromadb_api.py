import chromadb
import os
from langchain_openai import OpenAIEmbeddings


persist_directory = "../../data"
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory, exist_ok=True)



client = chromadb.PersistentClient(persist_directory)

collection_name = "new_collection"
collection = client.get_or_create_collection(name=collection_name)
embedding_model = OpenAIEmbeddings()

def add_document_to_chromadb(chunks=None, content=None, metadata=None):
    """
    Add content or pre-chunked data to ChromaDB.

    Args:
        chunks (list[dict]): List of dictionaries, each containing "content" and "metadata".
        content (str): Raw text content to be stored.
        metadata (dict): Metadata associated with the raw content.

    Returns:
        str: Success or error message.
    """
    try:
        if chunks:
            # Add pre-chunked content to ChromaDB
            for chunk in chunks:
                embedding = embedding_model.embed_query(chunk["content"])
                collection.add(
                    ids=[chunk["metadata"]["unique_id"]],
                    documents=[chunk["content"]],
                    metadatas=[chunk["metadata"]],
                    embeddings=[embedding]
                )
        elif content and metadata:
            # Add raw content with metadata
            embedding = embedding_model.embed_query(content)
            collection.add(
                ids=[metadata["unique_id"]],
                documents=[content],
                metadatas=[metadata],
                embeddings=[embedding]
            )
        else:
            raise ValueError("Either chunks or content with metadata must be provided.")

        return "Content successfully added to ChromaDB."
    except Exception as e:
        return f"Error adding content to ChromaDB: {e}"



def retrieve_relevant_docs_from_chromadb(query, top_k=5):
    # Embed the query
    query_embedding = embedding_model.embed_query(query)

    # Retrieve top-k relevant chunks
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["documents", "metadatas"])
    print("most relevant docs", results)

    if not results or not results.get("documents") or not results.get("metadatas"):
        return "no context"
    
  
    # Flatten the list of documents and metadata
    documents = [doc for sublist in results["documents"] for doc in sublist]
    metadatas = [meta for sublist in results["metadatas"] for meta in sublist]

    # Build context with references
    context_with_references = []
    for doc, meta in zip(documents, metadatas):
        file_name = meta.get("file_name", "Unknown File")
        page = meta.get("page_num", "Unknown Page")
        context_with_references.append(f"Reference: file name: {file_name}, page: {page}\n{doc}")

    context = "\n\n".join(context_with_references)

    return context



def remove_document_from_chromadb(file_name, file_ids):
    """
    Remove all chunks of a file from ChromaDB using their IDs.
    """
    try:
        # Flatten the list of IDs if it's nested
        flat_file_ids = [item for sublist in file_ids for item in sublist] if isinstance(file_ids, list) and any(isinstance(i, list) for i in file_ids) else file_ids
        
        # Delete all IDs associated with the file
        collection.delete(ids=flat_file_ids)
        return f"All chunks of {file_name} have been removed from ChromaDB."
    except Exception as e:
        return f"Error removing file {file_name}: {str(e)}"
    

def get_uploaded_documents():
    """
    Retrieve all files currently stored in ChromaDB, grouped by file name.
    """
    try:
        # Fetch documents and metadata from ChromaDB
        documents = collection.get(include=["metadatas"])
        
        # Group documents by file name
        file_map = {}
        for meta, doc_id in zip(documents["metadatas"], documents["ids"]):
            file_name = meta.get("file_name", "Unknown File")  # Fallback if file_name is missing
            if file_name not in file_map:
                file_map[file_name] = {"name": file_name, "status": "Processed", "ids": []}
            file_map[file_name]["ids"].append(doc_id)
        

        # Convert file_map to a list
        return list(file_map.values())
    except Exception as e:
        print(f"Error retrieving uploaded documents: {e}")
        return []