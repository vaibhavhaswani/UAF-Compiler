# Universal Agent File (UAF) Compiler & Protocol

The **Universal Agent File (UAF)** is a standardized binary format and protocol for packaging, distributing, and running AI agents. It wraps agent implementation code, dependencies, metadata, and tool definitions into a single portable `.uaf` file (gzip-compressed tarball).

The **UAF Compiler** is a CLI tool to build, validate, inspect, and run these agent files, making agents "plug-and-play" across different environments (e.g., LangChain, LangGraph).

## Features

- **Standardized Format**: Defines a strict schema (`agent.yaml`) for agent metadata, runtime, and tools.
- **Compilation**: Bundles source code and assets into a signed-like `.uaf` binary.
- **Validation**: Enforces strict checks for required files (entrypoints, dependencies, tool schemas) to prevent broken builds.
- **Inspection**: Allows peering into the contents and metadata of an existing `.uaf` file without extracting it.
- **Runtime Loader**: Provides a Python API to dynamically load and execute agents from `.uaf` files directly into frameworks like LangGraph.
- **Cross-Platform**: Available as an MSI installer for Windows and DEB package for Linux.

## Installation

### Windows
Download and run the provided `.msi` installer.
- The installer adds `uaf` to your system `PATH`.
- Default installation directory: `C:\Program Files\UAFCompiler`.

### Linux (Debian/Ubuntu)
Install the `.deb` package:
```bash
sudo apt install ./uaf-compiler_0.1.0-1_all.deb
```
This automatically handles dependencies like `python3-pydantic` and `python3-yaml`.

### From Source
```bash
pip install .
```

## Usage

### 1. Project Structure
A standard UAF agent project looks like this:

```text
my-agent-project/
├── agent.yaml              # (Required) Protocol metadata & manifest
├── agent.py                # (Required) Agent implementation code
├── requirements.txt        # (Recommended) Python dependencies
├── uaf_setup.yaml          # (Required for build) build configuration
└── tools/                  # (Optional) Tool definitions
    └── calculate_risk.json
```

### 2. CLI Commands

**Compile an Agent**
Builds the `.uaf` file based on the `uaf_setup.yaml` manifest.
```bash
uaf compile -f uaf_setup.yaml
```

**Validate an Agent**
Checks the `.uaf` file for schema compliance and missing assets.
```bash
uaf validate my-agent.uaf
```

**Inspect an Agent**
View metadata and file listing without unpacking.
```bash
uaf inspect my-agent.uaf
```

**Run/Test an Agent**
Loads and executes the agent's entrypoint in a temporary environment.
```bash
uaf run my-agent.uaf
```

### 3. schemas

**agent.yaml** (Protocol Definition)
```yaml
version: "1.0"
format: "uaf"
name: "risk-assessment-agent"
type: "langgraph"           # or "langchain"
runtime: "python"           # or "wasm"
entrypoint: "agent.py:create_agent" # module:factory_function
tools:
  - name: "calculate_risk"
    description: "Calculate risk metrics"
    schema: "tools/calculate_risk.json"
metadata:
    author: "Your Org"
    version: "1.0.0"
```

**uaf_setup.yaml** (Build Configuration)
Maps your local source files to their destination inside the `.uaf` archive.
```yaml
output: my-agent.uaf
files:
  agent.yaml: ./agent.yaml
  agent.py: ./agent.py
  requirements.txt: ./requirements.txt
  tools/calculate_risk.json: ./tools/calculate_risk.json
```

## Integration with LangGraph

The UAF framework allows you to load agents dynamically into LangGraph workflows.

```python
from uaf_compiler.loader import UAFLoader
from langgraph.graph import StateGraph

# Load the agent node from the binary
loader = UAFLoader("my-agent.uaf")
agent_factory, meta = loader.load()
agent_node = agent_factory()

# Integrate into Graph
builder = StateGraph(State)
builder.add_node("agent", agent_node)
# ... build rest of graph ...
```

## Building the Compiler

### Windows (MSI)
Requires `cx_Freeze`.
```bash
pip install -r requirements_win.txt
python setup_win.py bdist_msi
```
Output: `dist/uaf_compiler-0.1.0-win64.msi`

### Linux (DEB)
Requires `stdeb`, `fakeroot`, `build-essential`.
```bash
bash build_deb.sh
```
Output: `deb_dist/uaf-compiler_0.1.0-1_all.deb`
