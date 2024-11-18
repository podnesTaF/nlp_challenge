import streamlit as st
from src.utils.pdf_processing import process_and_store_pdf
from src.api.chromadb_api import remove_document_from_chromadb
from src.agents.crew_agent import Agent

# Initialize the Agent
agent = Agent(config_path="./src/config/agents.yaml")

# Show title and description.
st.title("💬 Personalized Learning Assistant")
st.write(
    "This is a simple chatbot designed to provide personalized learning assistance. "
    "You can upload course documents and ask questions for tailored responses."
)

# Sidebar for LLM selection
st.sidebar.title("Options")
llm_choice = st.sidebar.selectbox("Choose LLM", ["Groq API (default)", "Other LLMs (future)"])
st.sidebar.write("Selected LLM:", llm_choice)

# Placeholder for API key input
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
if not groq_api_key:
    st.sidebar.info("Please add your Groq API key to continue.", icon="🗝️")
else:
    # Initialize session state for chat messages and uploaded files
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # File Upload Section for PDFs
    st.subheader("Upload Files")
    uploaded_pdfs = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
    if uploaded_pdfs:
        for file in uploaded_pdfs:
            if file.name not in [f["name"] for f in st.session_state.uploaded_files]:
                processing_message = process_and_store_pdf(file)
                st.session_state.uploaded_files.append({"name": file.name, "status": "Processed"})
                st.write(processing_message)
        st.success(f"Uploaded {len(uploaded_pdfs)} PDF(s).")

    # Display and Manage Uploaded Files
    st.subheader("Uploaded Files")
    for file in st.session_state.uploaded_files:
        col1, col2 = st.columns([4, 1])
        col1.write(f"📄 {file['name']} - {file['status']}")
        if col2.button("Remove", key=file["name"]):
            # Remove file from ChromaDB
            remove_message = remove_document_from_chromadb(file["name"])
            st.write(remove_message)

            # Remove file from session state
            st.session_state.uploaded_files = [
                f for f in st.session_state.uploaded_files if f["name"] != file["name"]
            ]
            st.experimental_rerun()  # Reload the page to reflect changes

    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input field for asking questions
    if prompt := st.chat_input("Ask a question..."):
        # Save the user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Use the RAG pipeline
        response, references = agent.rag_pipeline(prompt, groq_api_key)

        # Format references
        references_md = "\n".join([f"- **Reference {i+1}**: {doc}" for i, doc in enumerate(references)])

        # Display response and references
        with st.chat_message("assistant"):
            st.markdown(response)
            st.markdown("#### References:\n" + references_md)

        # Save response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})
