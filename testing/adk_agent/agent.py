"""
Google ADK agent using native google-adk SDK with LiteLlm(model="ollama/...").
Factory: create_agent(llm_model, base_url) -> ADKAgentWrapper

The wrapper provides a synchronous invoke() interface compatible with the UAF test harness.
"""
import asyncio
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

try:
    from tools import fetch_weather, get_stock_price
except ImportError:
    from .tools import fetch_weather, get_stock_price


class ADKAgentWrapper:
    """
    Wraps a Google ADK InMemoryRunner behind a LangChain-compatible invoke() interface.
    """
    def __init__(self, runner: InMemoryRunner, app_name: str):
        self.runner = runner
        self.app_name = app_name
        self._session_id = None

    def _run_async(self, coro):
        """Run an async coroutine from sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    async def _setup_session(self):
        session = await self.runner.session_service.create_session(
            app_name=self.app_name,
            user_id="test_user",
        )
        self._session_id = session.id

    async def _invoke_async(self, query: str) -> str:
        if self._session_id is None:
            await self._setup_session()

        user_msg = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=query)],
        )

        collected_text = []
        final_response = ""
        try:
            async for event in self.runner.run_async(
                user_id="test_user",
                session_id=self._session_id,
                new_message=user_msg,
            ):
                # Collect ALL text from any event part
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            collected_text.append(part.text)
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = event.content.parts[0].text or ""
                    break
        except ValueError as e:
            # LLM hallucinated a bad tool name — recover by using collected text
            if collected_text:
                final_response = " ".join(collected_text)
            else:
                final_response = f"[ADK Error recovered: {e}]"

        return final_response or " ".join(collected_text) or "[No response]"

    def invoke(self, state: dict) -> dict:
        """
        Accepts {"messages": [HumanMessage(...)]} and runs the ADK agent.
        Returns {"messages": [..., AIMessage(content=result)]}.
        """
        from langchain_core.messages import AIMessage
        messages = state.get("messages", [])
        query = messages[-1].content if messages else ""

        response_text = self._run_async(self._invoke_async(query))
        return {"messages": messages + [AIMessage(content=response_text)]}


def create_agent(llm_model: str = "ollama/gemma3:4b",
                 base_url: str = "http://localhost:11434"):
    """
    Factory: Creates a real Google ADK LlmAgent powered by Ollama via LiteLlm.

    Args:
        llm_model: LiteLLM model string e.g. 'ollama/gemma3:4b'
        base_url:  Ollama server URL (used via OLLAMA_API_BASE env var)

    Returns:
        ADKAgentWrapper with a LangChain-compatible invoke() method.
    """
    import os
    # LiteLlm uses OLLAMA_API_BASE to route requests
    os.environ["OLLAMA_API_BASE"] = base_url

    llm = LiteLlm(model=llm_model)

    # Very explicit instruction to prevent LLM from hallucinating function names
    instruction = (
        "You are a helpful assistant. "
        "When asked about weather for a location, call the tool named EXACTLY 'fetch_weather' with argument 'location'. "
        "When asked about stock prices, call the tool named EXACTLY 'get_stock_price' with argument 'ticker'. "
        "Only call tools by their exact names: fetch_weather OR get_stock_price. "
        "Do not invent tool names. After getting a tool result, answer the user directly."
    )

    agent = LlmAgent(
        name="adk_weather_stock_agent",
        description="An agent that fetches weather and stock price information.",
        model=llm,
        instruction=instruction,
        tools=[fetch_weather, get_stock_price],
    )

    app_name = "adk_test_app"
    runner = InMemoryRunner(agent=agent, app_name=app_name)
    return ADKAgentWrapper(runner=runner, app_name=app_name)

