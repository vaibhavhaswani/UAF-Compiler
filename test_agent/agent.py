from langchain_core.messages import AIMessage
from typing import Dict, Any

# Define a simple agent node function compatible with LangGraph
def run_agent(state: Dict[str, Any]):
    print("  [Agent] Processing state...")
    messages = state.get("messages", [])
    # Simple logic: echo or respond
    response = "Processed by UAF Agent: " + str(len(messages)) + " messages so far."
    return {"messages": [AIMessage(content=response)]}

def create_agent():
    print("  [Factory] Instantiating agent node...")
    return run_agent
