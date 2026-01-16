from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    name: str
    description: str
    schema_file: str = Field(alias="schema") 

class Metadata(BaseModel):
    author: Optional[str] = None
    version: str
    langchain_version: Optional[str] = None
    langgraph_version: Optional[str] = None

class AgentYaml(BaseModel):
    version: str = "1.0"
    format: Literal["uaf"] = "uaf"
    name: str
    type: Literal["langgraph", "langchain"]
    runtime: Literal["python", "wasm"]
    entrypoint: str
    tools: Optional[List[ToolDefinition]] = None
    metadata: Metadata
