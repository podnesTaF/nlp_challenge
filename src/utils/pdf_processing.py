from src.api.chromadb_api import add_document_to_chromadb
from PyPDF2 import PdfReader

def process_and_store_pdf(file):
    """
    Process a PDF file and add it to ChromaDB.
    """
    try:
        pdf_reader = PdfReader(file)
        content = ""
        for page in pdf_reader.pages:
            content += page.extract_text()
        
        # Add to ChromaDB
        response = add_document_to_chromadb(content, file.name)
        print(f"DEBUG: Added to ChromaDB - {response}")
        return f"File {file.name} processed and stored."
    except Exception as e:
        print(f"Error processing file {file.name}: {e}")
        return f"Failed to process {file.name}."
