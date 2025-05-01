"""
Base Agent class for all TEC agents.
This serves as the foundation for all agent types in the TEC ecosystem.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional

# Add site-packages to path to help find modules
python_path = sys.executable
site_packages = os.path.join(os.path.dirname(os.path.dirname(python_path)), 'lib', 'site-packages')
if os.path.exists(site_packages):
    sys.path.append(site_packages)

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAgent:
    """Base class for all TEC agents to inherit from."""
    
    def __init__(self, name: str, config_path: Optional[str] = None):
        """
        Initialize the base agent with a name and optional configuration.
        
        Args:
            name: Name of the agent
            config_path: Optional path to a configuration file
        """
        self.name = name
        self.logger = logging.getLogger(f"TEC.{name}")
        self.logger.info(f"Initializing {name} agent")
        
        # Load environment variables from the specific path
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
        load_dotenv(env_path, override=True)
        
        # Load configuration if provided
        self.config = {}
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file or directory
        """
        try:
            # Import yaml with error handling
            try:
                import yaml
            except ImportError:
                self.logger.error("PyYAML not found. Please run 'pip install pyyaml'")
                return
            
            # If the path is a directory, look for config.yaml
            if os.path.isdir(config_path):
                config_file = os.path.join(config_path, "config.yaml")
                if not os.path.exists(config_file):
                    self.logger.info(f"No config.yaml found in {config_path}, skipping configuration")
                    return
                config_path = config_file
                
            # Load the YAML file
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"Loaded configuration from {config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            # Continue without configuration rather than failing
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent's main functionality.
        This method should be overridden by subclasses.
        
        Returns:
            Dict containing the result of the agent's execution
        """
        self.logger.warning("Base run method called - should be overridden by subclass")
        return {"status": "not_implemented", "message": "This method should be overridden"}