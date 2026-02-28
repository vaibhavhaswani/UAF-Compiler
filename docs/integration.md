# Python Integration Guide

This guide details how to integrate UAF agents into your Python applications using the native `uaf_compiler` API.

## Installation

Ensure the package is installed:

```bash
pip install uaf_compiler
```

## The `UAFLoader` Class

The core class for interacting with `.uaf` files is `UAFLoader`. It handles extraction, verification, dependency injection, and updates.

### Import

```python
from uaf_compiler.loader import UAFLoader
```

### Loading an Agent

To load an agent, you simply point to the `.uaf` file and call `.load()`. Based on the UAF version 2 schema (`sdk.name`), the compiler will dynamically route to the correct runtime instantiation. 

#### AgentComet Example (Recommended)
```python
from uaf_compiler.loader import UAFLoader

# 1. Initialize the loader
loader = UAFLoader("agents/my-math-bot.uaf")

# 2. Load the AgentComet instance directly
agent = loader.load()

# 3. Use the agent natively
response = agent.run("What is 5 times 10?")
print(response)
```

#### Generic Framework Example (LangChain / LangGraph / CrewAI)
You can optionally pass any runtime dependencies (like LLMs, API keys, or database connections) directly as keyword arguments for standard factory loaders.

```python
from langchain_ollama import ChatOllama
from uaf_compiler.loader import UAFLoader

llm = ChatOllama(model="gemma3:4b")
loader = UAFLoader("agents/my-langchain-agent.uaf")

# Inject dependencies (kwargs must match entrypoint signature)
agent_app = loader.load(llm=llm)

response = agent_app.invoke({"messages": ["What is 2 + 2?"]})
print(response["messages"][-1].content)
```

For more detailed integration guides on building with each SDK, see the [Frameworks & SDK Integrations Guide](frameworks.md).

### Updating an Agent Programmatically

You can modify an existing `.uaf` archive directly from Python. This is useful for saving state, updating configurations, or hot-patching code.

The `update()` method queues changes, and `apply_updates()` commits them to the file.

#### Supported Update Types
| Type | Target File Inside Archive | Description |
| :--- | :--- | :--- |
| `"state"` | `agent.state` | Persistent memory or checkpoint data |
| `"config"` | `agent.yaml` | Metadata and configuration |
| `"code"` | `agent.py` | The main agent logic code |
| `"requirements"` | `requirements.txt` | Dependency list |

#### Example: Saving Agent State

```python
loader = UAFLoader("my-agent.uaf")

# Queue an update: Replace 'agent.state' inside the archive with local 'latest_state.json'
loader.update("latest_state.json", type="state")

# Commit changes to the .uaf file
result = loader.apply_updates()
print(result) # "Updates applied" or "Nothing to update"
```

#### Example: Hot-Patching

```python
# Queue multiple updates
loader.update("new_logic.py", type="code")
loader.update("new_config.yaml", type="config")

# Apply all at once
loader.apply_updates()
```

## complete API Reference

### `UAFLoader(uaf_path: str)`
Constructor.
- **uaf_path**: Absolute or relative path to the target `.uaf` file.

### `load(**kwargs) -> Runnable`
Loads the agent environment and instantiates the agent.
- **kwargs**: Arbitrary keyword arguments passed to the agent's entrypoint function (e.g. `create_agent(llm=...)`).
- **Returns**: The instantiated agent object (typically a LangChain Runnable or LangGraph CompiledGraph).

### `update(file_path: str, type: str)`
Queues a file to be added or updated in the archive.
- **file_path**: Path to the local file source.
- **type**: One of `"state"`, `"config"`, `"code"`, `"requirements"`.
- **Raises**: `FileNotFoundError` if source is missing, `ValueError` if type is invalid.

### `apply_updates() -> str`
Commits all queued updates to the `.uaf` file.
- **Returns**: Status string ("Updates applied" or "Nothing to update").
