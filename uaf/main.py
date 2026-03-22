import argparse
import sys
import os

# Ensure we can import modules from the current directory if running as a script
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from uaf.builder import UAFBuilder
from uaf.validator import UAFValidator
from uaf.inspector import UAFInspector
from uaf.loader import UAFLoader
from uaf.updater import UAFUpdater
from uaf.scaffold import Scaffold

def main():
    parser = argparse.ArgumentParser(description="Universal Agent File (UAF) Compiler")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Build Command
    parser_build = subparsers.add_parser("compile", help="Compile a UAF agent from a setup file or directory")
    parser_build.add_argument("directory", nargs='?', default=".", help="Directory to compile (default: current directory)")
    parser_build.add_argument("-f", "--setup-file", default=None, help="Specific path to uaf_setup.yaml (overrides directory auto-detection)")
    parser_build.add_argument("-t", "--type", help="Validate against specific agent type (e.g., langchain, crewai)")

    # Validate Command
    parser_validate = subparsers.add_parser("validate", help="Validate a .uaf file")
    parser_validate.add_argument("file", help="Path to the .uaf file")

    # Inspect Command
    parser_inspect = subparsers.add_parser("inspect", help="Inspect a .uaf file")
    parser_inspect.add_argument("file", help="Path to the .uaf file")

    # Run Command (Test)
    parser_run = subparsers.add_parser("run", help="Run/Load a .uaf file (Test)")
    parser_run.add_argument("file", help="Path to the .uaf file")
    
    # Update Command
    parser_update = subparsers.add_parser("update", help="Add or update a file in an existing .uaf archive")
    parser_update.add_argument("uaf_file", help="Path to the .uaf file to update")
    parser_update.add_argument("-f", "--file", required=True, help="Path to the file to add/update")
    parser_update.add_argument("-n", "--name", default=None, help="Name to use inside archive (default: filename)")

    # Init Command
    parser_init = subparsers.add_parser("init", help="Initialize a new agent project")
    parser_init.add_argument("--name", required=True, help="Name of the agent")
    parser_init.add_argument("--type", default="agentcomet", choices=["agentcomet", "langchain", "langgraph", "crewai", "google-adk"], help="Type of agent (default: agentcomet)")
    parser_init.add_argument("--agentcomet", action="store_true", help="Explicitly create an AgentComet agent (equivalent to --type agentcomet)")

    args = parser.parse_args()

    if args.command == "compile":
        try:
            # If -f is provided, it takes precedence. Otherwise use directory.
            builder = UAFBuilder(setup_file=args.setup_file, target_dir=args.directory, agent_type=args.type)
            builder.build()
        except Exception as e:
            print(f"Build failed: {e}")
            sys.exit(1)
    
    elif args.command == "validate":
        try:
            validator = UAFValidator(args.file)
            validator.validate()
        except Exception as e:
            print(f"Validation failed: {e}")
            sys.exit(1)

    elif args.command == "inspect":
        try:
            inspector = UAFInspector(args.file)
            inspector.inspect()
        except Exception as e:
            print(f"Inspection failed: {e}")
            sys.exit(1)
            
    elif args.command == "run":
        try:
            loader = UAFLoader(args.file)
            agent = loader.load()
            agent_name = loader.meta.agent.name if loader.meta else "unknown"
            agent_version = loader.meta.agent.version if loader.meta else "unknown"
            sdk_name = loader.meta.sdk.name if loader.meta and loader.meta.sdk else "generic"
            print(f"Successfully loaded agent '{agent_name}' v{agent_version} (SDK: {sdk_name})")
            print(f"Agent instance: {agent}")
        except Exception as e:
            print(f"Run failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.command == "update":
        try:
            updater = UAFUpdater(args.uaf_file)
            updater.update(args.file, args.name)
        except Exception as e:
            print(f"Update failed: {e}")
            sys.exit(1)

    elif args.command == "init":
        try:
            agent_type = args.type
            if args.agentcomet:
                agent_type = "agentcomet"
            
            Scaffold.generate(args.name, agent_type)
        except Exception as e:
            print(f"Init failed: {e}")
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
