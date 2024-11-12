import streamlit as st
from src.utils.pdf_processing import process_and_store_pdf
from src.api.chromadb_api import retrieve_relevant_docs_from_chromadb

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

# Placeholder for Groq API key
groq_api_key = st.text_input("Groq API Key (placeholder for actual setup)", type="password")
if not groq_api_key:
    st.info("Please add your Groq API key to continue.", icon="🗝️")
else:
    # Initialize session state for chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # PDF Upload Section
    st.subheader("Upload PDF Materials")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    # Process each uploaded PDF and store in ChromaDB
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} PDF(s). Processing...")
        for file in uploaded_files:
            processing_message = process_and_store_pdf(file)
            st.write(processing_message)

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

        # Retrieve relevant documents for context from ChromaDB
        relevant_docs = retrieve_relevant_docs_from_chromadb(prompt)
        for doc in relevant_docs:
            st.session_state.messages.append({"role": "system", "content": f"Reference Document: {doc}"})

        # Placeholder for Groq API response (simulate for now)
        response = f"Simulated response for: {prompt}"

        # Display and save the assistant's response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
