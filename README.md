<div align="center">

# 📦 Universal Agent File (UAF) — The Standard for Portable AI Agents

**Package once. Run anywhere. Share stateful AI agents as binaries.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-v0.8.0-blue)](https://pypi.org/project/uaf-cli/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)]()

[Overview](#-overview) •
[Features](#-features) •
[Installation](#-installation) •
[Quick Start](#-quick-start) •
[CLI](#-cli) •
[Specification](#-protocol-specification) •
[AgentComet](#-agentcomet-upcoming-framework)

</div>

---

## 🚀 Overview

**Universal Agent File (UAF)** is a **standardized binary format** for packaging and distributing AI agents.

It solves a core problem in the agent ecosystem:

> ❌ Agents are fragmented, framework-locked, and not portable
> ✅ UAF makes agents **portable, reproducible, and shareable**

A `.uaf` file is a compressed, verifiable artifact that bundles agent logic, dependencies, metadata, tools, and optional state.

This enables:
**Write once → run anywhere → resume anytime**

---

## ✨ Features

* **📦 Portable Binary Format** - Package complete agents into a single `.uaf` file.
* **🧠 Stateful Agents** - Persist and transfer agent memory across environments.
* **🛡️ Strict Validation** - Enforced schema (`agent.yaml`) ensures reliability.
* **🔍 Inspect Without Running** - View metadata, tools, and config without execution.
* **🔌 Framework Agnostic** - Works across LangChain, LangGraph, CrewAI, Google ADK.
* **⚡ Runtime Loader** - Dynamically load and execute agents from `.uaf`.

---

## 🛠️ Installation

Install from PyPI (Python 3.9+):

```bash
pip install uaf-cli
```

Or from source:

```bash
git clone https://github.com/vaibhavhaswani/uaf-cli.git
cd uaf-cli
pip install .
```

---

## ⚡ Quick Start

### 1️⃣ Project Structure

Create an agent folder with the following structure:

```text
my-agent/
├── agent.py          # Framework logic (LangChain, CrewAI, etc.)
├── agent.yaml        # Manifest metadata
├── requirements.txt  # Dependencies
├── agent.state       # (Optional) Initial state
└── uaf_setup.yaml    # Compiler build instructions
```

### 2️⃣ Configure Build (`uaf_setup.yaml`)

```yaml
output: my-agent.uaf

files:
  agent.py: ./agent.py
  agent.yaml: ./agent.yaml
  requirements.txt: ./requirements.txt
  agent.state: ./agent.state
```

### 3️⃣ Compile

```bash
uaf compile -f uaf_setup.yaml
```

✅ **Output**: `my-agent.uaf`

---

## 💻 CLI

Compile, package, and execute agents with simple commands:

```bash
uaf init        # Scaffold absolute path project
uaf compile     # Compile into .uaf artifact
uaf validate    # Validate schema compliance
uaf inspect     # View deep metadata
uaf run         # Run CLI agent turn loop
uaf update      # Inject incremental builds
```

Full technical guide → [`docs/usage_guide.md`](docs/usage_guide.md)

---

## 🔗 Loading Agents

The `UAFLoader` dynamically routes directly into execution setups powered by target frame pipelines.

```python
from uaf_compiler.loader import UAFLoader

# 1. Initialize Loader
uaf_loader = UAFLoader("my-agent.uaf")

# 2. Dynamic Router Injection
# Load LangChain/LangGraph
agent_app = uaf_loader.load(llm=my_llm)

# Load CrewAI
agent_crew = uaf_loader.load(llm_model="ollama/gemma3", base_url="http://...")

# Load Google ADK
agent_runner = uaf_loader.load(llm_model="ollama/gemma3", base_url="http://...")
```

Full Loading & Integration workflows → [`docs/integration.md`](docs/integration.md)

---

## 📜 Protocol Specification

Complete binary spec design detailing underlying tarball structure, manifest validation rules, and lifecycle bindings.

See frameworks & schema docs → [`docs/frameworks.md`](docs/frameworks.md)

---

## 🏗️ Development & Testing

Standard installation and developer workflows:

```bash
pip install -e .
```

### Run End-to-End Tests
To verify loaders and correct tool-use turn loops across all SDK adaptors (LangChain, CrewAI, ADK, Comet) over a local Ollama endpoint:

```bash
python testing/test_dummy_agents.py
```

---

**AgentComet** natively loads and executes UAF agents using its SDK-level hooks without wrapping logic adapters.

```python
from agentcomet import load_agent

# 1. Load UAF directly 
agent = load_agent("my-agent.uaf")

# 2. Run agent natively
response = agent.run("Calculate current stock performance")
print("Response:", response)

# 3. Export / Save state
agent.export("my_assistant.uaf")
```

---

<div align="center">
    <sub>Built with ❤️ by Vaibhav Haswani • Apache 2.0 License</sub>
</div>
