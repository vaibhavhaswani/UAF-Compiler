
from langchain.tools import tool

@tool
def calculate_complex_math(expression: str) -> str:
    """Calculates complex math."""
    return "42"

@tool
def search_database(query: str) -> str:
    """Searches a mock database."""
    return "Mock Result for: " + query

tools = [calculate_complex_math, search_database]
