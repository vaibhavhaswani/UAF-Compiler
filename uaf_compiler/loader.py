import tarfile
import yaml
import sys
import os
import importlib.util
import shutil
import tempfile
from .schema import AgentYaml
from .updater import UAFUpdater

class UAFLoader:
    def __init__(self, uaf_path: str):
        self.uaf_path = uaf_path
        self.agent_dir = tempfile.mkdtemp(prefix="uaf_agent_")
        self.meta = None
        self.pending_updates = {} # Map of internal_name -> source_path

    def update(self, file_path: str, type: str):
        """
        Queue an update for the UAF archive.
        
        Args:
            file_path: Path to the local file source.
            type: Type of file to update. Supported: 'state', 'code', 'requirements', 'config'.
        """
        valid_types = {
            "state": "agent.state",
            "code": "agent.py",
            "requirements": "requirements.txt",
            "config": "agent.yaml"
        }
        
        if type not in valid_types:
            raise ValueError(f"Invalid update type '{type}'. Supported: {list(valid_types.keys())}")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        internal_name = valid_types[type]
        self.pending_updates[internal_name] = file_path
        print(f"  [Loader] Queued update for '{internal_name}' from '{file_path}'")

    def apply_updates(self):
        """
        Commit all pending updates to the UAF file.
        """
        if not self.pending_updates:
            print("Nothing to update")
            return "Nothing to update"
            
        print(f"Applying {len(self.pending_updates)} updates to {self.uaf_path}...")
        
        # Use UAFUpdater to apply updates. 
        # Note: Ideally UAFUpdater should support batch updates, but for now we loop.
        # Since UAFUpdater repacks on every call, this is inefficient for many files.
        # But for 1-2 files it is acceptable.
        
        updater = UAFUpdater(self.uaf_path)
        
        for name, src_path in self.pending_updates.items():
            updater.update(src_path, archive_name=name)
            
        # Clear pending
        self.pending_updates = {}
        print("All updates applied successfully.")
        return "Updates applied"

    def load(self, **kwargs):
        """
        High-level API to load and instantiate the agent using dynamic SDK routing.
        """
        if not self.meta:
            if not os.path.exists(self.agent_dir) or not os.listdir(self.agent_dir):
                self._extract()
            self._load_metadata()

        from .runtimes.agentcomet import AgentCometRuntime
        from .runtimes.generic import GenericUAFRuntime

        if getattr(self.meta, 'sdk', None) and self.meta.sdk.name == "agentcomet":
            print(f"  [Loader] Routing to AgentCometRuntime (SDK: {self.meta.sdk.name})")
            runtime = AgentCometRuntime(self)
        else:
            sdk_name = self.meta.sdk.name if getattr(self.meta, 'sdk', None) else "unknown"
            print(f"  [Loader] Routing to GenericUAFRuntime (SDK: {sdk_name})")
            runtime = GenericUAFRuntime(self)

        return runtime.load(**kwargs)

    def load_factory(self):
        """
        Legacy entry point for factory getters.
        Warning: This is not guaranteed to return a function on class-based SDKs.
        """
        if not self.meta:
            if not os.path.exists(self.agent_dir) or not os.listdir(self.agent_dir):
                self._extract()
            self._load_metadata()
            
        from .runtimes.generic import GenericUAFRuntime
        # Always use generic to return a factory for backwards compatibility
        runtime = GenericUAFRuntime(self)
        return runtime._load_factory()

    def _extract(self):
        print(f"Loading agent from {self.uaf_path} into {self.agent_dir}...")
        with tarfile.open(self.uaf_path, "r:gz") as tar:
            tar.extractall(path=self.agent_dir)
        self._load_metadata()

    def _load_metadata(self):
        agent_yaml_path = os.path.join(self.agent_dir, "agent.yaml")
        if not os.path.exists(agent_yaml_path):
             raise ValueError("agent.yaml missing in archive")
        
        with open(agent_yaml_path, "r") as f:
            from .schema import UAFv2AgentYaml # Inline import to avoid circular errors or clean up global definition
            self.meta = UAFv2AgentYaml(**yaml.safe_load(f))

    def cleanup(self):
        shutil.rmtree(self.agent_dir)
