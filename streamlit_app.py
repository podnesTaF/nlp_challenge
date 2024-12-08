import streamlit as st
from src.utils.pdf_processing import process_and_store_pdf
from src.api.chromadb_api import remove_document_from_chromadb
from src.agents.content_agent import ContentIngestionAgent
from src.agents.qa_agent import QuestionAnsweringAgent
import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
search_engine_id = os.getenv("SEARCH_ENGINE_ID")


# Initialize content ingestion agent
content_agent = ContentIngestionAgent(vector_db_client="course_documents")
qa_agent = QuestionAnsweringAgent(
    groq_api_key=groq_api_key,
    web_search_api_key=google_api_key,
    search_engine_id=search_engine_id
)

# Streamlit setup
st.set_page_config(
    page_title="Personalized Learning Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for Options
st.sidebar.title("Options")
llm_choice = st.sidebar.selectbox("Choose LLM", ["Groq API (default)", "Other LLMs (future)"])
st.sidebar.write("Selected LLM:", llm_choice)

# Search mode toggle
search_mode = st.sidebar.radio("Search Mode", ["Local", "Online"])

content_type = st.sidebar.selectbox("Choose Content Type to Upload", ["PDF", "YouTube Video", "PowerPoint"])


# Main Layout
col_chat, col_files = st.columns([3, 1])

with col_chat:
    st.title("💬 Personalized Learning Assistant")
    st.write(
        "This is a simple chatbot designed to provide personalized learning assistance. "
        "You can upload course documents and ask questions for tailored responses."
    )

    # Check if Groq API key is added
    if not groq_api_key:
        st.error("No Groq API key provided. Please enter your API key in the sidebar to proceed.", icon="⚠️")
    else:
        # Initialize session state for chat messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Container for chat messages
        messages_container = st.container()
        with messages_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input field positioned after messages
        prompt = st.chat_input("Ask a question...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with messages_container:  # Append new messages to the container
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Determine search mode based on user input
            if prompt.lower().startswith("online:"):
                search_mode = "online"
                prompt = prompt[len("online:"):].strip()

            # Generate response
            response = qa_agent.respond(prompt, mode=search_mode.lower())
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Add assistant message
            with messages_container:  # Append assistant response
                with st.chat_message("assistant"):
                    st.markdown(response)

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

def add_to_uploaded_files(name, status="Processed"):
    """
    Add an entry to the session_state uploaded_files list.
    """
    st.session_state.uploaded_files.append({"name": name, "status": status})

# File Management Logic
with col_files:
    if not groq_api_key:
        st.write("Please provide the Groq API Key in the sidebar to enable content ingestion.")
    else:
        st.subheader("File Management")

        if content_type == "PDF":
            uploaded_pdfs = st.file_uploader(
                "Upload PDF files", type="pdf", accept_multiple_files=True, label_visibility="hidden"
            )
            if uploaded_pdfs:
                for file in uploaded_pdfs:
                    if file.name not in [f["name"] for f in st.session_state.uploaded_files]:
                        # Process PDF
                        processing_message = content_agent.process_pdf(file)
                        st.write(processing_message)

                        # Add to uploaded files
                        add_to_uploaded_files(file.name)

        elif content_type == "YouTube Video":
            video_url = st.text_input("Enter YouTube Video URL")
            if st.button("Process Video"):
                # Process YouTube Video
                processing_message = content_agent.process_youtube_video(video_url)
                st.write(processing_message)

                # Add to uploaded files
                video_id = video_url.split("v=")[-1]
                if f"YouTube Video: {video_id}" not in [f["name"] for f in st.session_state.uploaded_files]:
                    add_to_uploaded_files(f"YouTube Video: {video_id}")

        elif content_type == "PowerPoint":
            uploaded_pptx = st.file_uploader("Upload PowerPoint File", type="pptx")
            if uploaded_pptx and st.button("Process PowerPoint"):
                # Process PowerPoint
                processing_message = content_agent.process_pptx(uploaded_pptx)
                st.write(processing_message)

                # Add to uploaded files
                if uploaded_pptx.name not in [f["name"] for f in st.session_state.uploaded_files]:
                    add_to_uploaded_files(uploaded_pptx.name)

        # Display Uploaded Files
        st.subheader("Uploaded Files")
        filter_query = st.text_input("Search files by name:", key="file_filter_query").strip().lower()
        filtered_files = [
            file for file in st.session_state.uploaded_files
            if filter_query in file["name"].lower()
        ] if filter_query else st.session_state.uploaded_files

        for file in filtered_files:
            col1, col2 = st.columns([3, 1])
            col1.write(f"📄 {file['name']} - {file['status']}")
            if col2.button("Remove", key=f"remove_{file['name']}"):
                # Remove file from ChromaDB
                remove_message = remove_document_from_chromadb(file["name"])
                st.write(remove_message)

                # Update session state
                st.session_state.uploaded_files = [
                    f for f in st.session_state.uploaded_files if f["name"] != file["name"]
                ]