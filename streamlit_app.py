import base64
from src.agents.web_search_agent import  create_web_search_task, initiate_web_agent
from src.api.models import initialize_groq_llm, initialize_openai_llm
import streamlit as st
from src.api.chromadb_api import get_uploaded_documents, remove_document_from_chromadb, retrieve_relevant_docs_from_chromadb
from src.agents.crew_agent import  create_pdf_summary_task, create_qa_task, create_quiz_task, initialize_pdf_summary_agent, initialize_question_answering_agent, initialize_quiz_agent
from src.agents.content_agent import ContentIngestionAgent
import os
from dotenv import load_dotenv
from crewai import Crew,Process
from src.stt.real_time_stt import RealTimeSTT
from src.tts.tts_engine import TTSEngine

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")


# Initialize content ingestion agent
content_agent = ContentIngestionAgent()

# Streamlit setup
st.set_page_config(
    page_title="Personalized Learning Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)


llm_options = {"Groq API": initialize_groq_llm, "OpenAI": initialize_openai_llm}
selected_llm_name = st.sidebar.selectbox("Choose LLM", list(llm_options.keys()), key="llm_choice")
st.sidebar.write("Selected LLM:", selected_llm_name)

llm_initializer = llm_options[selected_llm_name]
llm = llm_initializer()

# Initialize agents
pdf_summary_agent = initialize_pdf_summary_agent(llm)
qa_agent = initialize_question_answering_agent(llm)
quiz_agent = initialize_quiz_agent(llm)

web_search_agent = initiate_web_agent(llm)

# Initialize Whisper-based STT and TTS
tts_response = ''
real_time_stt = RealTimeSTT(model_name="base")
tts_engine = TTSEngine()


content_type = st.sidebar.selectbox("Choose Content Type to Upload", ["PDF", "YouTube Video", "PowerPoint"])

# Agent selection
selected_agent = st.sidebar.selectbox("Choose Agent", ["Personalized Learning Assistant", "Quiz Creator"])
st.sidebar.write("Selected Agent:", selected_agent)


# Search mode toggle
search_mode = st.sidebar.radio("Search Mode", ["Local", "Online"])

response_mode = st.sidebar.radio("Response Mode", ["Text", "Voice"], index=0)


# Main Layout
col_chat, col_files = st.columns([3, 1])

def process_input(user_input, agent_type):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with messages_container:
        with st.chat_message("user"):
            st.markdown(user_input)

    tasks = []
    agents = []

    if search_mode == "Local":
        context = retrieve_relevant_docs_from_chromadb(user_input)
        if context:
            tasks.append(create_pdf_summary_task(context=context, agent=pdf_summary_agent))
            agents.append(pdf_summary_agent)

        if agent_type == "Personalized Learning Assistant":
            tasks.append(create_qa_task(prompt=user_input, agent=qa_agent))
            agents.append(qa_agent)
        elif agent_type == "Quiz Creator":
            tasks.append(create_quiz_task(topic=user_input, agent=quiz_agent))
            agents.append(quiz_agent)

    elif search_mode == "Online":
        # Perform web search using WebSearchAgent
        agents.append(web_search_agent)
        tasks.append(create_web_search_task(query=user_input, agent=web_search_agent))

    # Execute the tasks
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    st.session_state.messages.append({"role": "assistant", "content": result})
    with messages_container:
        with st.chat_message("assistant"):
            st.markdown(result)
            return result

with col_chat:
    if selected_agent == "Personalized Learning Assistant":
        st.title("💬 Personalized Learning Assistant")
        input_placeholder = "Ask a question..."
    elif selected_agent == "Quiz Creator":
        st.title("📝 Quiz Creator")
        input_placeholder = "Enter the topic of the quiz"

    st.write(
        "This is a chatbot designed for personalized learning assistance and quiz generation. "
        "You can upload documents or specify a topic for a quiz."
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
        prompt = st.chat_input(input_placeholder)
        if prompt:
            tts_response = process_input(prompt, selected_agent)

        # Start Listening button
        if st.button("Start Listening", key="start_listening_button"):
            with st.spinner("Listening..."):
                transcription = real_time_stt.listen_and_transcribe(duration=10)
                if transcription:
                    tts_response = process_input(transcription, selected_agent)
        # TTS Response
        if st.checkbox("Speak Response", key="speak_response_checkbox"):
            tts_engine.speak(tts_response)


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
        uploaded_documents = get_uploaded_documents()
        print(uploaded_documents)

        filter_query = st.text_input("Search files by name:", key="file_filter_query").strip().lower()
        filtered_files = [
            file for file in uploaded_documents
            if filter_query in file["name"].lower()
        ] if filter_query else uploaded_documents

        # Display files in a structured format
        for file in filtered_files:
            col1, col2 = st.columns([3, 1])
            col1.write(f"📄 {file['name']} - {file['status']}")

            # Add a delete button
            if col2.button("Remove", key=f"remove_{file['name']}"):
                # Remove all chunks of the file from ChromaDB
                try:
                    remove_message = remove_document_from_chromadb(file["name"], file["ids"])
                    st.success(remove_message)
                except Exception as e:
                    st.error(f"Error removing {file['name']}: {str(e)}")

                # Refresh the displayed documents
                uploaded_documents = get_uploaded_documents()