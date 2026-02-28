from typing import Dict, Any, List, Literal, Annotated, Union
from typing_extensions import TypedDict
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

# Import tools
try:
    from tools.math_tools import add, multiply
except ImportError:
    from .tools.math_tools import add, multiply

# --- State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- Nodes ---

SYSTEM_PROMPT = """You are a mathematical reasoning assistant. 
You can calculate answers using the following tools:

1. add: Add two numbers. Arguments: {"a": number, "b": number}
2. multiply: Multiply two numbers. Arguments: {"a": number, "b": number}

To use a tool, you MUST respond with ONLY a JSON object in the following format:
{
    "action": "add",
    "args": {"a": 1, "b": 2}
}

If you have the final answer, respond with a JSON object:
{
    "final_answer": "The answer is 3"
}

Do not output any text outside the JSON.
"""

def create_agent(llm):
    """
    Factory function to create the math reasoning agent.
    """
    if llm is None:
        raise ValueError("An LLM instance must be provided.")
    
    # We do NOT use bind_tools here because the model might not support native tool calling.
    # Instead, we rely on the system prompt and parsing.

    def call_model(state: AgentState):
        messages = state["messages"]
        
        # Ensure system prompt is present
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            
        response = llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content
        
        # Parse JSON
        try:
            # simple cleanup for markdown code blocks if any
            clean_content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_content)
            
            if "final_answer" in data:
                # We are done, but we need to signal that.
                # Actually, the 'should_continue' logic handles the flow.
                # Here we strictly run tools. If we got final answer, this node shouldn't be validly reached 
                # unless logic sent us here.
                 return {"messages": [AIMessage(content=data["final_answer"])]}
            
            action = data.get("action")
            args = data.get("args", {})
            
            result = None
            if action == "add":
                result = add.invoke(args)
            elif action == "multiply":
                result = multiply.invoke(args)
            else:
                result = f"Error: Unknown tool '{action}'"
            
            # Return result as a ToolMessage (conceptually), but since we are doing manual ReAct,
            # we can just return a HumanMessage or SystemMessage representing the tool output 
            # so the model sees it.
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
            # If parsing fails, we might want to loop back to let the model retry (via call_tools error msg)
            # But strictly, call_tools node is where we handle execution.
            # If we decide to go to 'tools', call_tools will run and see the garbage and return error.
            return "tools"
            
        return "__end__"

    # --- Graph ---
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    
    workflow.add_edge(START, "agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    app = workflow.compile()
    return app
