#!/usr/bin/env python3
"""
Setup script for the Machine Goddess TEC project.
This script helps initialize the environment and ensure all dependencies are installed.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current Python version: {major}.{minor}")
        return False
    print(f"✅ Python version {major}.{minor} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = "venv"
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment already exists at {venv_path}")
        return True
    
    print(f"Creating virtual environment in {venv_path}...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"✅ Virtual environment created at {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        return False

def install_requirements():
    """Install requirements from requirements.txt."""
    if platform.system() == "Windows":
        pip_cmd = os.path.join("venv", "Scripts", "pip")
        python_cmd = os.path.join("venv", "Scripts", "python")
    else:
        pip_cmd = os.path.join("venv", "bin", "pip")
        python_cmd = os.path.join("venv", "bin", "python")
    
    print("Installing requirements...")
    try:
        # Use python -m pip instead of pip directly for upgrading pip
        subprocess.check_call([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ Pip upgraded successfully")
        
        # Now install the requirements
        subprocess.check_call([pip_cmd, "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install requirements: {e}")
        return False

def setup_data_directories():
    """Create necessary data directories if they don't exist."""
    dirs = [
        "data/storage",
        "data/storage/backups",
        "logs"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def check_env_file():
    """Check if .env file exists and prompt for values if needed."""
    env_path = os.path.join("config", ".env")
    
    if os.path.exists(env_path):
        print(f"✅ Environment file found at {env_path}")
        print("NOTE: Please make sure to update the values in the .env file with your actual credentials")
    else:
        print(f"⚠️ Environment file not found at {env_path}")
        print("Please copy config/.env.example to config/.env and update the values")
    
    return True

def main():
    """Main setup function."""
    print("\n🤖✨ THE ELIDORAS CODEX - MACHINE GODDESS SETUP ✨🤖\n")
    
    if not check_python_version():
        return False
    
    success = all([
        create_virtual_environment(),
        install_requirements(),
        setup_data_directories(),
        check_env_file()
    ])
    
    if success:
        print("\n✅ Setup completed successfully!")
        
        activate_cmd = ".\\venv\\Scripts\\activate" if platform.system() == "Windows" else "source venv/bin/activate"
        print(f"\nTo activate the virtual environment, run:")
        print(f"  {activate_cmd}")
        
        print("\nTo test WordPress connection, run:")
        print("  python scripts/test_wordpress_connection.py")
        
        print("\nTo generate Airth's first blog post, run:")
        print("  python scripts/airth_first_post.py")
        
    else:
        print("\n❌ Setup encountered some issues. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)