import tarfile
import yaml
import io
from .schema import UAFv2AgentYaml
from pydantic import ValidationError

class UAFValidator:
    def __init__(self, uaf_path: str):
        self.uaf_path = uaf_path

    def validate(self):
        print(f"Validating {self.uaf_path}...")
        if not tarfile.is_tarfile(self.uaf_path):
             raise ValueError(f"{self.uaf_path} is not a valid tar file.")

        with tarfile.open(self.uaf_path, "r:gz") as tar:
            # Check for agent.yaml
            try:
                agent_yaml_info = tar.getmember("agent.yaml")
            except KeyError:
                raise ValueError("Archive is missing 'agent.yaml'")
            
            # Read and validate agent.yaml
            f = tar.extractfile(agent_yaml_info)
            if f is None:
                 raise ValueError("Could not extract agent.yaml")
            
            content = f.read()
            try:
                data = yaml.safe_load(content)
                agent_config = UAFv2AgentYaml(**data)
                print("  [OK] agent.yaml schema validation passed.")
            except ValidationError as e:
                raise ValueError(f"agent.yaml inside archive is invalid: {e}")
            except yaml.YAMLError as e:
                 raise ValueError(f"agent.yaml inside archive is not valid YAML: {e}")

            # Check entrypoint existence
            entrypoint_module = agent_config.runtime.entrypoint.split(":")[0]
            entrypoint_file = entrypoint_module if entrypoint_module.endswith(".py") else f"{entrypoint_module}.py"
            try:
                tar.getmember(entrypoint_file)
                print(f"  [OK] Entrypoint file '{entrypoint_file}' exists in archive.")
            except KeyError:
                raise ValueError(f"CRITICAL: Entrypoint file '{entrypoint_file}' specified in agent.yaml is missing from archive.")

            # Strict: Check requirements.txt
            try:
                tar.getmember("requirements.txt")
                print("  [OK] requirements.txt found.")
            except KeyError:
                print("  [WARNING] requirements.txt is missing. Agent may fail to run without dependencies.")

            # Check tools.py if custom tools are declared
            if agent_config.tools and agent_config.tools.custom:
                try:
                    tar.getmember("tools.py")
                    print(f"  [OK] tools.py found for {len(agent_config.tools.custom)} custom tool(s).")
                except KeyError:
                    print(f"  [WARNING] Custom tools declared ({agent_config.tools.custom}) but tools.py not found in archive.")

            # Check agent.state if state is enabled
            if agent_config.state and agent_config.state.enabled:
                state_file = agent_config.state.file or "agent.state"
                try:
                    tar.getmember(state_file)
                    print(f"  [OK] State file '{state_file}' found.")
                except KeyError:
                    print(f"  [WARNING] State is enabled but '{state_file}' not found in archive.")

            print("UAF Validation Successful.")

