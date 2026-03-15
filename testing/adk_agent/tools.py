def fetch_weather(location: str) -> dict:
    """Gets the current weather for a given location."""
    return {"temp": 72, "conditions": "Sunny", "location": location}

def get_stock_price(ticker: str) -> dict:
    """Gets the current stock price for a given ticker symbol."""
    return {"price": 150.0, "ticker": ticker}
