
import os
import yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(base_dir, exist_ok=True)

# 1. Complex LangChain Agent
lc_dir = os.path.join(base_dir, "langchain_agent")
os.makedirs(lc_dir, exist_ok=True)

with open(os.path.join(lc_dir, "agent.yaml"), "w") as f:
    f.write("""uaf_version: 2
agent:
  name: "langchain_complex"
  version: "1.0.0"
  description: "LangChain complex agent with math and database tools"
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
    f.write("""from langchain_core.tools import tool

@tool
def calculate_complex_math(expression: str) -> str:
    \"\"\"Evaluates a math expression and returns the result.\"\"\"
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def search_database(query: str) -> str:
    \"\"\"Searches a mock database and returns results.\"\"\"
    return "Mock Result for: " + query

tools = [calculate_complex_math, search_database]
""")

with open(os.path.join(lc_dir, "agent.py"), "w") as f:
    f.write("""from typing import List, Literal, Annotated
from typing_extensions import TypedDict
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

try:
    from tools import tools, calculate_complex_math, search_database
except ImportError:
    from .tools import tools, calculate_complex_math, search_database

# --- State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- System Prompt ---
SYSTEM_PROMPT = \"\"\"You are a complex data assistant with access to the following tools:

1. calculate_complex_math: Evaluates a math expression. Arguments: {"expression": "string"}
2. search_database: Searches a mock database. Arguments: {"query": "string"}

To use a tool, respond ONLY with a JSON object:
{
    "action": "calculate_complex_math",
    "args": {"expression": "2 + 2"}
}

If you have the final answer, respond with:
{
    "final_answer": "Your answer here"
}

Do not output any text outside the JSON.
\"\"\"

def create_agent(llm):
    if llm is None:
        raise ValueError("An LLM instance must be provided.")

    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return {"messages": [AIMessage(content=data["final_answer"])]}
            action = data.get("action")
            args = data.get("args", {})
            result = None
            if action == "calculate_complex_math":
                result = calculate_complex_math.invoke(args)
            elif action == "search_database":
                result = search_database.invoke(args)
            else:
                result = f"Error: Unknown tool '{action}'"
            return {"messages": [HumanMessage(content=f"Tool '{action}' returned: {result}")]}
        except json.JSONDecodeError:
            return {"messages": [HumanMessage(content="Error: Invalid JSON format. Please output ONLY JSON.")]}
        except Exception as e:
            return {"messages": [HumanMessage(content=f"Error executing tool: {str(e)}")]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return "__end__"
            if "action" in data:
                return "tools"
        except:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    app = workflow.compile()
    return app
""")

with open(os.path.join(lc_dir, "requirements.txt"), "w") as f:
    f.write("langchain-core\nlanggraph\n")

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
    f.write("""from langchain_core.tools import tool

@tool
def analyze_data(data: str) -> str:
    \"\"\"Analyzes data and returns a structured analysis result.\"\"\"
    return "Analysis complete. Key findings from: " + data

tools = [analyze_data]
""")

with open(os.path.join(crew_dir, "agent.py"), "w") as f:
    f.write("""from typing import List, Literal, Annotated
from typing_extensions import TypedDict
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

try:
    from tools import tools, analyze_data
except ImportError:
    from .tools import tools, analyze_data

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

SYSTEM_PROMPT = \"\"\"You are a crew of two AI agents working together:

1. **Researcher**: Analyzes data using the analyze_data tool.
2. **Writer**: Writes summaries based on analysis results.

You have access to the following tool:
- analyze_data: Analyzes data input. Arguments: {"data": "string"}

To use a tool, respond ONLY with a JSON object:
{
    "action": "analyze_data",
    "args": {"data": "some data to analyze"}
}

If you have the final answer, respond with:
{
    "final_answer": "Your summary here"
}

Do not output any text outside the JSON.
\"\"\"

def create_crew(llm):
    if llm is None:
        raise ValueError("An LLM instance must be provided.")

    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return {"messages": [AIMessage(content=data["final_answer"])]}
            action = data.get("action")
            args = data.get("args", {})
            result = None
            if action == "analyze_data":
                result = analyze_data.invoke(args)
            else:
                result = f"Error: Unknown tool '{action}'"
            return {"messages": [HumanMessage(content=f"Tool '{action}' returned: {result}")]}
        except json.JSONDecodeError:
            return {"messages": [HumanMessage(content="Error: Invalid JSON format. Please output ONLY JSON.")]}
        except Exception as e:
            return {"messages": [HumanMessage(content=f"Error executing tool: {str(e)}")]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return "__end__"
            if "action" in data:
                return "tools"
        except:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    app = workflow.compile()
    return app
""")

with open(os.path.join(crew_dir, "requirements.txt"), "w") as f:
    f.write("langchain-core\nlanggraph\n")

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
    f.write("""from langchain_core.tools import tool

@tool
def fetch_weather(location: str) -> str:
    \"\"\"Gets the current weather for a given location.\"\"\"
    return f'{{"temp": 72, "conditions": "Sunny", "location": "{location}"}}'

@tool
def get_stock_price(ticker: str) -> str:
    \"\"\"Gets the current stock price for a given ticker symbol.\"\"\"
    return f'{{"price": 150.0, "ticker": "{ticker}"}}'

tools = [fetch_weather, get_stock_price]
""")

with open(os.path.join(adk_dir, "agent.py"), "w") as f:
    f.write("""from typing import List, Literal, Annotated
from typing_extensions import TypedDict
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

try:
    from tools import tools, fetch_weather, get_stock_price
except ImportError:
    from .tools import tools, fetch_weather, get_stock_price

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

SYSTEM_PROMPT = \"\"\"You are a helpful assistant that can fetch weather and stock data.

You have access to the following tools:

1. fetch_weather: Gets the weather for a location. Arguments: {"location": "string"}
2. get_stock_price: Gets the stock price for a ticker. Arguments: {"ticker": "string"}

To use a tool, respond ONLY with a JSON object:
{
    "action": "fetch_weather",
    "args": {"location": "New York"}
}

If you have the final answer, respond with:
{
    "final_answer": "Your answer here"
}

Do not output any text outside the JSON.
\"\"\"

def create_agent(llm):
    if llm is None:
        raise ValueError("An LLM instance must be provided.")

    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return {"messages": [AIMessage(content=data["final_answer"])]}
            action = data.get("action")
            args = data.get("args", {})
            result = None
            if action == "fetch_weather":
                result = fetch_weather.invoke(args)
            elif action == "get_stock_price":
                result = get_stock_price.invoke(args)
            else:
                result = f"Error: Unknown tool '{action}'"
            return {"messages": [HumanMessage(content=f"Tool '{action}' returned: {result}")]}
        except json.JSONDecodeError:
            return {"messages": [HumanMessage(content="Error: Invalid JSON format. Please output ONLY JSON.")]}
        except Exception as e:
            return {"messages": [HumanMessage(content=f"Error executing tool: {str(e)}")]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return "__end__"
            if "action" in data:
                return "tools"
        except:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    app = workflow.compile()
    return app
""")

with open(os.path.join(adk_dir, "requirements.txt"), "w") as f:
    f.write("langchain-core\nlanggraph\n")

# 4. Comet Agent (math bot)
comet_dir = os.path.join(base_dir, "comet_agent")
os.makedirs(comet_dir, exist_ok=True)

with open(os.path.join(comet_dir, "agent.yaml"), "w") as f:
    f.write("""uaf_version: 2
agent:
  name: "math-bot"
  version: "0.1.0"
  description: "Simple math assistant bot"
  author: "Vaibhav"
runtime:
  engine: "python"
  entrypoint: "agent:create_agent"
sdk:
  name: "langgraph"
  version: "0.1.0"
tools:
  builtin: []
  custom:
    - "multiply"
state:
  enabled: false
dependencies:
  auto: true
""")

with open(os.path.join(comet_dir, "tools.py"), "w") as f:
    f.write("""from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> str:
    \"\"\"Multiplies two numbers and returns the result.\"\"\"
    return str(a * b)

tools = [multiply]
""")

with open(os.path.join(comet_dir, "agent.state"), "w") as f:
    f.write("{}")

with open(os.path.join(comet_dir, "agent.py"), "w") as f:
    f.write("""from typing import List, Literal, Annotated
from typing_extensions import TypedDict
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

try:
    from tools import tools, multiply
except ImportError:
    from .tools import tools, multiply

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

SYSTEM_PROMPT = \"\"\"You are a simple math assistant bot.

You have access to the following tool:
- multiply: Multiplies two numbers. Arguments: {"a": number, "b": number}

To use a tool, respond ONLY with a JSON object:
{
    "action": "multiply",
    "args": {"a": 5, "b": 3}
}

If you have the final answer, respond with:
{
    "final_answer": "Your answer here"
}

Do not output any text outside the JSON.
\"\"\"

def create_agent(llm):
    if llm is None:
        raise ValueError("An LLM instance must be provided.")

    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return {"messages": [AIMessage(content=data["final_answer"])]}
            action = data.get("action")
            args = data.get("args", {})
            result = None
            if action == "multiply":
                result = multiply.invoke(args)
            else:
                result = f"Error: Unknown tool '{action}'"
            return {"messages": [HumanMessage(content=f"Tool '{action}' returned: {result}")]}
        except json.JSONDecodeError:
            return {"messages": [HumanMessage(content="Error: Invalid JSON format. Please output ONLY JSON.")]}
        except Exception as e:
            return {"messages": [HumanMessage(content=f"Error executing tool: {str(e)}")]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            if "final_answer" in data:
                return "__end__"
            if "action" in data:
                return "tools"
        except:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    app = workflow.compile()
    return app
""")

with open(os.path.join(comet_dir, "requirements.txt"), "w") as f:
    f.write("langchain-core\nlanggraph\n")

print("Generated dummy agent directories.")
