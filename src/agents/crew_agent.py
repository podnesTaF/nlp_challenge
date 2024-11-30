from crewai import Agent, Task


def initialize_qa_agent(llm):

    return Agent(
        name="question_answering_agent",
        role="Question Answering Specialist",
        goal="Answer user queries by retrieving relevant information from the vector database and generating accurate responses using RAG.",
        backstory="You're a knowledgeable assistant capable of combining retrieved content with LLM capabilities to deliver precise answers.",
        llm=llm
    )


def create_qa_task(prompt, agent, context=None):
    description = f"Answer the user's query: '{prompt}'."
   
    if context:
        context_str = "\n".join(
            [
                f"Reference {i+1}: {entry['content']} (file name: {entry['metadata']})"
                for i, entry in enumerate(context)
            ]
        )
        description += f" Include the following context:\n{context_str}"

    return Task(
        description=description,
        agent=agent,
        expected_output="A detailed and accurate response including retrieved context and references to the file names which used in response."
    )