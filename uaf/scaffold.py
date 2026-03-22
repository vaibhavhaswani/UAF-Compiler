import os
import yaml

class Scaffold:
    TEMPLATES = {
        "agentcomet": {
            "agent.py": """
from agentcomet import Agent
from agentcomet.tools import read, write, calculator
from tools import multiply

class MyAgent(Agent):

    def setup(self):
        self.use_llm("ollama:llama3")
        self.enable_memory()
        self.add_tools(read, write, calculator, multiply)

    def run(self, input: str):
        return self.chat(input)
""",
            "tools.py": """
from agentcomet.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    return a * b
""",
            "agent.state": """
{}
""",
            "requirements.txt": """
agentcomet
""",
            "agent.yaml": """
uaf_version: 2

agent:
  name: "{name}"
  version: 0.1.0
  description: Simple math assistant
  author: Unknown

runtime:
  engine: python
  entrypoint: agent:MyAgent

sdk:
  name: agentcomet
  version: 0.1.0

tools:
  builtin:
    - read
    - write
    - calculator
  custom:
    - multiply

state:
  enabled: true
  file: agent.state

dependencies:
  auto: true
"""
        },
        "langchain": {
            "agent.py": """
from langchain.agents import AgentExecutor
# from tools import tools

def create_agent():
    # Placeholder for LangChain agent creation
    # agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor()
""",
            "tools.py": """
from langchain.tools import tool

@tool
def example_tool():
    "An example tool."
    return "example"

tools = [example_tool]
""",
            "requirements.txt": """
langchain
uaf-compiler
""",
            "agent.yaml": """
uaf_version: 2

agent:
  name: "{name}"
  version: 0.1.0
  description: LangChain Agent
  author: Unknown

runtime:
  engine: python
  entrypoint: agent:create_agent

sdk:
  name: langchain
  version: 0.1.0

tools:
  builtin: []
  custom:
    - example_tool

state:
  enabled: false

dependencies:
  auto: true
"""
        },
        "langgraph": {
            "agent.py": """
from langgraph.graph import StateGraph
# from tools import tools

def create_agent():
    # Placeholder for LangGraph agent creation
    graph = StateGraph()
    return graph.compile()
""",
            "tools.py": """
# Define your LangGraph nodes/tools here
tools = []
""",
            "requirements.txt": """
langgraph
uaf-compiler
""",
            "agent.yaml": """
uaf_version: 2

agent:
  name: "{name}"
  version: 0.1.0
  description: LangGraph Agent
  author: Unknown

runtime:
  engine: python
  entrypoint: agent:create_agent

sdk:
  name: langgraph
  version: 0.1.0

tools:
  builtin: []
  custom: []

state:
  enabled: false

dependencies:
  auto: true
"""
        },
        "crewai": {
            "agent.py": """
from crewai import Agent, Task, Crew
# from tools import tools

def create_crew():
    # Placeholder for CrewAI creation
    return Crew(agents=[], tasks=[])
""",
            "tools.py": """
from langchain.tools import tool

# CrewAI uses LangChain tools
tools = []
""",
            "requirements.txt": """
crewai
uaf-compiler
""",
            "agent.yaml": """
uaf_version: 2

agent:
  name: "{name}"
  version: 0.1.0
  description: CrewAI Agent
  author: Unknown

runtime:
  engine: python
  entrypoint: agent:create_crew

sdk:
  name: crewai
  version: 0.1.0

tools:
  builtin: []
  custom: []

state:
  enabled: false

dependencies:
  auto: true
"""
        },
        "google-adk": {
            "agent.py": """
# Google GenAI ADK Agent
# from tools import tools

def create_agent():
    pass
""",
            "tools.py": """
# Define Google ADK functions here
tools = []
""",
            "requirements.txt": """
google-generativeai
uaf-compiler
""",
            "agent.yaml": """
uaf_version: 2

agent:
  name: "{name}"
  version: 0.1.0
  description: Google ADK Agent
  author: Unknown

runtime:
  engine: python
  entrypoint: agent:create_agent

sdk:
  name: google-adk
  version: 0.1.0

tools:
  builtin: []
  custom: []

state:
  enabled: false

dependencies:
  auto: true
"""
        }
    }

    @staticmethod
    def generate(name: str, agent_type: str, destination: str = "."):
        if agent_type not in Scaffold.TEMPLATES:
            raise ValueError(f"Unknown agent type: {agent_type}. Supported: {list(Scaffold.TEMPLATES.keys())}")

        target_dir = os.path.join(destination, name)
        if os.path.exists(target_dir):
            raise FileExistsError(f"Directory {target_dir} already exists.")

        os.makedirs(target_dir)
        print(f"Created agent directory: {target_dir}")

        templates = Scaffold.TEMPLATES[agent_type]
        for filename, content in templates.items():
            file_path = os.path.join(target_dir, filename)
            # Format content if needed (like injecting name into yaml)
            if filename == "agent.yaml":
                content = content.format(name=name)
            
            with open(file_path, "w") as f:
                f.write(content.strip())
            print(f"  - Created {filename}")
        
        print(f"Successfully initialized {agent_type} agent '{name}' in {target_dir}")
