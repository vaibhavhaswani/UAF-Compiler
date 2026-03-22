import os
import sys
import importlib
import importlib.util
from .base import BaseRuntime

class GenericUAFRuntime(BaseRuntime):
    def load(self, **kwargs):
        factory = self._load_factory()
        return factory(**kwargs)
    
    def _load_factory(self):
        loader = self.loader
        if not os.path.exists(loader.agent_dir) or not os.listdir(loader.agent_dir):
             loader._extract()

        if loader.agent_dir not in sys.path:
            sys.path.insert(0, loader.agent_dir)
        
        if not loader.meta:
            loader._load_metadata()

        module_name, func_name = loader.meta.runtime.entrypoint.split(":")
        module_path = os.path.join(loader.agent_dir, module_name if module_name.endswith(".py") else f"{module_name}.py")
        
        if not os.path.exists(module_path):
             raise ValueError(f"Entrypoint module {module_path} not found.")

        # Use a unique module name based on the agent directory to avoid module cache conflicts
        # when loading multiple agents that have identically-named modules (e.g. "agent", "tools")
        unique_suffix = os.path.basename(loader.agent_dir)
        unique_module_name = f"{module_name}_{unique_suffix}"

        # Also pre-load any sibling modules (like tools.py) with unique names 
        # so that the agent module's "from tools import ..." resolves correctly
        self._preload_sibling_modules(loader.agent_dir, unique_suffix)

        try:
            spec = importlib.util.spec_from_file_location(unique_module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[unique_module_name] = module
            spec.loader.exec_module(module)
        except Exception as e:
            raise ImportError(f"Failed to import agent module: {e}")
        
        if not hasattr(module, func_name):
            raise ValueError(f"Function {func_name} not found in {module_name}")
            
        factory = getattr(module, func_name)
        return factory

    def _preload_sibling_modules(self, agent_dir, unique_suffix):
        """
        Pre-load sibling .py modules from the agent directory into sys.modules
        so that 'from tools import ...' style imports resolve to the correct files
        rather than cached modules from previous agents.
        """
        for filename in os.listdir(agent_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                mod_name = filename[:-3]  # e.g., "tools"
                mod_path = os.path.join(agent_dir, filename)
                
                # Remove any previously cached version of this base module name
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
                
                # Invalidate import caches so Python re-discovers the module
                importlib.invalidate_caches()
