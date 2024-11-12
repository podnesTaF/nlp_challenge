from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')  # Choose a smaller model if speed is important

def create_embedding(text):
    """
    Generates embeddings for a given text using Sentence Transformers.
    """
    embedding = model.encode(text)
    return embedding.tolist()  # Convert to list for compatibility with ChromaDB
