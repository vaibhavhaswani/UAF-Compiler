"""
LangChain agent using ChatOllama from langchain-ollama + LangGraph.
Factory: create_agent(llm) -> CompiledStateGraph
"""
from typing import List, Literal, Annotated
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
SYSTEM_PROMPT = """You are a complex data assistant with access to the following tools:

1. calculate_complex_math: Evaluates a Python math expression. Arguments: {"expression": "string"}
2. search_database: Searches a mock database. Arguments: {"query": "string"}

To use a tool, respond ONLY with a single JSON object, no extra text:
{"action": "calculate_complex_math", "args": {"expression": "2 + 2"}}

If you have the final answer, respond ONLY with:
{"final_answer": "Your answer here"}

Do not output any text outside the JSON.
"""

def create_agent(llm):
    """
    Factory: Creates a LangChain/LangGraph agent powered by an injected LangChain LLM.
    Compatible with: ChatOllama, ChatOpenAI, etc.
    """
    if llm is None:
        raise ValueError("A LangChain LLM instance must be provided.")

    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState):
        messages = state["messages"]
        content = messages[-1].content
        try:
            data = json.loads(content.replace("```json", "").replace("```", "").strip())
            if "final_answer" in data:
                return {"messages": [AIMessage(content=data["final_answer"])]}
            action = data.get("action")
            args = data.get("args", {})
            if action == "calculate_complex_math":
                result = calculate_complex_math.invoke(args)
            elif action == "search_database":
                result = search_database.invoke(args)
            else:
                result = f"Error: Unknown tool '{action}'"
            return {"messages": [HumanMessage(content=f"Tool '{action}' returned: {result}")]}
        except json.JSONDecodeError:
            return {"messages": [HumanMessage(content="Error: Invalid JSON. Output ONLY a JSON object.")]}
        except Exception as e:
            return {"messages": [HumanMessage(content=f"Tool error: {str(e)}")]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        content = state["messages"][-1].content
        try:
            data = json.loads(content.replace("```json", "").replace("```", "").strip())
            if "final_answer" in data:
                return "__end__"
            if "action" in data:
                return "tools"
        except Exception:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    return workflow.compile()
