"""
Quick probe: confirm google-adk InMemoryRunner with genai.types Content
"""
import asyncio
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

def fetch_weather(location: str) -> dict:
    """Gets the current weather for a given location."""
    return {"temp": 72, "conditions": "Sunny", "location": location}

async def run():
    llm = LiteLlm(model="ollama/gemma3:4b")
    agent = LlmAgent(
        name="weather_agent",
        description="An agent that can fetch weather data",
        model=llm,
        instruction="You are a helpful weather assistant. Use the fetch_weather tool to answer questions.",
        tools=[fetch_weather],
    )
    runner = InMemoryRunner(agent=agent, app_name="test_app")
    session = await runner.session_service.create_session(
        app_name="test_app", user_id="user1"
    )

    user_msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text="What is the weather in New York?")]
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="user1",
        session_id=session.id,
        new_message=user_msg,
    ):
        print(f"Event: {type(event).__name__}, final={event.is_final_response()}")
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text
            break

    print("ADK Response:", final_response)

asyncio.run(run())
