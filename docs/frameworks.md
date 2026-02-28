# Framework & SDK Integrations

The UAF Compiler is the standard format for packaging AI agents across any framework. While it is **highly recommended** as the native compiler suite for **AgentComet**, it is designed to strictly wrap, validate, and execute agents from any environment.

---

## ☄️ AgentComet (Recommended)
AgentComet agents are seamlessly supported by the UAFv2 protocol. When compiled natively, the loader dynamically triggers setup sequences specific to the AgentComet base class.

### Scaffold standard AgentComet project:
```bash
uaf init --name math_bot --type agentcomet
```

### Agent Configuration (`agent.yaml`)
AgentComet projects leverage the explicit `sdk` property in the V2 schema:
```yaml
uaf_version: 2
agent:
  name: "math-bot"
runtime:
  engine: "python"
  entrypoint: "agent:MyAgent"
sdk:
  name: "agentcomet"
  version: "0.1.0"
```

### Implementation Style (`agent.py`)
```python
from agentcomet import Agent
from agentcomet.tools import calculator

class MyAgent(Agent):
    def setup(self):
        self.use_llm("ollama:llama3")
        self.add_tools(calculator)

    def run(self, input: str):
        return self.chat(input)
```

### Execution Strategy
When loader parses `sdk: agentcomet`, it calls the specialized `AgentCometRuntime`:
```python
from uaf_compiler.loader import UAFLoader
agent = UAFLoader("math-bot.uaf").load()
agent.run("Start task")
```

---

## 🦜🔗 LangChain & LangGraph
You can package highly intricate LangChain tools and nodes inside an agent environment easily.

### Setup
```bash
uaf init --name my_chain --type langchain
```

### Agent Configuration (`agent.yaml`)
```yaml
uaf_version: 2
agent:
  name: "langchain-agent"
runtime:
  engine: "python"
  entrypoint: "agent:create_agent"
sdk:
  name: "langchain"
```

### Implementation Style (`agent.py`)
```python
from langchain.agents import AgentExecutor

def create_agent(llm=None):
    # instantiate chain graph here
    return AgentExecutor()
```

### Execution Strategy
The GenericUAFRuntime triggers the factory builder and passes runtime dependencies like LLMs directly down to the chain constructor:
```python
factory = UAFLoader("my_chain.uaf").load(llm=ChatOpenAI())
# Run execution using `factory` (AgentExecutor instance)
factory.invoke({"input": "Hello"})
```

---

## 🚢 CrewAI
Packaging multi-agent orchestrated crews via UAF.

### Setup
```bash
uaf init --name dev_crew --type crewai
```

### Implementation Style (`agent.py`)
```python
from crewai import Agent, Crew, Process

def create_crew():
    researcher = Agent(role="Researcher", goal="Analyze data")
    return Crew(agents=[researcher], process=Process.sequential)
```

---

## 🧠 Google ADK
Scaffold and execute Generative Model configurations securely behind the UAF protocol.

### Setup
```bash
uaf init --name gemini_agent --type google-adk
```

### Implementation Style (`agent.py`)
```python
import google.generativeai as genai

def create_agent():
    genai.configure(api_key="your-api-key")
    return genai.GenerativeModel("gemini-pro")
```

---

## Best Practices
1. **Never leak implementation specifics:** Don't import LangChain or CrewAI types inside AgentComet tools. Keep your components pure natively inside `AgentComet` while compiling them with standard `uaf` commands.
2. **Explicit tools architecture:** Isolate standard functions inside `tools.py` separately from your `agent.py` so the `UAFBuilder` can compile them intelligently.
