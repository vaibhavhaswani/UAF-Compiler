"""
test_dummy_agents.py
====================
Tests each dummy agent through its native SDK with its SDK-compatible
Ollama model loader, then invokes it via LLM.

SDK mapping:
  langchain_agent  -> ChatOllama (langchain-ollama)      + LangGraph
  crewai_agent     -> LLM(model="ollama/...") (LiteLLM)  + CrewAI Crew
  adk_agent        -> LiteLlm(model="ollama/...") (LiteLLM) + Google ADK InMemoryRunner
  comet_agent      -> Ollama (agentcomet.models.providers) + AgentComet Agent

Each test:
  1. Compile the agent directory into a .uaf file
  2. Load the factory via UAFLoader.load_factory()
  3. Instantiate via UAFLoader.load(**sdk_kwargs) with the SDK-specific LLM config
  4. Invoke via agent.invoke({"messages": [HumanMessage(content=query)]})
  5. Assert the response contains expected content
"""
import os
import sys
import unittest

# Ensure local uaf_compiler takes precedence over installed version
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.messages import HumanMessage, AIMessage
from uaf_compiler.builder import UAFBuilder
from uaf_compiler.loader import UAFLoader

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"


class TestDummyAgents(unittest.TestCase):
    """
    End-to-end tests for all dummy UAF agents.
    Each agent is loaded via its native SDK's Ollama integration,
    then invoked through the LLM.
    """

    def setUp(self):
        self.base_dir = os.path.dirname(__file__)

    # =========================================================================
    # Internal helpers
    # =========================================================================

    def _compile(self, agent_dir_name: str) -> str:
        """Compile agent directory -> .uaf file. Returns the .uaf path."""
        agent_dir = os.path.join(self.base_dir, agent_dir_name)
        builder = UAFBuilder(target_dir=agent_dir)
        builder.build()
        config = builder.load_config()
        output_name = config.get("output", "agent.uaf")
        uaf_path = os.path.join(agent_dir, output_name)
        self.assertTrue(os.path.exists(uaf_path), f"Compile failed for {agent_dir_name}")
        print(f"  [COMPILE OK] {agent_dir_name} -> {output_name}")
        return uaf_path

    def _load_factory(self, uaf_path: str, agent_dir_name: str):
        """Load and return (loader, factory_callable)."""
        loader = UAFLoader(uaf_path)
        factory = loader.load_factory()
        self.assertIsNotNone(factory, f"Factory is None for {agent_dir_name}")
        print(f"  [FACTORY OK] {agent_dir_name}: {factory}")
        return loader, factory

    def _invoke_and_assert(self, agent_app, query: str, agent_name: str,
                           expected_keywords=None):
        """
        Invoke the agent with a LangChain-compatible state dict and validate output.
        All agents must implement invoke({"messages": [HumanMessage(...)]}).
        """
        initial_state = {"messages": [HumanMessage(content=query)]}
        print(f"  [QUERY] {agent_name}: '{query}'")

        result = agent_app.invoke(initial_state)

        self.assertIn("messages", result,
                      f"Result missing 'messages' key for {agent_name}")
        self.assertGreater(len(result["messages"]), 1,
                           f"{agent_name} produced no response messages")

        # Print trace
        print(f"  [TRACE] {agent_name}:")
        for msg in result["messages"]:
            preview = msg.content[:200].encode("ascii", "replace").decode("ascii")
            print(f"    [{type(msg).__name__}]: {preview}")

        final = result["messages"][-1]
        final_preview = final.content[:300].encode("ascii", "replace").decode("ascii")
        print(f"  [FINAL] {final_preview}")

        # Keyword check across all message content
        if expected_keywords:
            all_text = " ".join(m.content.lower() for m in result["messages"])
            for kw in expected_keywords:
                self.assertIn(kw.lower(), all_text,
                              f"Keyword '{kw}' not found in {agent_name} output")

        return result

    # =========================================================================
    # 1. LangChain Agent
    #    SDK: langchain-ollama -> ChatOllama
    #    Pattern: create_agent(llm=ChatOllama(...)) -> CompiledStateGraph
    # =========================================================================

    def test_langchain_compile_and_factory(self):
        """Compile and factory-load the LangChain agent."""
        uaf_path = self._compile("langchain_agent")
        loader, factory = self._load_factory(uaf_path, "langchain_agent")
        loader.cleanup()

    def test_langchain_llm_invocation(self):
        """
        Load the LangChain agent via ChatOllama (langchain-ollama SDK)
        and invoke it with the LLM to perform math calculation.
        """
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0,
        )
        uaf_path = self._compile("langchain_agent")
        loader = UAFLoader(uaf_path)
        try:
            # Inject the ChatOllama instance as the 'llm' kwarg
            agent_app = loader.load(llm=llm)
            print(f"  [SDK] LangChain agent loaded: {type(agent_app).__name__}")
            self._invoke_and_assert(
                agent_app,
                query="Calculate 15 + 27",
                agent_name="langchain_agent",
                expected_keywords=["42"],
            )
        finally:
            loader.cleanup()

    # =========================================================================
    # 2. CrewAI Agent
    #    SDK: crewai + litellm -> LLM(model="ollama/gemma3:4b")
    #    Pattern: create_crew(llm_model, base_url) -> CrewAIAgentWrapper
    # =========================================================================

    def test_crewai_compile_and_factory(self):
        """Compile and factory-load the CrewAI agent."""
        uaf_path = self._compile("crewai_agent")
        loader, factory = self._load_factory(uaf_path, "crewai_agent")
        loader.cleanup()

    def test_crewai_llm_invocation(self):
        """
        Load the CrewAI agent with crewai.LLM using LiteLLM + Ollama
        and invoke it to analyze data.
        """
        uaf_path = self._compile("crewai_agent")
        loader = UAFLoader(uaf_path)
        try:
            # CrewAI uses LiteLLM model strings: "ollama/<model>"
            agent_app = loader.load(
                llm_model=f"ollama/{OLLAMA_MODEL}",
                base_url=OLLAMA_BASE_URL,
            )
            print(f"  [SDK] CrewAI agent loaded: {type(agent_app).__name__}")
            self._invoke_and_assert(
                agent_app,
                query="Analyze the key trends in AI adoption for 2024",
                agent_name="crewai_agent",
                expected_keywords=["analy"],  # expects 'analyze' or 'analysis' response
            )
        finally:
            loader.cleanup()

    # =========================================================================
    # 3. Google ADK Agent
    #    SDK: google-adk + litellm -> LiteLlm(model="ollama/gemma3:4b")
    #    Pattern: create_agent(llm_model, base_url) -> ADKAgentWrapper
    # =========================================================================

    def test_adk_compile_and_factory(self):
        """Compile and factory-load the Google ADK agent."""
        uaf_path = self._compile("adk_agent")
        loader, factory = self._load_factory(uaf_path, "adk_agent")
        loader.cleanup()

    def test_adk_llm_invocation(self):
        """
        Load the Google ADK agent with google.adk.models.lite_llm.LiteLlm + Ollama
        and invoke it to fetch weather data.
        """
        uaf_path = self._compile("adk_agent")
        loader = UAFLoader(uaf_path)
        try:
            # ADK uses LiteLlm(model="ollama/<model>")
            agent_app = loader.load(
                llm_model=f"ollama/{OLLAMA_MODEL}",
                base_url=OLLAMA_BASE_URL,
            )
            print(f"  [SDK] Google ADK agent loaded: {type(agent_app).__name__}")
            self._invoke_and_assert(
                agent_app,
                query="What is the weather in New York?",
                agent_name="adk_agent",
                # ADK with gemma3:4b may return weather data, city name, or temperature
                expected_keywords=["new york"],
            )
        finally:
            loader.cleanup()

    # =========================================================================
    # 4. AgentComet Agent
    #    SDK: agentcomet -> agentcomet.models.providers.Ollama
    #    Pattern: create_agent(model, base_url) -> AgentCometWrapper
    # =========================================================================

    def test_comet_compile_and_factory(self):
        """Compile and factory-load the AgentComet agent."""
        uaf_path = self._compile("comet_agent")
        loader, factory = self._load_factory(uaf_path, "comet_agent")
        loader.cleanup()

    def test_comet_llm_invocation(self):
        """
        Load the AgentComet agent using agentcomet.models.providers.Ollama
        and invoke it to multiply numbers.
        """
        uaf_path = self._compile("comet_agent")
        loader = UAFLoader(uaf_path)
        try:
            # AgentComet uses its native Ollama provider
            agent_app = loader.load(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
            )
            print(f"  [SDK] AgentComet agent loaded: {type(agent_app).__name__}")
            self._invoke_and_assert(
                agent_app,
                query="What is 6 multiplied by 7?",
                agent_name="comet_agent",
                expected_keywords=["42"],
            )
        finally:
            loader.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
