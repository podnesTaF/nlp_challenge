from crewai import Agent, Task



def initialize_pdf_summary_agent(llm):
    return Agent(
          name="pdf_summary_agent",
          role="Text Summary Specialist",
          goal="Create detailed, structured summaries or reports based on the content of PDFs, including references to page numbers and file names. If no context provided, return 'no context'.",
          backstory="You are a highly trained text analysis agent designed to extract, organize, and summarize key insights from text. You specialize in creating detailed, user-friendly reports that reference specific sections, pages, and files.",
          llm=llm,
          allow_delegation=True
    )

def initialize_question_answering_agent(llm):
    return Agent(
        name="question_answering_agent",
        role="Question Answering Specialist",
        goal="Answer user queries by retrieving relevant information from the vector database and generating accurate responses using RAG.",
        backstory="You are a text analysis agent, capable of navigating large volumes of text content to provide precise answers to user questions. Your responses are concise yet comprehensive, always including references to specific sections, pages, and files.",
        llm=llm,
    )

def initialize_quiz_agent(llm):
    return Agent(
        name="quiz_agent",
        role="Quiz Creator",
        goal="Generate multiple-choice quizzes based on a specified topic and context.",
        backstory="You are an intelligent quiz creator capable of designing multiple-choice questions on any topic. Your quizzes are tailored to the context provided, making them highly relevant and educational.",
        llm=llm
    )


def create_pdf_summary_task(context, agent):
    description = f"Review the provided context and expand each topic into a full section for a report.\nThe provided context is:\n{context}\nMake sure the report is detailed and contains any and all relevant information."
    if not context:
        description += "\nNo context provided, return 'no context'."
    return Task(
        description=description,
        agent=agent,
        expected_output="A fully-fledged report with the main topics, each with a full section of information. Each section should include 'Document: [file name], page: [page number]' as a reference, followed by the summary of that page. Formatted as markdown without '```'. If no context provided, return 'no context'."
    )

def create_qa_task(prompt, agent):
    description = f"Answer the user's query: '{prompt}'."
    
    return Task(
        description=description,
        agent=agent,
        expected_output="A detailed and accurate response including retrieved context and references to the file names and pages used in the response."
    )

def create_quiz_task(topic, agent):
    description = f"Create a multiple-choice quiz on the topic: '{topic}'."
    
    return Task(
        description=description,
        agent=agent,
        expected_output="A multiple-choice quiz with well-formulated questions and answers. Each question should include plausible options, and references to the context should be included wherever applicable."
    )

def internet_search_agent(query):
    return Agent(
        
    )