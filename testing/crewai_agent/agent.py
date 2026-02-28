
from crewai import Agent, Task, Crew, Process
from tools import tools
from langchain_openai import ChatOpenAI

def create_crew():
    # Fake LLM
    llm = ChatOpenAI(openai_api_key="fake-key", model="gpt-4")
    
    researcher = Agent(
        role='Senior Data Analyst',
        goal='Analyze complex datasets',
        backstory='Expert analyst from a top tech firm.',
        verbose=True,
        allow_delegation=False,
        tools=tools,
        llm=llm
    )
    
    writer = Agent(
        role='Tech Content Strategist',
        goal='Craft compelling narratives from data',
        backstory='Renowned content strategist.',
        verbose=True,
        allow_delegation=True,
        llm=llm
    )
    
    task1 = Task(description='Analyze 2024 trends', expected_output='Trend report', agent=researcher)
    task2 = Task(description='Write blog post based on trends', expected_output='Blog post', agent=writer)
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,
        process=Process.sequential
    )
    return crew
