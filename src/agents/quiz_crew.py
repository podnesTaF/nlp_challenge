from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class QuizCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/quiz-tasks.yaml'
    
    @agent
    def pdf_summary_agent(self) -> Agent:
      return Agent(
        config=self.agents_config['pdf_summary_agent'],
        verbose=True,
        allow_delegation=True,
      )
    
    
    @agent
    def quiz_agent(self) -> Agent:
      return Agent(
          config=self.agents_config['quiz_agent'],
          verbose=True,
      )

    @task
    def pdf_summary_task(self) -> Task:
      return Task(
        config=self.tasks_config['pdf_summary_task'],
      )

    @task
    def quiz_task(self) -> Task:
      return Task(
          config=self.tasks_config['quiz_task'],
      )

    @crew
    def crew(self) -> Crew:
      """Creates the PdfRag crew"""
      return Crew(
        agents=self.agents, # Automatically created by the @agent decorator
        tasks=self.tasks, # Automatically created by the @task decorator
        process=Process.sequential,
        verbose=True,
      )