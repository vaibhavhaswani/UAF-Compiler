
import os
import shutil
import unittest
import sys
import tempfile
import yaml

from uaf_compiler.scaffold import Scaffold
from uaf_compiler.builder import UAFBuilder

class TestUAFExpansion(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        try:
            shutil.rmtree(self.test_dir)
        except PermissionError:
            pass # Windows file locking sometimes

    def test_scaffold_agentcomet(self):
        Scaffold.generate("my_agent", "agentcomet", self.test_dir)
        target_dir = os.path.join(self.test_dir, "my_agent")
        
        self.assertTrue(os.path.exists(target_dir))
        self.assertTrue(os.path.exists(os.path.join(target_dir, "agent.py")))
        self.assertTrue(os.path.exists(os.path.join(target_dir, "tools.py")))
        self.assertTrue(os.path.exists(os.path.join(target_dir, "prompt.txt")))
        self.assertTrue(os.path.exists(os.path.join(target_dir, "agent.yaml")))
        
        with open(os.path.join(target_dir, "agent.yaml"), 'r') as f:
            data = yaml.safe_load(f)
            self.assertEqual(data['type'], 'agentcomet')

    def test_scaffold_crewai(self):
        Scaffold.generate("crew_bot", "crewai", self.test_dir)
        target_dir = os.path.join(self.test_dir, "crew_bot")
        
        self.assertTrue(os.path.exists(os.path.join(target_dir, "agent.yaml")))
        with open(os.path.join(target_dir, "agent.yaml"), 'r') as f:
            data = yaml.safe_load(f)
            self.assertEqual(data['type'], 'crewai')

    def test_scaffold_langchain(self):
        Scaffold.generate("lc_agent", "langchain", self.test_dir)
        target_dir = os.path.join(self.test_dir, "lc_agent")
        
        self.assertTrue(os.path.exists(os.path.join(target_dir, "agent.yaml")))
        with open(os.path.join(target_dir, "agent.yaml"), 'r') as f:
            data = yaml.safe_load(f)
            self.assertEqual(data['type'], 'langchain')

    def test_scaffold_google_adk(self):
        Scaffold.generate("gadk_agent", "google-adk", self.test_dir)
        target_dir = os.path.join(self.test_dir, "gadk_agent")
        
        self.assertTrue(os.path.exists(os.path.join(target_dir, "agent.yaml")))
        with open(os.path.join(target_dir, "agent.yaml"), 'r') as f:
            data = yaml.safe_load(f)
            self.assertEqual(data['type'], 'google-adk')

    def test_compile_auto_detection(self):
        # 1. Init
        Scaffold.generate("auto_agent", "agentcomet", self.test_dir)
        agent_dir = os.path.join(self.test_dir, "auto_agent")
        
        # 2. Compile (without uaf_setup.yaml)
        os.chdir(agent_dir)
        try:
            # We initialize builder with "uaf_setup.yaml" (default), which doesn't exist
            # This triggers the auto-detection logic in builder.py
            builder = UAFBuilder("uaf_setup.yaml")
            builder.build()
            
            # Should produce auto_agent.uaf (derived from agent.yaml name)
            self.assertTrue(os.path.exists("auto_agent.uaf"))
        finally:
            os.chdir(self.test_dir) # Back to temp root

if __name__ == '__main__':
    unittest.main()
