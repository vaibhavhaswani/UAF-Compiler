
from langchain.tools import tool

@tool
def analyze_data(data: str) -> str:
    """Analyzes data."""
    return "Analyzed: " + data

tools = [analyze_data]
