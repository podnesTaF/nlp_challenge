from src.api.chromadb_api import add_document_to_chromadb
from PyPDF2 import PdfReader

class ContentIngestionAgent:
    def __init__(self, vector_db_client):
        self.vector_db_client = vector_db_client

    def process_pdf(self, file):
        """
        Process a PDF file, extract text, and store it in the vector database.
        """
        try:
            pdf_reader = PdfReader(file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
            
            response = add_document_to_chromadb(content, file.name)
            return f"File {file.name} processed and stored: {response}"
        except Exception as e:
            return f"Error processing file {file.name}: {e}"