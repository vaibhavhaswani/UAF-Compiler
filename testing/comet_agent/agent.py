"""
AgentComet agent using native agentcomet SDK with the Ollama provider.
Factory: create_agent(model, base_url) -> AgentCometWrapper

The wrapper provides a synchronous invoke() interface compatible with UAF test harness.
"""
from agentcomet import Agent
from agentcomet.models.providers import Ollama
from agentcomet.tools import tool

try:
    from tools import multiply
except ImportError:
    from .tools import multiply


class CometMathBot(Agent):
    """
    A concrete AgentComet agent for math operations.
    Uses the native Ollama provider for LLM calls.
    """
    def setup(self):
        self.name = "math-bot"
        self.description = "A simple math assistant that can multiply numbers."
        self.add_tools(multiply)

    def run(self, input: str) -> str:
        return self.chat(input)


class AgentCometWrapper:
    """
    Wraps an AgentComet agent behind a LangChain-compatible invoke() interface.
    """
    def __init__(self, agent: Agent):
        self.agent = agent

    def invoke(self, state: dict) -> dict:
        """
        Accepts {"messages": [HumanMessage(...)]} and runs the AgentComet agent.
        Returns {"messages": [..., AIMessage(content=result)]}.
        """
        from langchain_core.messages import AIMessage
        messages = state.get("messages", [])
        query = messages[-1].content if messages else ""

        response = self.agent.run(query)
        return {"messages": messages + [AIMessage(content=response)]}


def create_agent(model: str = "gemma3:4b",
                 base_url: str = "http://localhost:11434"):
    """
    Factory: Creates a real AgentComet agent powered by the native Ollama provider.

    Args:
        model:    Ollama model name e.g. 'gemma3:4b'
        base_url: Ollama server URL

    Returns:
        AgentCometWrapper with a LangChain-compatible invoke() method.
    """
    ollama_llm = Ollama(model=model, base_url=base_url, temperature=0)
    agent = CometMathBot(llm=ollama_llm)
    return AgentCometWrapper(agent)
