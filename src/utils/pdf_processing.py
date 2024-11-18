from PyPDF2 import PdfReader
from src.api.chromadb_api import add_document_to_chromadb

def process_and_store_pdf(file):
    """
    Process a PDF file, extract text, and store it in ChromaDB.
    """
    pdf_reader = PdfReader(file)
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text() + "\n"

    # Use file name as a unique identifier
    add_document_to_chromadb(full_text, file.name)
    return f"{file.name} processed and stored."