
from agentcomet import Agent
from agentcomet.tools import read, write, calculator
from tools import multiply

class MyAgent(Agent):

    def setup(self):
        self.use_llm("ollama:llama3")
        self.enable_memory()
        self.add_tools(read, write, calculator, multiply)

    def run(self, input: str):
        return self.chat(input)
