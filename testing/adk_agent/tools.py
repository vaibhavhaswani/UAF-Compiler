
def fetch_weather(location: str):
    return {"temp": 72, "conditions": "Sunny"}

def get_stock_price(ticker: str):
    return {"price": 150.0}

tools = [fetch_weather, get_stock_price]
