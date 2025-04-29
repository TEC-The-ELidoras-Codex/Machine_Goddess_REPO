"""
Local Storage integration for The Elidoras Codex.
Handles storage and retrieval of files using local file system instead of cloud services.
"""
import os
import logging
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
import json
import shutil

from .base_agent import BaseAgent

class LocalStorageAgent(BaseAgent):
    """
    LocalStorageAgent handles interactions with the local file system.
    It uploads, downloads, and manages files locally without cloud dependencies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("LocalStorageAgent", config_path)
        self.logger.info("LocalStorageAgent initialized")
        
        # Initialize storage folder
        self.storage_dir = os.getenv("LOCAL_STORAGE_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage"))
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "backups"), exist_ok=True)
        
        self.logger.info(f"Local storage initialized at: {self.storage_dir}")
    
    def upload_file(self, file_path: str, destination_blob_name: Optional[str] = None) -> Dict[str, Any]:
        """
        "Upload" (copy) a file to local storage.
        
        Args:
            file_path: Path to the local file
            destination_blob_name: Name to save the file as (if None, uses file name)
            
        Returns:
            Dictionary with upload status and path
        """
        try:
            # If no destination name provided, use the file name
            if not destination_blob_name:
                destination_blob_name = os.path.basename(file_path)
            
            # Destination path
            destination_path = os.path.join(self.storage_dir, destination_blob_name)
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(file_path, destination_path)
            
            self.logger.info(f"File {file_path} copied to {destination_path}")
            return {
                "success": True,
                "path": destination_path,
                "blob_name": destination_blob_name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to copy file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def download_file(self, blob_name: str, destination_file_path: str) -> Dict[str, Any]:
        """
        "Download" (copy) a file from local storage.
        
        Args:
            blob_name: Name of the file in storage
            destination_file_path: Local path to save the file
            
        Returns:
            Dictionary with download status
        """
        try:
            # Source path
            source_path = os.path.join(self.storage_dir, blob_name)
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, destination_file_path)
            
            self.logger.info(f"File {source_path} copied to {destination_file_path}")
            return {
                "success": True,
                "file_path": destination_file_path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to copy file {blob_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_files(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in local storage.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            Dictionary with list of files
        """
        try:
            file_list = []
            
            for root, _, files in os.walk(self.storage_dir):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.storage_dir)
                    
                    # Apply prefix filter if specified
                    if prefix and not rel_path.startswith(prefix):
                        continue
                    
                    file_stats = os.stat(full_path)
                    file_list.append({
                        "name": rel_path,
                        "size": file_stats.st_size,
                        "updated": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                    })
            
            self.logger.info(f"Listed {len(file_list)} files in local storage")
            return {
                "success": True,
                "files": file_list
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def backup_wordpress_data(self, content_data: Dict[str, Any], backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Backup WordPress post data to local storage.
        
        Args:
            content_data: Dictionary of WordPress post data
            backup_name: Optional custom backup name
            
        Returns:
            Dictionary with backup status and path
        """
        try:
            # Create a timestamp for the backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not backup_name:
                backup_name = f"wp_backup_{timestamp}.json"
            else:
                if not backup_name.endswith('.json'):
                    backup_name += '.json'
            
            # Backup path
            backup_path = os.path.join(self.storage_dir, "backups", backup_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Write the data to a file
            with open(backup_path, 'w') as backup_file:
                json.dump(content_data, backup_file, indent=2)
            
            self.logger.info(f"WordPress data backed up to {backup_path}")
            return {
                "success": True,
                "path": backup_path,
                "blob_name": os.path.join("backups", backup_name)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to backup WordPress data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent's main logic.
        
        Returns:
            Dictionary with agent execution results
        """
        self.logger.info("Running LocalStorageAgent")
        
        results = {
            "status": "success",
            "files_count": 0,
            "storage_dir": self.storage_dir
        }
        
        try:
            # List files as a test
            file_list_result = self.list_files()
            if file_list_result["success"]:
                results["files_count"] = len(file_list_result["files"])
                self.logger.info(f"Found {results['files_count']} files in storage")
            else:
                results["status"] = "warning"
                results["message"] = "Failed to list files"
            
        except Exception as e:
            self.logger.error(f"Error in LocalStorageAgent run: {e}")
            results["status"] = "error"
            results["message"] = str(e)
        
        return results

if __name__ == "__main__":
    # Create and run the agent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "config", "config.yaml")
    agent = LocalStorageAgent(config_path)
    results = agent.run()
    
    print(f"LocalStorageAgent execution completed with status: {results['status']}")
    print(f"Files in storage: {results.get('files_count', 'unknown')}")