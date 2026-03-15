"""
CrewAI agent using native crewai SDK with LLM(model="ollama/...") via LiteLLM.
Factory: create_crew(llm_model, base_url) -> dict with invoke() method
The returned object has an invoke({"messages": [HumanMessage(...)]}) interface
that internally calls crew.kickoff() and returns a LangChain-compatible result.
"""
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

try:
    from tools import analyze_data
except ImportError:
    from .tools import analyze_data


# --------------------------------------------------------------------------
# Pydantic input schema for CrewAI tool
# --------------------------------------------------------------------------
class AnalyzeDataInput(BaseModel):
    data: str = Field(description="The data string to analyze")


class AnalyzeDataTool(BaseTool):
    """CrewAI-native wrapper for the analyze_data function."""
    name: str = "analyze_data"
    description: str = "Analyzes data and returns a structured analysis result."
    args_schema: Type[BaseModel] = AnalyzeDataInput

    def _run(self, data: str) -> str:
        return analyze_data(data)


# --------------------------------------------------------------------------
# Thin wrapper to give a LangGraph-compatible invoke() interface
# --------------------------------------------------------------------------
class CrewAIAgentWrapper:
    """
    Wraps a CrewAI Crew behind a LangChain-compatible invoke() interface
    so the UAF test harness can call it uniformly.
    """
    def __init__(self, crew: Crew):
        self.crew = crew

    def invoke(self, state: dict) -> dict:
        """
        Accepts {"messages": [HumanMessage(...)]} and runs the crew.
        Returns {"messages": [..., AIMessage(content=result)]}.
        """
        from langchain_core.messages import AIMessage
        messages = state.get("messages", [])
        # Extract the user query from the last HumanMessage
        query = messages[-1].content if messages else ""

        # Dynamically update the task description with the actual query
        for task in self.crew.tasks:
            task.description = query

        result = self.crew.kickoff()
        # CrewAI kickoff returns a CrewOutput; get the string representation
        output_str = str(result)
        return {"messages": messages + [AIMessage(content=output_str)]}


def create_crew(llm_model: str = "ollama/gemma3:4b",
                base_url: str = "http://localhost:11434"):
    """
    Factory: Creates a real CrewAI crew with Ollama LLM.

    Args:
        llm_model: LiteLLM model string e.g. 'ollama/gemma3:4b'
        base_url:  Ollama server URL

    Returns:
        CrewAIAgentWrapper with a LangChain-compatible invoke() method.
    """
    llm = LLM(
        model=llm_model,
        base_url=base_url,
    )

    researcher = Agent(
        role="Senior Data Analyst",
        goal="Analyze the provided information and produce key findings",
        backstory="You are an expert analyst who synthesizes information clearly and concisely.",
        verbose=False,
        allow_delegation=False,
        tools=[AnalyzeDataTool()],
        llm=llm,
    )

    writer = Agent(
        role="Tech Content Strategist",
        goal="Write a concise summary based on the analysis findings",
        backstory="You are a skilled writer who turns analysis into clear narratives.",
        verbose=False,
        allow_delegation=False,
        llm=llm,
    )

    # Placeholder task descriptions; invoke() updates them with real queries
    task1 = Task(
        description="Analyze the following: {topic}",
        expected_output="A structured set of key findings",
        agent=researcher,
    )
    task2 = Task(
        description="Write a brief summary of the analysis findings",
        expected_output="A concise paragraph summarizing the findings",
        agent=writer,
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=False,
        process=Process.sequential,
    )
    return CrewAIAgentWrapper(crew)
