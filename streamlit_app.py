import streamlit as st
from src.utils.pdf_processing import process_and_store_pdf
from src.api.chromadb_api import remove_document_from_chromadb
from src.agents.crew_agent import Agent

st.set_page_config(
    page_title="Personalized Learning Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the Agent
agent = Agent(config_path="./src/config/agents.yaml")

# Sidebar for Options
st.sidebar.title("Options")
llm_choice = st.sidebar.selectbox("Choose LLM", ["Groq API (default)", "Other LLMs (future)"])
st.sidebar.write("Selected LLM:", llm_choice)
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")


# Main Layout
col_chat, col_files = st.columns([3, 1])

with col_chat:
    st.title("💬 Personalized Learning Assistant")
    st.write(
        "This is a simple chatbot designed to provide personalized learning assistance. "
        "You can upload course documents and ask questions for tailored responses."
    )

    # Check if token is added
    if not groq_api_key:
        st.error("No API key provided. Please enter your API key in the sidebar to proceed.", icon="⚠️")
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

            uploaded_files = st.session_state.get("uploaded_files", [])
            response = agent.respond(prompt, groq_api_key, uploaded_files)

            with messages_container:  # Append assistant response to the container
                with st.chat_message("assistant"):
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Right Column: File Management
with col_files:
    if not groq_api_key:
        st.write("")  # Placeholder if API key is not provided
    else:
        st.subheader("File Management")

        if "uploaded_files" not in st.session_state:
          st.session_state.uploaded_files = []

        # File upload section
        uploaded_pdfs = st.file_uploader(
            "Upload PDF files", type="pdf", accept_multiple_files=True, label_visibility="hidden"
        )
        if uploaded_pdfs:
          for file in uploaded_pdfs:
              if file.name not in [f["name"] for f in st.session_state.uploaded_files]:
                  # Process and add the file
                  processing_message = process_and_store_pdf(file)
                  st.session_state.uploaded_files.append({"name": file.name, "status": "Processed", "file_obj": file})
                  st.write(processing_message)

        if st.session_state.uploaded_files:
          st.subheader("Uploaded Files")
          filter_query = st.text_input("Search files by name:", key="file_filter_query").strip().lower()
          filtered_files = [
              file for file in st.session_state.uploaded_files
              if filter_query in file["name"].lower()
          ] if filter_query else st.session_state.uploaded_files

          for file in filtered_files:
              col1, col2 = st.columns([3, 1], vertical_alignment="center")
              col1.write(f"📄 {file['name']} - {file['status']}")
              
              # Remove button
              if col2.button("Remove", key=f"remove_{file['name']}"):
                  # Remove file from ChromaDB
                  remove_message = remove_document_from_chromadb(file["name"])
                  st.write(remove_message)
                  
                  # Update the session state
                  st.session_state.uploaded_files = [
                      f for f in st.session_state.uploaded_files if f["name"] != file["name"]
                  ]
          
          # Synchronize st.file_uploader with session state
          remaining_files = [file["file_obj"] for file in st.session_state.uploaded_files]
          st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True, label_visibility="hidden", key="reupload", value=remaining_files)