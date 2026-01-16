#!/bin/bash
set -e

# Universal Agent File (UAF) Linux Build Script
# This script is intended to be run inside a Debian-based Linux environment (e.g., Ubuntu, WSL).

echo ">>> Updating package lists..."
sudo apt-get update

echo ">>> Installing build dependencies..."
sudo apt-get install -y python3-all python3-pip python3-stdeb fakeroot build-essential dh-python

echo ">>> Installing Python dependencies..."
pip3 install -r requirements.txt
pip3 install stdeb

echo ">>> Cleaning previous builds..."
rm -rf deb_dist dist build *.egg-info

echo ">>> Building Debian Package (.deb)..."
python3 setup.py --command-packages=stdeb.command bdist_deb

echo ">>> Build Complete!"
echo "You can find your .deb package in the 'deb_dist' directory."
ls -l deb_dist/*.deb

echo ""
echo ">>> INSTALLATION INSTRUCTIONS:"
echo "To install the package and automatically resolve dependencies (like python3-pydantic), run:"
echo "sudo apt install ./deb_dist/uaf-compiler_*.deb"

