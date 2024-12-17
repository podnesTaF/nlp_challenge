# NLP Challenge

**Team 5**

Oleksii Pidnebesnyi

Mark Vaykul

German Novykov

## Table of Contents

- [NLP Challenge](#nlp-challenge)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
    - [2. System Architecture](#2-system-architecture)
      - [2.1 Folder Structure](#21-folder-structure)
      - [2.2 Technologies Used](#22-technologies-used)
    - [3 Models](#3-models)
      - [3.1 Groq API and OpenAI Integration](#31-groq-api-and-openai-integration)
      - [3.2 Embeddings](#32-embeddings)
    - [4 Content Ingestion](#4-content-ingestion)
      - [4.1 Content Ingestion Agent](#41-content-ingestion-agent)
      - [4.2 Embedding](#42-embedding)
      - [4.3 Key Functions](#43-key-functions)
      - [4.4 File Management UI](#44-file-management-ui)
  - [5. Agents](#5-agents)
    - [5.1 Text Summarization Expert](#51-text-summarization-expert)
    - [5.2 Question Answering Agent](#52-question-answering-agent)
    - [5.3 Agent selection](#53-agent-selection)
    - [5.4 Web Search Agent](#54-web-search-agent)
    - [5.5 Crew Processing](#55-crew-processing)
  - [6. STT and TTS Integration](#6-stt-and-tts-integration)
    - [6.1 Speech-to-Text (STT)](#61-speech-to-text-stt)
    - [Code Example: Silence Detection in STT](#code-example-silence-detection-in-stt)
    - [6.2 Text-to-Speech (TTS)](#62-text-to-speech-tts)
    - [Code Example: Playing and Stopping TTS](#code-example-playing-and-stopping-tts)
    - [6.3 Key Integration in Streamlit](#63-key-integration-in-streamlit)
    - [Code Example: Start Listening in Streamlit](#code-example-start-listening-in-streamlit)
    - [6.4 Sample Workflow](#64-sample-workflow)
  - [7. Possible Improvements](#7-possible-improvements)
    - [7.1 Remote Vector Database](#71-remote-vector-database)
    - [7.2 Content Summarization Enhancements](#72-content-summarization-enhancements)
    - [7.3 Bug Fixing](#73-bug-fixing)
    - [7.4 User Experience (UX) Improvements](#74-user-experience-ux-improvements)
  - [8. Conclusion](#8-conclusion)
  - [9. How Generative AI Helped Us Implement This Project](#9-how-generative-ai-helped-us-implement-this-project)
    - [Example of AI Assistance](#example-of-ai-assistance)

## 1. Introduction

The goal of this project was to create a personalized learning assistant that can help users by summarizing text, answering questions, generating quizzes, and even searching the web for information. The assistant also supports voice input and output, making it more interactive and user-friendly.

The challenge was complex, requiring the integration of various technologies for a multi-agent framework. Processing diverse content types, including PDFs, YouTube links, and PowerPoint files, added further complexity.

While the model is not perfect, it satisfies the main objectives and provides a solid foundation for future improvements.

### 2. System Architecture

#### 2.1 Folder Structure

- **`streamlit-app.py`**
  - Main application file for the Streamlit interface.
- **`src/agents`**
  - Contains agent-specific logic (e.g., text summarization, question answering, etc.).
- **`src/api`**
  - Configuration for database and models.
- **`src/utils`**
  - Helper functions for reusable logic.
- **`src/config`**
  - YAML file for application configuration.
- **`src/stt`**
  - Functions for Speech-to-Text processing.
- **`src/tts`**
  - Functions for Text-to-Speech processing.

#### 2.2 Technologies Used

- **LLMs:** Groq API, OpenAI.
- **Vector Database:** ChromaDB (local).
- **Agent Framework:** CrewAI.
- **STT and TTS:** PyAudio, gTTS.
- **Frameworks and Tools:** LangChain, Streamlit, and additional Python libraries.

### 3 Models

#### 3.1 Groq API and OpenAI Integration

The system integrates Groq API and OpenAI models, allowing users to choose between them in the Streamlit sidebar. Each model is initialized with API keys and configured for consistent outputs.

- **Groq API:** Uses `ChatGroq` with the `groq/llama3-8b-8192` model.
- **OpenAI:** Uses `ChatOpenAI` with the `gpt-4o` model.

Users select the desired model from a dropdown menu, and the application dynamically initializes it.

```python
llm_options = {"Groq API": initialize_groq_llm, "OpenAI": initialize_openai_llm}
selected_llm_name = st.sidebar.selectbox("Choose LLM", list(llm_options.keys()))
llm = llm_options[selected_llm_name]()
```

#### 3.2 Embeddings

The system uses OpenAIEmbeddings() to convert text into embeddings for efficient retrieval and similarity searches. These embeddings are stored in a local ChromaDB vector database.

This setup supports powerful text processing and ensures accurate answers and summaries based on user data.

### 4 Content Ingestion

#### 4.1 Content Ingestion Agent

The `ContentIngestionAgent` is a standalone component, not part of the CrewAI framework. It processes content for ingestion into the vector database (ChromaDB). Key functionalities include:

**PDF Processing:**

- Extracts text from PDF pages.
- Splits content into chunks (e.g., paragraphs) and adds metadata like file name, page number, and unique ID.
- Stores the processed chunks in ChromaDB.

**YouTube Video Processing:**

- Retrieves transcripts using the YouTube API.
- Combines transcript text and metadata, including the video ID.
- Adds the content and metadata to ChromaDB.

**PowerPoint (PPTX) Processing:**

- Extracts text from slides and shapes within a presentation.
- Associates each text block with metadata, such as slide and shape numbers.
- Stores processed text chunks in ChromaDB.

This agent enables seamless content ingestion for diverse file types, ensuring they are stored with relevant metadata for efficient retrieval.

#### 4.2 Embedding

The system uses `OpenAIEmbeddings()` to convert text into embeddings. These embeddings allow:

Efficient similarity searches.

Accurate retrieval of relevant content based on user queries.

#### 4.3 Key Functions

**Add Content to Database:**
Processes chunks or raw text with metadata and stores them in ChromaDB.

```python
embedding = embedding_model.embed_query(content)
collection.add(
    ids=[metadata["unique_id"]],
    documents=[content],
    metadatas=[metadata],
    embeddings=[embedding]
)
```

**Retrieve Relevant Documents:** Matches user queries to stored embeddings and retrieves the most relevant text.

```python

query_embedding = embedding_model.embed_query(query)

results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["documents", "metadatas"])

documents = [doc for sublist in results["documents"] for doc in sublist]

metadatas = [meta for sublist in results["metadatas"] for meta in sublist]

return "\n\n".join([f"Reference: {meta['file_name']} (Page {meta.get('page_num', 'N/A')})\n{doc}" for doc, meta in zip(documents, metadatas)])
```

**Remove Documents from Database:**
Deletes all content related to a specific file from ChromaDB.

```python
def remove_document_from_chromadb(file_name, file_ids):
    collection.delete(ids=file_ids)
```

#### 4.4 File Management UI

Users can upload PDFs, YouTube links, or PowerPoint files through the Streamlit interface. Each file type is processed and stored in ChromaDB.

Users can search uploaded files by name or status.

Includes a button to remove selected files from the database.

![file management](https://storage.googleapis.com/lift-peak/extra/file_management.png)

## 5. Agents

#### 5.1 Text Summarization Expert

The **Text Summarization Expert** is a specialized agent designed to summarize text from documents, like PDFs, and include references to pages and file names. The agent operates based on the CrewAI framework, using a pre-trained language model (LLM).

**Purpose:**  
 Creates detailed, structured summaries with references to page numbers and file names. If no relevant context is available, it returns "no context."

**Agent Setup:**

```python
Agent(
    name="pdf_summary_agent",
    role="Text Summary Specialist",
    goal="Create detailed summaries or reports based on PDFs.",
    backstory="You specialize in extracting and summarizing key insights from text.",
    llm=llm
)
```

#### 5.2 Question Answering Agent

The **Question Answering (QA) Agent** is designed to provide accurate answers to user queries by leveraging the vector database and advanced retrieval techniques.

**Purpose:**  
 Retrieves relevant information using Retrieval-Augmented Generation (RAG) and provides comprehensive answers, always referencing file names, pages, or sections.

**Agent Setup:**
The agent uses a pre-trained language model (LLM) and is configured for efficient and accurate question answering.

```python
Agent(
    name="question_answering_agent",
    role="Question Answering Specialist",
    goal="Answer user queries using RAG and provide references.",
    backstory="Capable of navigating large text volumes for precise answers.",
    llm=llm
)
```

**Process Overview**

1. Relevant text is fetched from the vector database based on the user query.
2. The agent uses the LLM to formulate a precise response, ensuring:
   - The answer is concise but detailed.
   - References to file names and page numbers are included.
3. The answer is displayed to the user in an easily understandable format.

#### 5.3 Agent selection

The **Quiz Agent** is designed to create multiple-choice quizzes tailored to a specific topic and context. It uses a pre-trained language model to generate educational and engaging quizzes that help users learn effectively.

**Purpose:**  
 Develops quizzes with well-structured questions and plausible answer options, ensuring they are relevant to the provided topic or context.

**Agent Setup:**
The agent is initialized with a clear goal and backstory to focus on creating meaningful quizzes.

```python
Agent(
    name="quiz_agent",
    role="Quiz Creator",
    goal="Generate multiple-choice quizzes based on a specified topic and context.",
    backstory="An intelligent quiz creator capable of designing questions tailored to the context provided.",
    llm=llm
)
```

**Task Creation**
A task is generated by specifying the topic, which the agent uses to create the quiz

```python
Task(
description="Create a multiple-choice quiz on the topic.",
expected_output="A quiz with well-formulated questions and plausible answers, including references."
)
```

Users can select the Quiz Agent through the Streamlit sidebar, input a topic, and receive a tailored quiz. This agent helps users actively engage with the content, enhancing their understanding and retention of key concepts.

#### 5.4 Web Search Agent

The **Web Search Agent** is a custom agent that performs online searches using the Google Custom Search API. It retrieves relevant information, including titles, snippets, and links, and provides users with concise, actionable search results.

**How It Works:**

1. **Initialization:**  
   The agent is configured with a role and a goal to query information online using Google Custom Search. It uses a custom tool (`WebSearchTool`) to handle the API calls.

   ```python
   Agent(
       role="Web Search Agent",
       goal="Search for information online using Google Custom Search.",
       tools=[WebSearchTool()],
       llm=llm,
       backstory="You are an expert in finding accurate information online."
   )

   ```

2. **Search Query Execution:**
   When a user inputs a query in the "Online" mode, the agent sends the query to the Google API and fetches up to 5 search results. Each result includes title, snippet, link to the source.

The **Web Search Tool** is a custom tool built to integrate with the **Web Search Agent**. It allows the agent to perform Google searches programmatically using the Google Custom Search API.

3. **Concept of a Custom Tool**

A custom tool in CrewAI extends the agent's functionality by enabling specific actions. In this case, the Web Search Tool provides the capability to query Google and retrieve search results. It is designed with an input schema, a description, and a core execution function.

4. **Execution Logic:**
   The \_run method is implemented to handle the tool's core functionality—querying the Google Custom Search API. It constructs the request, sends it to Google, and parses the response to extract relevant search results.

```python
def _run(self, input: str) -> str:
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": search_engine_id,
        "q": input,
        "num": 5
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("items", [])
        return [{"title": item["title"], "snippet": item["snippet"], "link": item["link"]} for item in results]
    else:
        return [{"error": f"Error fetching search results: {response.text}"}]
```

#### 5.5 Crew Processing

The **process_input** function handles user input by dynamically selecting agents and tasks based on the search mode and agent type, then processing them sequentially. User input is stored and displayed in the chat interface using st.chat_message.

In Local Mode, the system retrieves documents from ChromaDB and creates tasks for agents such as summarizing PDFs or answering questions. The agent type determines the specific tasks to be executed. In Online Mode, the system uses a WebSearchAgent to fetch data and process it accordingly.

```python
if search_mode == "Local":
    context = retrieve_relevant_docs_from_chromadb(user_input)
    if context:
        tasks.append(create_pdf_summary_task(context=context, prompt=prompt, agent=pdf_summary_agent))
        agents.append(pdf_summary_agent)

    if agent_type == "Personalized Learning Assistant":
        tasks.append(create_qa_task(prompt=user_input, agent=qa_agent))
        agents.append(qa_agent)
    elif agent_type == "Quiz Creator":
        tasks.append(create_quiz_task(topic=user_input, agent=quiz_agent))
        agents.append(quiz_agent)

elif search_mode == "Online":
    agents.append(web_search_agent)
    tasks.append(create_web_search_task(query=user_input, agent=web_search_agent))
```

Tasks and agents are processed sequentially using the Crew module:

```python
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    verbose=True,
)
result = crew.kickoff()
```

## 6. STT and TTS Integration

#### 6.1 Speech-to-Text (STT)

The Speech-to-Text functionality, powered by **Whisper**, supports:

- **Silence Detection**: Automatically stops recording after detecting silence for a configurable duration (default: 1.5 seconds).
- **Configurable Settings**: Parameters such as language, threshold, and save paths are defined in `stt_settings.yaml`.
- **Key Functions**:
  - `listen_and_transcribe()`: Manages recording, silence detection, and transcription.
  - `record_audio_with_silence_detection()`: Captures audio chunks and saves debug files.

#### Code Example: Silence Detection in STT

```python
def record_audio_with_silence_detection(self):
    def callback(indata, frames, time, status):
        if np.abs(indata).mean() < self.silence_threshold:
            silence_counter += 1
        else:
            silence_counter = 0
        if silence_counter > self.silence_duration:
            self.running = False
    audio_data = self._capture_audio(callback)
    return self.transcribe_audio(audio_data)
```

---

#### 6.2 Text-to-Speech (TTS)

The Text-to-Speech (TTS) functionality is built using **gTTS** and **Pygame**, offering real-time audio generation and playback. Key features include:

- **Thread-Safe Design**: Ensures smooth operation in multithreaded contexts, avoiding conflicts during playback.
- **Temporary File Management**: Deletes temporary audio files after playback to prevent clutter and improve system efficiency.

#### Code Example: Playing and Stopping TTS

```python
def play_audio(self, text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    pygame.mixer.music.load(temp_audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.unlink(temp_audio_path)  # Clean up the temporary file
```

---

#### 6.3 Key Integration in Streamlit

The Streamlit app integrates STT and TTS functionalities seamlessly:

- **Start Listening**: Activates real-time transcription of audio input.
- **Speak Response**: Converts generated text responses into audio for playback.

#### Code Example: Start Listening in Streamlit

```python
if st.button("Start Listening"):
    threading.Thread(target=real_time_stt.listen_and_transcribe).start()
    st.markdown("Listening...")
```

---

#### 6.4 Sample Workflow

1. **Start Listening**: Activates real-time transcription of audio input.
2. **Play Response**: Converts the assistant's text output into speech.

This STT and TTS integration provides a robust voice interaction pipeline for personalized learning assistance.

## 7. Possible Improvements

While the current system is functional and effective, there are several areas where enhancements could be made to further improve performance and user experience.

### 7.1 Remote Vector Database

**Current State:** The system uses a local vector database (ChromaDB) for storing and retrieving embeddings.

**Improvement:** Transitioning to a remote vector database like Pinecone, FAISS, or Qdrant could improve scalability, speed, and reliability, especially for larger datasets or multi-user scenarios.

### 7.2 Content Summarization Enhancements

**Current State:** Summarization relies on basic techniques and references but may lack depth or advanced formatting.

**Improvement:** Enhance the summarization agent by:

- Leveraging more advanced LLMs.
- Adding formatting features like bullet points, tables, or visual aids.
- Allowing users to specify summarization styles or lengths.

### 7.3 Bug Fixing

**Current State:** Minor bugs or inefficiencies in document ingestion, query processing, or task execution may exist.

**Improvement:** Conduct thorough testing to identify and resolve issues, ensuring smoother functionality and error handling across the system.

### 7.4 User Experience (UX) Improvements

**Current State:** The interface is functional but may not be as intuitive or visually appealing as desired.

**Improvement:**

- Redesign the Streamlit interface for better usability.
- Add features like progress indicators, real-time status updates, and a more dynamic file management system.
- Include user feedback mechanisms for ongoing refinement.

These improvements would significantly enhance the system's performance, scalability, and overall user experience.

## 8. Conclusion

This project successfully implemented a personalized learning assistant with advanced capabilities, including content summarization, question answering, quiz generation, and web search. While the system is not without limitations, it provides a strong foundation for further development. Future improvements like remote vector databases, enhanced summarization, and UX refinements can make it even more robust and user-friendly. Overall, the project demonstrates the potential of AI-driven tools in personalized learning.

## 9. How Generative AI Helped Us Implement This Project

Generative AI was instrumental in helping structure the project efficiently. While it did not directly assist in writing code, it provided valuable guidance on organizing the workflow and creating a solid structure for the system.

### Example of AI Assistance

A prompt like _"Give me a proper structure for my challenge"_ helped define:

- Logical folder structures for different components.
- Clear separation of responsibilities (e.g., agents, tools, configurations).
- Recommendations for integrating APIs and handling tasks effectively.

By suggesting organized approaches and best practices, AI ensured the project was developed with clarity and maintainability in mind. However, its limitations became apparent with rapidly evolving tools, requiring manual research for the latest updates. Despite this, AI proved valuable for planning and structuring the project's foundation.
