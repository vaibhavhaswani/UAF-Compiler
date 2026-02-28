# UAF Compiler User Guide

The **Universal Agent File (UAF) Compiler** is a command-line interface (CLI) tool designed to manage the lifecycle of your AI agents. It allows you to package standard agents into a single, portable `.uaf` file, validate their structure, inspect their contents, and even run or update them.

This guide provides a detailed reference for all `uaf` commands and their options.

---

## 🚀 0. Initializing Agents (`init`)

The `init` command generates a scaffold for a new AI agent project, providing a rapid starting point for various agent frameworks.

### Usage
```bash
uaf init --name <agent_name> [--type <agent_type>] [--agentcomet]
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `--name` | **Required.** the name of the new agent project directory. |
| `--type` | Optional. The framework to scaffold (`agentcomet`, `langchain`, `crewai`, `google-adk`, `langgraph`). Defaults to `agentcomet`. |
| `--agentcomet` | Optional flag to explicitly default to the `agentcomet` template. |

### Example
```bash
# Scaffold a default AgentComet project
uaf init --name my_agent

# Scaffold a CrewAI project
uaf init --name my_crew_agent --type crewai
```

---

## 🏗️ 1. Compiling Agents (`compile`)

The `compile` command is your primary tool for creating a `.uaf` artifact. It takes a local folder structure and packages it based on a configuration file.

### Usage
```bash
uaf compile [directory] [-f <setup_file>] [-t <type>]
```

### Arguments

| Argument | Short | Default | Required | Description |
| :--- | :---: | :--- | :---: | :--- |
| `directory` | - | `.` | No | The target directory to compile from. Defaults to the current directory. |
| `--setup-file` | `-f` | - | No | Explicit path to a setup file. Overrides default auto-detection. |
| `--type` | `-t` | - | No | Validates that the agent configuration matches this specific type (e.g., `langchain`). |

### Example
```bash
# Compile from the current directory (auto-detects agent.yaml or uaf_setup.yaml)
uaf compile

# Compile a specific directory
uaf compile ./my_agent

# Compile and validate it's a crewai agent
uaf compile ./my_agent --type crewai
```

**What it does:**
1. Validates the existence of all source files listed in the setup file.
2. Creates a gzip-compressed tarball (`.uaf`) specified by the `output` field.
3. Automatically validates the created archive to ensure integrity.

---

## 🛡️ 2. Validating Agents (`validate`)

The `validate` command checks an existing `.uaf` file to ensure it adheres to the UAF protocol. It verifies the manifest schema, required files (entrypoint, dependencies), and internal structure.

### Usage
```bash
uaf validate <uaf_file>
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `file` | Path to the `.uaf` file to validate. |

### Example
```bash
uaf validate my-agent.uaf
```

**Checks Performed:**
- Is it a valid tarball?
- Does `agent.yaml` exist and follow the schema?
- Does the entrypoint file exist?
- Are tool definitions consistent with included files?

---

## 🔍 3. Inspecting Agents (`inspect`)

The `inspect` command allows you to peek inside a `.uaf` file without extracting it manually. It displays key metadata from the manifest and lists the files contained within.

### Usage
```bash
uaf inspect <uaf_file>
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `file` | Path to the `.uaf` file to inspect. |

### Example
```bash
uaf inspect my-agent.uaf
```

**Output Includes:**
- **Metadata**: Name, Version, Author, Runtime, Type.
- **Entrypoint**: The defined entry function.
- **Tools**: List of tools packaged with the agent.
- **Files**: Listing of all files and directories inside the archive.

---

## 🏃 4. Running Agents (`run`)

The `run` command loads the agent into a temporary runtime environment and attempts to execute its entrypoint. This is useful for quickly verifying that your compiled agent can be loaded and authorized.

### Usage
```bash
uaf run <uaf_file>
```

### Arguments

| Argument | Description |
| :--- | :--- |
| `file` | Path to the `.uaf` file to run. |

### Example
```bash
uaf run my-agent.uaf
```

**Note:** This runs the agent in a local Python process. Ensure your environment meets the agent's dependencies (though UAF packages requirements, `uaf run` uses your current environment).

---

## 🔄 5. Updating Agents (`update`)

The `update` command allows you to surgically modify or add a single file within an existing `.uaf` archive. This is ideal for updating configuration files, state files, or patching code without a full re-compile.

### Usage
```bash
uaf update <uaf_file> -f <source_file> [-n <archive_name>]
```

### Arguments

| Argument | Short | Required | Description |
| :--- | :---: | :---: | :--- |
| `uaf_file` | - | Yes | Path to the existing `.uaf` archive to modify. |
| `--file` | `-f` | Yes | Path to the local source file you want to inject. |
| `--name` | `-n` | No | The filename to use *inside* the archive. Defaults to the source filename. |

### Examples

**Update `agent.state`:**
```bash
uaf update my-agent.uaf -f ./current_state.json -n agent.state
```

**Patch a script:**
```bash
uaf update my-agent.uaf -f ./hotfix.py -n agent.py
```

---

## ❓ Getting Help

To see global help or help for a specific command, use the `--help` flag.

```bash
# Global help
uaf --help

# Command-specific help
uaf compile --help
uaf update --help
```
