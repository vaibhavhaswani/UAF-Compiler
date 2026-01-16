import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "yaml", "pydantic", "tarfile", "json"],
    "excludes": ["tkinter"],
    "include_files": []
}

# Base set to None for console application
base = None

# MSI Options
bdist_msi_options = {
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFiles64Folder]\UAFCompiler",
}

setup(
    name="UAF Compiler",
    version="0.1.0",
    description="Universal Agent File Compiler",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[Executable("uaf_compiler/main.py", base=base, target_name="uaf.exe")]
)
