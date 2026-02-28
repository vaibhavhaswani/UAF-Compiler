import os
import yaml
import tarfile
from .schema import UAFv2AgentYaml
from pydantic import ValidationError

class UAFBuilder:
    def __init__(self, setup_file: str = None, target_dir: str = ".", agent_type: str = None):
        self.target_dir = os.path.abspath(target_dir)
        self.setup_file = setup_file
        self.agent_type = agent_type
        
        # If setup_file is absolute, use it. If relative, join with target_dir? 
        # Actually, if setup_file is provided, we assume it's the anchor.
        # But if setup_file is None, we look in target_dir.
        
        if self.setup_file:
            if not os.path.isabs(self.setup_file):
                 self.setup_file = os.path.join(self.target_dir, self.setup_file)
            self.base_dir = os.path.dirname(self.setup_file)
        else:
            # Default to looking for 'uaf_setup.yaml' in target_dir, or auto-detect
            self.setup_file = os.path.join(self.target_dir, "uaf_setup.yaml")
            self.base_dir = self.target_dir

    def load_config(self):
        # Case 1: Setup file exists
        if os.path.exists(self.setup_file):
            with open(self.setup_file, 'r') as f:
                return yaml.safe_load(f)
        
        # Case 2: Setup file missing, but we are looking for default 'uaf_setup.yaml'
        # and 'agent.yaml' exists -> Auto-detect mode
        agent_yaml_path = os.path.join(self.base_dir, "agent.yaml")
        if os.path.basename(self.setup_file) == "uaf_setup.yaml" and os.path.exists(agent_yaml_path):
            print("  [Info] uaf_setup.yaml not found, but agent.yaml detected. Using auto-configuration.")
            
            # Try to infer output name from agent.yaml
            output_name = "agent.uaf"
            try:
                with open(agent_yaml_path, 'r') as f:
                    agent_data = yaml.safe_load(f)
                    if agent_data and 'agent' in agent_data and 'name' in agent_data['agent']:
                        output_name = f"{agent_data['agent']['name']}.uaf"
            except Exception:
                pass # Fallback to agent.uaf
            
            # Auto-discover files
            files_map = {"agent.yaml": "agent.yaml"}
            
            potential_files = [
                "agent.py", 
                "requirements.txt", 
                "tools.py", 
                "prompt.txt",
                "agent.state",
                "tools" # dir
            ]
            
            for p in potential_files:
                p_path = os.path.join(self.base_dir, p)
                if os.path.exists(p_path):
                    files_map[p] = p
            
            return {
                "output": output_name,
                "files": files_map
            }

        raise FileNotFoundError(f"Setup file not found: {self.setup_file}")

    def validate_agent_yaml(self, agent_yaml_path):
        if not os.path.exists(agent_yaml_path):
            raise FileNotFoundError(f"agent.yaml not found at {agent_yaml_path}")
        
        with open(agent_yaml_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                agent = UAFv2AgentYaml(**data)
                
                # Check explicit type if provided
                if self.agent_type and agent.sdk.name != self.agent_type:
                     raise ValueError(f"Agent type mismatch: Expected '{self.agent_type}', found '{agent.sdk.name}'")
                
                print("  [OK] agent.yaml validation passed.")
            except ValidationError as e:
                raise ValueError(f"agent.yaml validation failed: {e}")
            except yaml.YAMLError as e:
                 raise ValueError(f"agent.yaml is not valid YAML: {e}")

    def build(self):
        config = self.load_config()
        output_filename = config.get('output', 'agent.uaf')
        files_mapping = config.get('files', {})
        
        # Determine strict validation preference? For now, we strict validate agent.yaml
        
        # Check if 'agent.yaml' is in the mapping, as it is required
        agent_yaml_source = None
        for target_name, source_path in files_mapping.items():
            if target_name == 'agent.yaml':
                agent_yaml_source = source_path if os.path.isabs(source_path) else os.path.join(self.base_dir, source_path)
                break
        
        if not agent_yaml_source:
             raise ValueError("uaf_setup.yaml must include a mapping for 'agent.yaml'")

        print(f"Validating {agent_yaml_source}...")
        self.validate_agent_yaml(agent_yaml_source)

        output_path = os.path.join(self.base_dir, output_filename)
        print(f"Building {output_filename}...")
        
        with tarfile.open(output_path, "w:gz") as tar:
            for target_name, source_rel_path in files_mapping.items():
                source_path = os.path.join(self.base_dir, source_rel_path)
                if not os.path.exists(source_path):
                    # Try raw path just in case
                    if os.path.exists(source_rel_path):
                         source_path = source_rel_path
                    else:
                        raise FileNotFoundError(f"Source file {source_rel_path} for {target_name} not found.")
                
                print(f"  Adding {target_name} from {source_rel_path}")
                tar.add(source_path, arcname=target_name)
        
        print(f"Successfully created {output_path}")
