from langchain_core.tools import tool

@tool
def calculate_complex_math(expression: str) -> str:
    """Evaluates a Python math expression and returns the numeric result."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

@tool
def search_database(query: str) -> str:
    """Searches a mock database and returns matching results."""
    return "Mock Result for: " + query

tools = [calculate_complex_math, search_database]
