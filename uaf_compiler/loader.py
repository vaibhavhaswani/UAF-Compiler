import tarfile
import yaml
import sys
import os
import importlib.util
import shutil
import tempfile
from .schema import AgentYaml

class UAFLoader:
    def __init__(self, uaf_path: str):
        self.uaf_path = uaf_path
        self.agent_dir = tempfile.mkdtemp(prefix="uaf_agent_")
        self.meta = None

    def load(self):
        print(f"Loading agent from {self.uaf_path} into {self.agent_dir}...")
        
        # Extract
        with tarfile.open(self.uaf_path, "r:gz") as tar:
            tar.extractall(path=self.agent_dir)
        
        # Read Metadata
        agent_yaml_path = os.path.join(self.agent_dir, "agent.yaml")
        if not os.path.exists(agent_yaml_path):
             raise ValueError("agent.yaml missing in archive")
        
        with open(agent_yaml_path, "r") as f:
            self.meta = AgentYaml(**yaml.safe_load(f))
        
        # Add to path
        sys.path.insert(0, self.agent_dir)
        
        # Load Entrypoint
        # entrypoint format: module:function
        try:
            module_name, func_name = self.meta.entrypoint.split(":")
        except ValueError:
            raise ValueError(f"Invalid entrypoint format: {self.meta.entrypoint}. Expected module:function")
            
        module_path = os.path.join(self.agent_dir, module_name if module_name.endswith(".py") else f"{module_name}.py")
        
        if not os.path.exists(module_path):
             raise ValueError(f"Entrypoint module {module_path} not found.")

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, func_name):
            raise ValueError(f"Function {func_name} not found in {module_name}")
            
        factory = getattr(module, func_name)
        return factory, self.meta

    def cleanup(self):
        shutil.rmtree(self.agent_dir)
