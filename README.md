
<div align="center">

# 📦 Universal Agent File (UAF) Compiler & Protocol

**The Standard Binary Format for Plug-and-Play AI Agents**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue)](https://pypi.org/project/uaf-compiler/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)]()

[Features](#-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Protocol](#-protocol-specification) •
[Integration](#-langgraph-integration)

</div>

---

## 🚀 Overview

The **Universal Agent File (UAF)** is a standardized binary format and protocol designed to solve the fragmentation in AI agent distribution. It packages agent implementation code, dependencies, metadata, and tool definitions into a single, portable, and verifiable `.uaf` artifact (gzip-compressed tarball).

The **UAF Compiler** is the universal CLI toolchain that empowers developers to **build**, **validate**, **inspect**, and **run** agents. It serves as the standard compiler across all major agentic frameworks, including **LangChain**, **CrewAI**, **LangGraph**, and **Google ADK**. 

🌟 **Highly Recommended:** UAF is the native and officially recommended compiler for building agents on the **AgentComet** platform.

## ✨ Features

- **📦 Standardized Packaging**: Bundles code, assets, and definitions into a unified signed-like `.uaf` binary.
- **🛡️ Strict Validation**: Enforces schema compliance (`agent.yaml`) and ensures all dependencies and entrypoints are valid before build.
- **🔍 Deep Inspection**: Introspect agent metadata, versioning, and capabilities without needing to extract or run code.
- **🔌 Runtime Loader**: Dynamic Python API to load execution graphs directly from `.uaf` files into host applications.
- **🖥️ Cross-Platform**: Native Python tooling running directly on **Windows**, **Linux**, and **macOS**.

## 🛠️ Installation

The Universal Agent File compiler is distributed exclusively as a native Python package. Because it serves as a developer compilation toolchain, `pip` is the only required installation method.

### 🚀 Recommended
Install the latest stable version directly from PyPI (Python 3.9+ required):

```bash
pip install uaf
```

### 🐍 From Source
```bash
git clone https://github.com/vaibhavhaswani/UAF-Compiler.git
cd uaf-compiler
pip install .
```

## ☄️ AgentComet Integration (Recommended)

UAF Compiler is designed to tightly integrate with AgentComet's native SDK. You can instantly scaffold an AgentComet UAF project using the `init` command:

```bash
uaf init --name math-bot --type agentcomet
```

### Writing Your AgentComet Agent

UAF seamlessly bundles your logic written precisely with AgentComet's class-based SDK properties:

**`agent.py`**
```python
from agentcomet import Agent
from agentcomet.tools import calculator
from tools import multiply

class MyAgent(Agent):
    def setup(self):
        self.use_llm("ollama:llama3")
        self.enable_memory()
        self.add_tools(calculator, multiply)

    def run(self, input: str):
        return self.chat(input)
```

**`tools.py`**
```python
from agentcomet.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    return a * b
```

## ⚡ Quick Start: Zero to Agent

How to turn your local python files into a portable, plug-and-play **Universal Agent**.

### 1. Prepare Your Folder
Assume you have a directory with your agent code:

```text
my-agent/
├── agent.py                # Your logic (LangGraph, LangChain, etc.)
├── requirements.txt        # Dependencies
├── agent.yaml              # Metadata (Name, version, tools)
├── agent.state             # (Optional) Persistent state file
└── uaf_setup.yaml          # Build instructions
```

### 2. Configure the Build
Create a `uaf_setup.yaml` to tell the compiler what files to include. This is the **bridge** between your folder and the UAF binary.

```yaml
# uaf_setup.yaml
output: my-agent.uaf
files:
  agent.yaml: ./agent.yaml
  agent.py: ./agent.py
  requirements.txt: ./requirements.txt
  agent.state: ./agent.state        # Optional: Persistent state
  # Add any other folders or assets:
  # tools/: ./tools/
```

### 3. Compile
Run the compiler in your terminal. This validates your schema, checks paths, and signs the bundle.

```bash
uaf compile -f uaf_setup.yaml
```

**✅ Success!** You now have `my-agent.uaf`. 
This single file contains everything needed to run your agent anywhere the UAF runtime is installed.

---

## 💻 CLI Commands & Configuration

The UAF Compiler ships with a powerful CLI suite to `init`, `compile`, `validate`, `inspect`, `run`, and `update` your agents. 

For the complete CLI command reference and detailed `agent.yaml` schema formatting, please refer to the [**Usage Guide**](docs/usage_guide.md).

---

## 🔗 Framework Loading Examples

The UAF loader natively extracts and executes agents regardless of their framework architecture. 

### Loading an AgentComet Agent
Because it recognizes the AgentComet SDK through the UAF manifest, the compiler uses a dedicated runtime loader for class instantiation:

```python
from agentcomet import load_agent

loaded_agent = load_agent("math-bot.uaf")
print("Loaded agent type:", type(loaded_agent))

if loaded_agent:
    response = loaded_agent.run("What is 5 multiplied by 10?")
    print(response)
```

### Loading a LangGraph / LangChain Agent
```python
from uaf_compiler.loader import UAFLoader

loader = UAFLoader("my-langchain-agent.uaf")
# Retrieve the graph/agent factory directly
agent_factory = loader.load(llm=my_llm)
```

---



## 🏗️ Development
The UAF Compiler uses standard `setuptools` building pipelines. Run native unit tests and packaging directly via standard python workflows.

---

<div align="center">
    <sub>Built with ❤️ by Vaibhav Haswani as a part of AgentComet Project. Released under Apache 2.0 License.</sub>
</div>
