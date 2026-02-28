
import sys
import os

print(f"Current Working Directory: {os.getcwd()}")
print(f"Initial Sys Path: {sys.path}")

# Add root to path explicitely
root_dir = os.path.abspath(".")
if root_dir not in sys.path:
    sys.path.append(root_dir)

print(f"Updated Sys Path: {sys.path}")

try:
    import uaf_compiler
    print(f"Successfully imported uaf_compiler: {uaf_compiler}")
except Exception as e:
    print(f"Failed to import uaf_compiler: {e}")

try:
    from uaf_compiler.scaffold import Scaffold
    print(f"Successfully imported Scaffold: {Scaffold}")
except Exception as e:
    print(f"Failed to import Scaffold: {e}")

try:
    from uaf_compiler.builder import UAFBuilder
    print(f"Successfully imported UAFBuilder: {UAFBuilder}")
except Exception as e:
    print(f"Failed to import UAFBuilder: {e}")
