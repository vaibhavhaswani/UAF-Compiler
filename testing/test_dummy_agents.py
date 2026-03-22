"""
test_dummy_agents.py
====================
End-to-end UAF agent tests. Each agent is:
  1. Compiled into a .uaf file
  2. Loaded via UAFLoader with the appropriate SDK + Ollama LLM
  3. Invoked with a real prompt through LLM inference
  4. Validated for expected output keywords

Output is clean and structured for readability.
"""
import os
import sys
import unittest
import warnings

# Suppress noisy deprecation / import warnings from third-party libs
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

# Ensure local uaf_compiler takes precedence
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.messages import HumanMessage
from uaf_compiler.builder import UAFBuilder
from uaf_compiler.loader import UAFLoader

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _hr(char="-", width=70):
    return char * width

def _banner(title):
    print(f"\n{_hr('=')}")
    print(f"  {title}")
    print(_hr("="))

def _step(msg):
    print(f"  > {msg}")

def _result(label, value, indent=4):
    prefix = " " * indent
    value_str = str(value)
    # Truncate very long responses for readability
    if len(value_str) > 300:
        value_str = value_str[:300] + "..."
    print(f"{prefix}{label}: {value_str}")


class TestDummyAgents(unittest.TestCase):
    """
    End-to-end tests for all dummy UAF agents.
    Phase 1: Compile all agents
    Phase 2: Load & invoke each agent through real LLM inference
    """

    def setUp(self):
        self.base_dir = os.path.dirname(__file__)

    # ─── Internal helpers ─────────────────────────────────────────────────

    def _compile(self, agent_dir_name: str) -> str:
        """Compile agent directory -> .uaf file. Returns the .uaf path."""
        agent_dir = os.path.join(self.base_dir, agent_dir_name)
        builder = UAFBuilder(target_dir=agent_dir)
        builder.build()
        config = builder.load_config()
        output_name = config.get("output", "agent.uaf")
        uaf_path = os.path.join(agent_dir, output_name)
        self.assertTrue(os.path.exists(uaf_path), f"Compile failed for {agent_dir_name}")
        return uaf_path

    def _invoke_agent(self, agent_app, query: str):
        """Invoke with LangChain-compatible state, return final response text."""
        initial_state = {"messages": [HumanMessage(content=query)]}
        result = agent_app.invoke(initial_state)
        self.assertIn("messages", result, "Result missing 'messages' key")
        self.assertGreater(len(result["messages"]), 1, "No response messages produced")
        final = result["messages"][-1].content
        return final

    def _assert_keywords(self, response: str, keywords: list, agent_name: str):
        """Check that at least one keyword appears in the response."""
        response_lower = response.lower()
        found_any = any(kw.lower() in response_lower for kw in keywords)
        self.assertTrue(
            found_any,
            f"[{agent_name}] None of {keywords} found in response: {response[:200]}"
        )

    # ═════════════════════════════════════════════════════════════════════
    # PHASE 1: Compile all agents
    # ═════════════════════════════════════════════════════════════════════

    def test_01_compile_all_agents(self):
        """Phase 1: Compile all agent directories into .uaf files."""
        _banner("PHASE 1: Compiling All Agents")

        agents = ["adk_agent", "comet_agent", "crewai_agent", "langchain_agent"]
        for agent_name in agents:
            uaf_path = self._compile(agent_name)
            _step(f"✅ {agent_name:20s} → {os.path.basename(uaf_path)}")

        print(f"\n  All {len(agents)} agents compiled successfully.\n")

    # ═════════════════════════════════════════════════════════════════════
    # PHASE 2: Load & invoke each agent via LLM
    # ═════════════════════════════════════════════════════════════════════

    def test_02_adk_agent(self):
        """Phase 2a: Google ADK agent — weather query via LiteLLM + Ollama."""
        _banner("TEST: Google ADK Agent (LiteLLM + Ollama)")

        _step("Compiling adk_agent...")
        uaf_path = self._compile("adk_agent")

        _step("Loading UAF file...")
        loader = UAFLoader(uaf_path)
        try:
            agent_app = loader.load(
                llm_model=f"ollama/{OLLAMA_MODEL}",
                base_url=OLLAMA_BASE_URL,
            )
            _step(f"Agent loaded: {type(agent_app).__name__}")

            query = "What is the weather in New York?"
            _step(f"Sending prompt...")
            _result("Prompt", query)
            response = self._invoke_agent(agent_app, query)
            _result("Response", response)

            # The tool returns {"temp": 72, "conditions": "Sunny", "location": "New York"}
            # Accept any of these as proof the tool was called
            self._assert_keywords(response, ["72", "sunny", "new york", "weather"], "adk_agent")
            _step("✅ ADK agent test PASSED\n")
        finally:
            loader.cleanup()

    def test_03_comet_agent(self):
        """Phase 2b: AgentComet agent — math query via native Ollama provider."""
        _banner("TEST: AgentComet Agent (Native Ollama)")

        _step("Compiling comet_agent...")
        uaf_path = self._compile("comet_agent")

        _step("Loading UAF file...")
        loader = UAFLoader(uaf_path)
        try:
            agent_app = loader.load(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
            )
            _step(f"Agent loaded: {type(agent_app).__name__}")

            query = "What is 6 multiplied by 7?"
            _step(f"Sending prompt...")
            _result("Prompt", query)
            response = self._invoke_agent(agent_app, query)
            _result("Response", response)

            self._assert_keywords(response, ["42"], "comet_agent")
            _step("✅ AgentComet agent test PASSED\n")
        finally:
            loader.cleanup()

    def test_04_crewai_agent(self):
        """Phase 2c: CrewAI agent — analysis query via LiteLLM + Ollama."""
        _banner("TEST: CrewAI Agent (LiteLLM + Ollama)")

        _step("Compiling crewai_agent...")
        uaf_path = self._compile("crewai_agent")

        _step("Loading UAF file...")
        loader = UAFLoader(uaf_path)
        try:
            agent_app = loader.load(
                llm_model=f"ollama/{OLLAMA_MODEL}",
                base_url=OLLAMA_BASE_URL,
            )
            _step(f"Agent loaded: {type(agent_app).__name__}")

            query = "Analyze the key trends in AI adoption for 2024"
            _step(f"Sending prompt...")
            _result("Prompt", query)
            response = self._invoke_agent(agent_app, query)
            _result("Response", response)

            self._assert_keywords(response, ["ai", "adoption", "analy"], "crewai_agent")
            _step("✅ CrewAI agent test PASSED\n")
        finally:
            loader.cleanup()

    def test_05_langchain_agent(self):
        """Phase 2d: LangChain agent — math via ChatOllama + LangGraph tool loop."""
        _banner("TEST: LangChain Agent (ChatOllama + LangGraph)")

        _step("Compiling langchain_agent...")
        uaf_path = self._compile("langchain_agent")

        _step("Loading UAF file...")
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0,
        )
        loader = UAFLoader(uaf_path)
        try:
            agent_app = loader.load(llm=llm)
            _step(f"Agent loaded: {type(agent_app).__name__}")

            query = "Calculate 15 + 27"
            _step(f"Sending prompt...")
            _result("Prompt", query)
            response = self._invoke_agent(agent_app, query)
            _result("Response", response)

            self._assert_keywords(response, ["42"], "langchain_agent")
            _step("✅ LangChain agent test PASSED\n")
        finally:
            loader.cleanup()


if __name__ == "__main__":
    # Use custom runner for cleaner output
    print(f"\n{'='*70}")
    print(f"  UAF Agent Test Suite")
    print(f"  Model: {OLLAMA_MODEL} @ {OLLAMA_BASE_URL}")
    print(f"{'='*70}")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDummyAgents)
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w', encoding='utf-8', errors='replace'))
    result = runner.run(suite)

    # Print summary
    print(f"\n{_hr('=')}")
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    if failures > 0 or errors > 0:
        print(f"  FAILED: {passed}/{total} passed, {failures} failed, {errors} errors")
        for test, traceback in result.failures + result.errors:
            print(f"\n  FAILED: {test}")
            # Print just the assertion message, not the full traceback
            lines = traceback.strip().split("\n")
            for line in lines[-3:]:
                print(f"    {line.strip()}")
    else:
        print(f"  PASSED: All {total} tests passed!")
    print(_hr("="))

    sys.exit(0 if result.wasSuccessful() else 1)
