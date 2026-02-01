import os
import sys
from langchain_core.messages import HumanMessage

# Try importing ChatOllama (supports both newer and older langchain versions)
try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama

# Import the Universal Agent File Loader
from uaf_compiler.loader import UAFLoader

def main():
    # ---------------------------------------------------------
    # 1. Setup Paths
    # ---------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # The UAF file we want to load (compiled artifact)
    uaf_file = os.path.join(base_dir, "test_agent", "mathematics-reasoning-agent.uaf")
    
    if not os.path.exists(uaf_file):
        print(f"❌ Error: Agent file not found: {uaf_file}")
        print("   Please compile it first using the CLI:")
        print("   uaf compile -f test_agent/uaf_setup.yaml")
        return

    # ---------------------------------------------------------
    # 2. Initialize Runtime Dependencies
    # ---------------------------------------------------------
    # The agent functionality relies on an LLM provided by the host.
    print("🔌 Initializing Host LLM (Ollama: gemma3:4b)...")
    llm = ChatOllama(
        base_url="http://localhost:11434",
        model="gemma3:4b",
        temperature=0
    )

    # ---------------------------------------------------------
    # 3. Load the Agent
    # ---------------------------------------------------------
    try:
        print(f"📦 Loading UAF Agent from: {os.path.basename(uaf_file)}")
        
        # Initialize loader with the file path
        agent = UAFLoader(uaf_file)
        
        # Load the agent and inject dependencies (kwargs match agent factory args)
        agent_app = agent.load(llm=llm)
        
        print("✅ Agent loaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to load agent: {e}")
        return

    # ---------------------------------------------------------
    # 4. Execute the Agent
    # ---------------------------------------------------------
    query = "Calculate 10 added to 20"
    print(f"\n🚀 Invoking Agent with query: '{query}'")
    
    initial_state = {"messages": [HumanMessage(content=query)]}
    
    try:
        # Run the agent graph
        result = agent_app.invoke(initial_state)
        
        # ---------------------------------------------------------
        # 5. Inspect Results
        # ---------------------------------------------------------
        print("\n--- Execution Trace ---")
        for msg in result['messages']:
            print(f"[{type(msg).__name__}]: {msg.content}")
            
        final_msg = result['messages'][-1]
        print(f"\n🏁 Final Output: {final_msg.content}")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    main()
