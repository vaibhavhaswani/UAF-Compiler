import sys
import os
import tarfile
import yaml
import importlib.util
import tempfile
import shutil
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage

# --- User's desired logic adapted for .tar.gz (UAF implementation) ---

def load_uaf(uaf_path: str):
    """Load a Universal Agent Format file (tar.gz implementation)"""
    print(f"Loading UAF from: {uaf_path}")
    
    # Extract to temp dir for execution
    agent_dir = tempfile.mkdtemp(prefix="uaf_run_")
    with tarfile.open(uaf_path, 'r:gz') as archive:
        archive.extractall(path=agent_dir)
    
    # Add to path so imports work if needed
    sys.path.insert(0, agent_dir)
    
    # Read manifest
    with open(os.path.join(agent_dir, 'agent.yaml'), 'r') as f:
        manifest = yaml.safe_load(f)
    
    entrypoint = manifest['entrypoint']
    runtime = manifest.get('runtime', 'python')
    
    print(f"Agent Info: {manifest['name']} ({runtime})")
    
    if runtime == 'python':
        module_name, func_name = entrypoint.split(':')
        module_path = os.path.join(agent_dir, f"{module_name}.py" if not module_name.endswith('.py') else module_name)
        
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        factory_func = getattr(module, func_name)
        # Create and return the agent instance (callable/node)
        return factory_func()
    
    else:
        raise NotImplementedError(f"Runtime {runtime} not supported in this test script.")

# --- LangGraph Integration Test ---

def main():
    uaf_file = "test_agent/my-agent.uaf"
    
    # 1. Load the agent from UAF
    try:
        agent_node = load_uaf(uaf_file)
    except Exception as e:
        print(f"Failed to load UAF: {e}")
        return

    # 2. Build Graph
    print("Building StateGraph...")
    builder = StateGraph(MessagesState)
    
    # Add the loaded agent as a node
    builder.add_node("agent", agent_node)
    
    # Simple flow
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    
    graph = builder.compile()
    
    # 3. Invoke
    print("Invoking Graph...")
    initial_state = {"messages": [HumanMessage(content="Start verification")]}
    result = graph.invoke(initial_state)
    
    print("\n--- Result ---")
    print(result)
    print("Test passed!")

if __name__ == "__main__":
    main()
