import os
import sys
import importlib.util
from .base import BaseRuntime

class AgentCometRuntime(BaseRuntime):
    def load(self, **kwargs):
        loader = self.loader
        if not os.path.exists(loader.agent_dir) or not os.listdir(loader.agent_dir):
             loader._extract()

        if loader.agent_dir not in sys.path:
            sys.path.insert(0, loader.agent_dir)
        
        if not loader.meta:
            loader._load_metadata()

        module_name, class_name = loader.meta.runtime.entrypoint.split(":")
        module_path = os.path.join(loader.agent_dir, module_name if module_name.endswith(".py") else f"{module_name}.py")
        
        if not os.path.exists(module_path):
             raise ValueError(f"Entrypoint module {module_path} not found.")

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            raise ImportError(f"Failed to import agent module: {e}")
        
        if not hasattr(module, class_name):
            raise ValueError(f"Class {class_name} not found in {module_name}")
            
        agent_class = getattr(module, class_name)
        
        # Instantiate and setup
        agent_instance = agent_class(**kwargs)
        if hasattr(agent_instance, "setup"):
            agent_instance.setup()
            
        return agent_instance
