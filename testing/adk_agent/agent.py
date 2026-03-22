"""
Google ADK agent using native google-adk SDK with LiteLlm(model="ollama/...").
Factory: create_agent(llm_model, base_url) -> ADKAgentWrapper

The wrapper provides a synchronous invoke() interface compatible with the UAF test harness.
"""
import asyncio
import json
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

try:
    from tools import fetch_weather, get_stock_price
except ImportError:
    from .tools import fetch_weather, get_stock_price

# Registry so we can manually execute tools if ADK doesn't auto-call them
TOOL_REGISTRY = {
    "fetch_weather": fetch_weather,
    "get_stock_price": get_stock_price,
}


class ADKAgentWrapper:
    """
    Wraps a Google ADK InMemoryRunner behind a LangChain-compatible invoke() interface.
    """
    def __init__(self, runner: InMemoryRunner, app_name: str):
        self.runner = runner
        self.app_name = app_name
        self._session_id = None

    def _run_async(self, coro):
        """Run an async coroutine from sync context robustly."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return asyncio.run(coro)

    async def _setup_session(self):
        session = await self.runner.session_service.create_session(
            app_name=self.app_name,
            user_id="test_user",
        )
        self._session_id = session.id

    def _try_execute_tool_from_text(self, text: str) -> str | None:
        """
        Attempt to detect and execute a tool call from raw LLM output.
        Handles multiple formats that LiteLLM + gemma3 may produce:
          1. Raw JSON with "type":"function" (LiteLLM function call format)
          2. CALL_TOOL:name:{args} text format
          3. Direct tool result JSON (ADK already executed the tool)
        Returns the tool result string, or None if no tool call was detected.
        """
        # Format 1: LiteLLM function-call JSON
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                # Direct tool result from ADK 
                # e.g. {"temp":72,"conditions":"Sunny","location":"New York"}
                if "temp" in parsed:
                    return f"The weather in {parsed.get('location')} is {parsed.get('conditions')} and {parsed.get('temp')} degrees."
                if "price" in parsed:
                    return f"The stock price for {parsed.get('ticker')} is {parsed.get('price')}."
                
                # LiteLLM function-call format
                if parsed.get("type") == "function":
                    func_info = parsed.get("function", {})
                    name = func_info.get("name")
                    args = func_info.get("arguments", {})
                    if isinstance(args, str):
                        args = json.loads(args)
                    if name == "fetch_weather":
                        res = TOOL_REGISTRY[name](**args)
                        return f"The weather in {args.get('location')} is {res.get('conditions')} and {res.get('temp')} degrees."
                    elif name == "get_stock_price":
                        res = TOOL_REGISTRY[name](**args)
                        return f"The stock price for {args.get('ticker')} is {res.get('price')}."
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

        # Format 2: CALL_TOOL:name:{args}
        for tool_name, tool_fn in TOOL_REGISTRY.items():
            marker = f"CALL_TOOL:{tool_name}:"
            if marker in text:
                try:
                    args_str = text.split(marker)[1].strip()
                    args = json.loads(args_str)
                    res = tool_fn(**args)
                    if tool_name == "fetch_weather":
                        return f"The weather in {args.get('location')} is {res.get('conditions')} and {res.get('temp')} degrees."
                    elif tool_name == "get_stock_price":
                        return f"The stock price for {args.get('ticker')} is {res.get('price')}."
                except Exception:
                    pass

        return None

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
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            collected_text.append(part.text)
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = event.content.parts[0].text or ""
                    break
        except ValueError as e:
            if collected_text:
                final_response = " ".join(collected_text)
            else:
                final_response = f"[ADK Error: {e}]"

        result_str = final_response or " ".join(collected_text) or "[No response]"

        # Try to detect and auto-execute tool calls from LLM output
        tool_result = self._try_execute_tool_from_text(result_str)
        if tool_result is not None:
            return tool_result

        return result_str

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
    """
    import os
    os.environ["OLLAMA_API_BASE"] = base_url

    llm = LiteLlm(model=llm_model)

    instruction = (
        "You are a helpful assistant with access to tools. "
        "When the user asks about weather, use the fetch_weather tool. "
        "When the user asks about stock prices, use the get_stock_price tool. "
        "After getting a tool result, present the information clearly to the user."
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
