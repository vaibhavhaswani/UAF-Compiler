from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field

# Legacy Support (v1)
class ToolDefinition(BaseModel):
    name: str
    description: str
    schema_file: Optional[str] = Field(default=None, alias="schema")
    file_path: Optional[str] = Field(default=None, alias="file") 

class Metadata(BaseModel):
    author: Optional[str] = None
    version: str
    langchain_version: Optional[str] = None
    langgraph_version: Optional[str] = None

class AgentYaml(BaseModel):
    version: str = "1.0"
    format: Literal["uaf"] = "uaf"
    name: str
    type: Literal["langgraph", "langchain", "crewai", "google-adk", "agentcomet"]
    runtime: Literal["python", "wasm"]
    entrypoint: str
    tools: Optional[List[ToolDefinition]] = None
    metadata: Metadata

# UAF v2 Schema

class AgentDef(BaseModel):
    name: str
    version: str = "0.1.0"
    description: Optional[str] = None
    author: Optional[str] = None

class RuntimeDef(BaseModel):
    engine: Literal["python", "wasm"] = "python"
    entrypoint: str

class SdkDef(BaseModel):
    name: str
    version: str = "0.1.0"

class ToolsDef(BaseModel):
    builtin: Optional[List[str]] = []
    custom: Optional[List[str]] = []

class StateDef(BaseModel):
    enabled: bool = False
    file: Optional[str] = None

class DependenciesDef(BaseModel):
    auto: bool = True

class UAFv2AgentYaml(BaseModel):
    uaf_version: int = 2
    agent: AgentDef
    runtime: RuntimeDef
    sdk: SdkDef
    tools: Optional[ToolsDef] = Field(default_factory=ToolsDef)
    state: Optional[StateDef] = Field(default_factory=StateDef)
    dependencies: Optional[DependenciesDef] = Field(default_factory=DependenciesDef)
