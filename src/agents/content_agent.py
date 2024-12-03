from src.api.chromadb_api import add_document_to_chromadb
from PyPDF2 import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from pptx import Presentation
from pytesseract import image_to_string
from PIL import Image
import os


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
        
    def process_youtube_video(self, video_url):
        """
        Extract transcript from a YouTube video and store it in the vector database.
        """
        try:
            video_id = video_url.split("v=")[-1]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            content = " ".join([t['text'] for t in transcript])

            print("video_id", video_id)
            
                
            # Add content to the vector database
            response = add_document_to_chromadb(content, video_id)
            return f"YouTube video processed and stored: {response}"
        except Exception as e:
            return f"Error processing YouTube video: {e}"
      
    def process_pptx(self, file):
      """
      Extract text and images from a PowerPoint presentation.
      """
      try:
          # Define the directory to save images
          base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the root of the project
          images_dir = os.path.join(base_dir, "data", "images")
          os.makedirs(images_dir, exist_ok=True)  # Create the directory if it doesn't exist

          presentation = Presentation(file)
          content = ""

          # Debugging: Ensure slides and shapes are being read
          print(f"Debug: Number of slides in the presentation: {len(presentation.slides)}")

          for slide_idx, slide in enumerate(presentation.slides, start=1):
              print(f"Debug: Processing slide {slide_idx}")
              for shape_idx, shape in enumerate(slide.shapes, start=1):
                  print(f"Debug: Processing shape {shape_idx} on slide {slide_idx}")

                  # Extract text from text-containing shapes
                  if shape.has_text_frame:
                      text = shape.text.strip()
                      print(f"Debug: Extracted text from shape {shape_idx}: {text}")
                      content += text + "\n"

                  # Extract text from images using OCR
                  elif hasattr(shape, "image"):
                      image_name = f"{images_dir}/{shape.name}.png"
                      print(f"Debug: Saving image from shape {shape_idx} to {image_name}")
                      with open(image_name, "wb") as f:
                          f.write(shape.image.blob)

                      # Perform OCR on the image
                      try:
                          text_from_image = image_to_string(Image.open(image_name))
                          print(f"Debug: Extracted text from image in shape {shape_idx}: {text_from_image}")
                          content += text_from_image + "\n"
                      except Exception as img_error:
                          print(f"Warning: Failed to extract text from image in shape {shape_idx}: {img_error}")

          print(f"Debug: Full extracted content: {content[:500]}...")  # Preview first 500 characters

          # Add content to the vector database
          response = add_document_to_chromadb(content, file.name)
          return f"PowerPoint file processed and stored: {response}"
      except Exception as e:
          print(f"Error in process_pptx: {e}")
          return f"Error processing PowerPoint file: {e}"
      