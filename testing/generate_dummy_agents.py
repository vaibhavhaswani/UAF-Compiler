
import os
import yaml

base_dir = r"d:\Projects\Personal\DefaultLoop\UAF Compiler\testing"
os.makedirs(base_dir, exist_ok=True)

# 1. Complex LangChain Agent
lc_dir = os.path.join(base_dir, "langchain_agent")
os.makedirs(lc_dir, exist_ok=True)

with open(os.path.join(lc_dir, "agent.yaml"), "w") as f:
    f.write("""uaf_version: 2
agent:
  name: "langchain_complex"
  version: "1.0.0"
  description: "LangChain complex testing"
  author: "Tester"
runtime:
  engine: "python"
  entrypoint: "agent:create_agent"
sdk:
  name: "langchain"
  version: "0.1.0"
tools:
  builtin: []
  custom: ["calculate_complex_math", "search_database"]
state:
  enabled: false
dependencies:
  auto: true
""")

with open(os.path.join(lc_dir, "tools.py"), "w") as f:
    f.write("""
from langchain.tools import tool

@tool
def calculate_complex_math(expression: str) -> str:
    \"\"\"Calculates complex math.\"\"\"
    return "42"

@tool
def search_database(query: str) -> str:
    \"\"\"Searches a mock database.\"\"\"
    return "Mock Result for: " + query

tools = [calculate_complex_math, search_database]
""")

with open(os.path.join(lc_dir, "agent.py"), "w") as f:
    f.write("""
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tools import tools

def create_agent():
    # We don't need a real key just to instantiate the object in LangChain usually, 
    # but we will just return a configured object or a wrapper
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly complex agent."),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Fake LLM for testing instantiation
    llm = ChatOpenAI(openai_api_key="fake-key", model="gpt-3.5-turbo")
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor
""")

with open(os.path.join(lc_dir, "requirements.txt"), "w") as f:
    f.write("langchain\nlangchain-openai\nlangchain-core\n")

# 2. Complex CrewAI Agent
crew_dir = os.path.join(base_dir, "crewai_agent")
os.makedirs(crew_dir, exist_ok=True)

with open(os.path.join(crew_dir, "agent.yaml"), "w") as f:
    f.write("""uaf_version: 2
agent:
  name: "crewai_complex"
  version: "1.0.0"
  description: "CrewAI complex testing"
  author: "Tester"
runtime:
  engine: "python"
  entrypoint: "agent:create_crew"
sdk:
  name: "crewai"
  version: "0.1.0"
tools:
  builtin: []
  custom: ["analyze_data"]
state:
  enabled: false
dependencies:
  auto: true
""")

with open(os.path.join(crew_dir, "tools.py"), "w") as f:
    f.write("""
from langchain.tools import tool

@tool
def analyze_data(data: str) -> str:
    \"\"\"Analyzes data.\"\"\"
    return "Analyzed: " + data

tools = [analyze_data]
""")

with open(os.path.join(crew_dir, "agent.py"), "w") as f:
    f.write("""
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
""")

with open(os.path.join(crew_dir, "requirements.txt"), "w") as f:
    f.write("crewai\nlangchain-openai\n")

# 3. Complex Google ADK Agent
adk_dir = os.path.join(base_dir, "adk_agent")
os.makedirs(adk_dir, exist_ok=True)

with open(os.path.join(adk_dir, "agent.yaml"), "w") as f:
    f.write("""uaf_version: 2
agent:
  name: "adk_complex"
  version: "1.0.0"
  description: "ADK complex testing"
  author: "Tester"
runtime:
  engine: "python"
  entrypoint: "agent:create_agent"
sdk:
  name: "google-adk"
  version: "0.1.0"
tools:
  builtin: []
  custom: ["fetch_weather", "get_stock_price"]
state:
  enabled: false
dependencies:
  auto: true
""")

with open(os.path.join(adk_dir, "tools.py"), "w") as f:
    f.write("""
def fetch_weather(location: str):
    return {"temp": 72, "conditions": "Sunny"}

def get_stock_price(ticker: str):
    return {"price": 150.0}

tools = [fetch_weather, get_stock_price]
""")

with open(os.path.join(adk_dir, "agent.py"), "w") as f:
    f.write("""
import google.generativeai as genai
from tools import tools

def create_agent():
    # Complex Configuration
    genai.configure(api_key="fake-key")
    
    generation_config = {
      "temperature": 0.9,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }

    # Model instantiation with tools
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        tools=tools
    )
    
    return model
""")

with open(os.path.join(adk_dir, "requirements.txt"), "w") as f:
    f.write("google-generativeai\n")

# 4. Complex AgentComet Agent
comet_dir = os.path.join(base_dir, "comet_agent")
os.makedirs(comet_dir, exist_ok=True)

with open(os.path.join(comet_dir, "agent.yaml"), "w") as f:
    f.write("""uaf_version: 2
agent:
  name: "math-bot"
  version: "0.1.0"
  description: "Simple math assistant"
  author: "Vaibhav"
runtime:
  engine: "python"
  entrypoint: "agent:MyAgent"
sdk:
  name: "agentcomet"
  version: "0.1.0"
tools:
  builtin:
    - "read"
    - "write"
    - "calculator"
  custom:
    - "multiply"
state:
  enabled: true
  file: "agent.state"
dependencies:
  auto: true
""")

with open(os.path.join(comet_dir, "tools.py"), "w") as f:
    f.write("""
from agentcomet.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    return a * b
""")

with open(os.path.join(comet_dir, "agent.state"), "w") as f:
    f.write("{}")

with open(os.path.join(comet_dir, "agent.py"), "w") as f:
    f.write("""
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
""")

with open(os.path.join(comet_dir, "requirements.txt"), "w") as f:
    f.write("uaf-compiler\nrequests\n")

print("Generated dummy agent directories.")
