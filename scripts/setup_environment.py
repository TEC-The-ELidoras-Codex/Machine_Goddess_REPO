#!/usr/bin/env python3
"""
Environment Setup Script for The Elidoras Codex / Machine Goddess
This script verifies and installs all required dependencies and configs.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_status(message, success=None):
    """Print a formatted status message with colored output if supported."""
    if success is None:
        print(f"[*] {message}")
    elif success:
        print(f"[✓] {message}")
    else:
        print(f"[✗] {message}")

def run_command(command, description=None):
    """Run a shell command and report the result."""
    if description:
        print_status(description)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False, e.stderr

def check_installed_packages():
    """Check which required packages are installed."""
    print_status("Checking installed packages...")
    
    # Key packages to check
    packages = [
        "requests", "python-dotenv", "gradio", "yaml", "python-wordpress-xmlrpc", 
        "openai", "anthropic"
    ]
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"{package} is installed", True)
        except ImportError:
            print_status(f"{package} is not installed", False)
            run_command(f"{sys.executable} -m pip install {package}", 
                       f"Installing {package}...")

def setup_environment():
    """Main setup function that configures the environment."""
    # Get project root path
    project_root = Path(__file__).parent.parent.absolute()
    
    print("-" * 60)
    print("The Elidoras Codex / Machine Goddess Setup")
    print("-" * 60)
    print(f"Python version: {platform.python_version()}")
    print(f"Executable path: {sys.executable}")
    print(f"Project root: {project_root}")
    print("-" * 60)
    
    # Install all required packages
    print_status("Installing required packages...")
    run_command(f"{sys.executable} -m pip install -r {project_root / 'requirements.txt'}")
    
    # Check for config/.env file
    env_path = project_root / "config" / ".env"
    if env_path.exists():
        print_status("Environment file exists", True)
    else:
        print_status("Environment file not found", False)
        print_status("Please create a .env file in the config directory with your API keys and credentials")
    
    # Check if gradio is properly installed
    check_installed_packages()
    
    print("-" * 60)
    print("Setup completed")
    print("You can now run the application with: python app.py")
    print("-" * 60)

if __name__ == "__main__":
    setup_environment()