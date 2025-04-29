"""
Base Agent class for all TEC agents.
This serves as the foundation for all agent types in the TEC ecosystem.
"""
import os
import logging
from typing import Dict, Any, Optional
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
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration if provided
        self.config = {}
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            import yaml
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent's main functionality.
        This method should be overridden by subclasses.
        
        Returns:
            Dict containing the result of the agent's execution
        """
        self.logger.warning("Base run method called - should be overridden by subclass")
        return {"status": "not_implemented", "message": "This method should be overridden"}