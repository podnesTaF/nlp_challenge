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

# Layout with left sidebar for keys and options, and right "file management sidebar"
st.sidebar.title("Options")
# Left Sidebar: Keys and Options
llm_choice = st.sidebar.selectbox("Choose LLM", ["Groq API (default)", "Other LLMs (future)"])
st.sidebar.write("Selected LLM:", llm_choice)
groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Main Layout with Chat Interface (left) and File Management (right)
col_chat, col_files = st.columns([2, 1])  # Adjust width ratios as needed

# Left Column: Chat Interface
with col_chat:
    # Show title and description.
    st.title("💬 Personalized Learning Assistant")
    st.write(
        "This is a simple chatbot designed to provide personalized learning assistance. "
        "You can upload course documents and ask questions for tailored responses."
    )

    # Initialize session state for chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input field for asking questions
    if prompt := st.chat_input("Ask a question..."):
        # Save the user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Use the agent to generate a response
        if groq_api_key:
            # Pass uploaded files to the agent
            uploaded_files = st.session_state.get("uploaded_files", [])
            response = agent.respond(prompt, groq_api_key, uploaded_files)

            # Display and save the assistant's response
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("Please enter your Groq API Key in the left sidebar.", icon="🗝️")

# Right Column: File Management
with col_files:
    st.subheader("File Management")

    # Initialize session state for uploaded files
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # File Upload Section for PDFs
    uploaded_pdfs = st.file_uploader(
        "Upload PDF files", type="pdf", accept_multiple_files=True, label_visibility="hidden"
    )
    if uploaded_pdfs:
        for file in uploaded_pdfs:
            if file.name not in [f["name"] for f in st.session_state.uploaded_files]:
                processing_message = process_and_store_pdf(file)
                st.session_state.uploaded_files.append({"name": file.name, "status": "Processed", "id": id(file)})
                st.write(processing_message)

    # Filter Bar for Uploaded Files
    if st.session_state.uploaded_files:
        st.subheader("Uploaded Files")

        # Filter input box
        filter_query = st.text_input("Search files by name:", key="file_filter_query").strip().lower()

        # Filter uploaded files based on the query
        filtered_files = [
            file for file in st.session_state.uploaded_files
            if filter_query in file["name"].lower()
        ] if filter_query else st.session_state.uploaded_files

        # Display filtered files
        for file in filtered_files:
            col1, col2 = st.columns([3, 1], vertical_alignment='center')
            col1.write(f"📄 {file['name']} - {file['status']}")
            if col2.button("Remove", key=f"remove_{file['id']}"):
                # Remove file from the database
                remove_message = remove_document_from_chromadb(file["name"])
                st.write(remove_message)

                # Filter and remove file from session state
                st.session_state.uploaded_files = [
                    f for f in st.session_state.uploaded_files if f["id"] != file["id"]
                ]
