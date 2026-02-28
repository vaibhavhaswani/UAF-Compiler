
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tools import tools

def create_agent():
    # We don't need a real key just to instantiate the object in LangChain usually, 
    # but we will just return a configured object or a wrapper
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly complex agent."),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Fake LLM for testing instantiation
    llm = ChatOpenAI(openai_api_key="fake-key", model="gpt-3.5-turbo")
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor
