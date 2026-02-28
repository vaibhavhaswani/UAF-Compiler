
import google.generativeai as genai
from tools import tools

def create_agent():
    # Complex Configuration
    genai.configure(api_key="fake-key")
    
    generation_config = {
      "temperature": 0.9,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }

    # Model instantiation with tools
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        tools=tools
    )
    
    return model
