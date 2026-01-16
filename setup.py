from setuptools import setup, find_packages

setup(
    name="uaf_compiler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "uaf=uaf_compiler.main:main",
        ],
    },
)
