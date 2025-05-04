"""
ClickUp Agent for The Elidoras Codex.
Handles interactions with the ClickUp API for task management and content workflow.
"""
import os
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent

class ClickUpAgent(BaseAgent):
    """
    ClickUpAgent handles interactions with the ClickUp API.
    It fetches tasks, updates task statuses, and manages content creation workflows.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("ClickUpAgent", config_path)
        self.logger.info("ClickUpAgent initialized")
        
        # Initialize ClickUp API credentials
        self.api_token = os.getenv("CLICKUP_TOKEN")
        self.workspace_id = os.getenv("CLICKUP_WORKSPACE_ID")
        self.content_list_id = os.getenv("CLICKUP_CONTENT_LIST_ID")
        
        # Check for required environment variables
        if not self.api_token or not self.workspace_id or not self.content_list_id:
            self.logger.warning("ClickUp credentials not fully configured in environment variables.")
            missing = []
            if not self.api_token: missing.append("CLICKUP_TOKEN")
            if not self.workspace_id: missing.append("CLICKUP_WORKSPACE_ID")
            if not self.content_list_id: missing.append("CLICKUP_CONTENT_LIST_ID")
            self.logger.warning(f"Missing environment variables: {', '.join(missing)}")
        
        # ClickUp API base URL
        self.api_base_url = "https://api.clickup.com/api/v2"
        
        # Cache for statuses, custom fields, etc.
        self.status_cache = {}
        self.custom_fields_cache = {}
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get the authorization headers for ClickUp API requests.
        
        Returns:
            Dictionary containing the Authorization header
        """
        if not self.api_token:
            self.logger.error("Cannot create auth headers: ClickUp API token not configured")
            return {}
            
        # ClickUp API expects just the token in the header
        return {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
    
    def get_statuses(self, list_id: str = None) -> List[Dict[str, Any]]:
        """
        Get all statuses for a specific list.
        
        Args:
            list_id: The ClickUp list ID to get statuses from (defaults to content_list_id)
            
        Returns:
            List of status objects with id, status, and color
        """
        target_list_id = list_id or self.content_list_id
        
        # Check if we've cached the statuses for this list
        if target_list_id in self.status_cache:
            return self.status_cache[target_list_id]
            
        if not target_list_id:
            self.logger.error("Cannot fetch statuses: No list ID provided")
            return []
        
        try:
            url = f"{self.api_base_url}/list/{target_list_id}"
            headers = self._get_auth_headers()
            
            self.logger.info(f"Fetching ClickUp list information for list {target_list_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            list_data = response.json()
            statuses = list_data.get("list", {}).get("statuses", [])
            
            # Cache the statuses
            self.status_cache[target_list_id] = statuses
            
            self.logger.info(f"Fetched {len(statuses)} statuses for list {target_list_id}")
            return statuses
            
        except Exception as e:
            self.logger.error(f"Failed to fetch ClickUp list statuses: {e}")
            return []
    
    def get_status_id_by_name(self, status_name: str, list_id: str = None) -> Optional[str]:
        """
        Find a status ID by its name.
        
        Args:
            status_name: Name of the status to find
            list_id: The ClickUp list ID to search in (defaults to content_list_id)
            
        Returns:
            Status ID if found, None otherwise
        """
        statuses = self.get_statuses(list_id)
        
        for status in statuses:
            if status.get("status", "").lower() == status_name.lower():
                return status.get("id")
        
        self.logger.warning(f"Status '{status_name}' not found in list")
        return None
    
    def get_custom_fields(self, list_id: str = None) -> List[Dict[str, Any]]:
        """
        Get all custom fields for a specific list.
        
        Args:
            list_id: The ClickUp list ID to get custom fields from (defaults to content_list_id)
            
        Returns:
            List of custom field objects
        """
        target_list_id = list_id or self.content_list_id
        
        # Check if we've cached the custom fields for this list
        if target_list_id in self.custom_fields_cache:
            return self.custom_fields_cache[target_list_id]
            
        if not target_list_id:
            self.logger.error("Cannot fetch custom fields: No list ID provided")
            return []
        
        try:
            url = f"{self.api_base_url}/list/{target_list_id}/field"
            headers = self._get_auth_headers()
            
            self.logger.info(f"Fetching ClickUp custom fields for list {target_list_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            fields_data = response.json()
            fields = fields_data.get("fields", [])
            
            # Cache the fields
            self.custom_fields_cache[target_list_id] = fields
            
            self.logger.info(f"Fetched {len(fields)} custom fields for list {target_list_id}")
            return fields
            
        except Exception as e:
            self.logger.error(f"Failed to fetch ClickUp custom fields: {e}")
            return []
    
    def get_custom_field_id_by_name(self, field_name: str, list_id: str = None) -> Optional[str]:
        """
        Find a custom field ID by its name.
        
        Args:
            field_name: Name of the custom field to find
            list_id: The ClickUp list ID to search in (defaults to content_list_id)
            
        Returns:
            Field ID if found, None otherwise
        """
        fields = self.get_custom_fields(list_id)
        
        for field in fields:
            if field.get("name", "").lower() == field_name.lower():
                return field.get("id")
        
        self.logger.warning(f"Custom field '{field_name}' not found in list")
        return None
    
    def get_tasks(self, list_id: str = None, status_name: str = None,
                 archived: bool = False, page: int = 0) -> List[Dict[str, Any]]:
        """
        Get tasks from a ClickUp list with optional filtering by status.
        
        Args:
            list_id: The ClickUp list ID to get tasks from (defaults to content_list_id)
            status_name: Optional status name to filter by (e.g., "Ready for AI")
            archived: Whether to include archived tasks
            page: Page number for pagination
            
        Returns:
            List of task objects matching the criteria
        """
        target_list_id = list_id or self.content_list_id
        
        if not target_list_id:
            self.logger.error("Cannot fetch tasks: No list ID provided")
            return []
        
        try:
            url = f"{self.api_base_url}/list/{target_list_id}/task"
            headers = self._get_auth_headers()
            
            # Prepare query parameters
            params = {
                "archived": str(archived).lower(),
                "page": page,
                "subtasks": "true",
                "include_closed": "true"
            }
            
            # Add status filter if provided
            if status_name:
                status_id = self.get_status_id_by_name(status_name, target_list_id)
                if status_id:
                    params["statuses[]"] = status_name
                else:
                    self.logger.warning(f"Status '{status_name}' not found, fetching all tasks")
            
            self.logger.info(f"Fetching ClickUp tasks for list {target_list_id}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            tasks_data = response.json()
            tasks = tasks_data.get("tasks", [])
            
            self.logger.info(f"Fetched {len(tasks)} tasks from list {target_list_id}" + 
                            (f" with status '{status_name}'" if status_name else ""))
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to fetch ClickUp tasks: {e}")
            return []
    
    def get_content_tasks(self, status_name: str = "Ready for AI") -> List[Dict[str, Any]]:
        """
        Get content creation tasks with a specific status from the content list.
        This is a convenience method that wraps get_tasks with default parameters.
        
        Args:
            status_name: Status name to filter by (defaults to "Ready for AI")
            
        Returns:
            List of task objects matching the criteria
        """
        return self.get_tasks(self.content_list_id, status_name)
    
    def update_task_status(self, task_id: str, status_name: str) -> Dict[str, Any]:
        """
        Update a task's status.
        
        Args:
            task_id: The ClickUp task ID to update
            status_name: New status name
            
        Returns:
            Dictionary with success flag and task data or error message
        """
        if not task_id:
            self.logger.error("Cannot update task: No task ID provided")
            return {"success": False, "error": "No task ID provided"}
        
        try:
            url = f"{self.api_base_url}/task/{task_id}"
            headers = self._get_auth_headers()
            
            # Prepare update data
            update_data = {
                "status": status_name
            }
            
            self.logger.info(f"Updating ClickUp task {task_id} status to '{status_name}'")
            response = requests.put(url, headers=headers, json=update_data)
            response.raise_for_status()
            
            updated_task = response.json()
            
            self.logger.info(f"Successfully updated task {task_id} status")
            return {
                "success": True,
                "task": updated_task
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update ClickUp task status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_task_custom_field(self, task_id: str, field_id: str, 
                               value: Any) -> Dict[str, Any]:
        """
        Update a task's custom field value.
        
        Args:
            task_id: The ClickUp task ID to update
            field_id: Custom field ID to update
            value: New value for the custom field
            
        Returns:
            Dictionary with success flag and task data or error message
        """
        if not task_id or not field_id:
            self.logger.error("Cannot update task: Missing task ID or field ID")
            return {"success": False, "error": "Missing task ID or field ID"}
        
        try:
            url = f"{self.api_base_url}/task/{task_id}/field/{field_id}"
            headers = self._get_auth_headers()
            
            # Prepare update data
            update_data = {
                "value": value
            }
            
            self.logger.info(f"Updating ClickUp task {task_id} custom field {field_id}")
            response = requests.post(url, headers=headers, json=update_data)
            response.raise_for_status()
            
            result = response.json()
            
            self.logger.info(f"Successfully updated task {task_id} custom field")
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update ClickUp task custom field: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the main ClickUpAgent workflow.
        
        Returns:
            Results of the ClickUpAgent execution
        """
        self.logger.info("Starting ClickUpAgent workflow")
        
        results = {
            "status": "success",
            "tasks_found": 0,
            "errors": []
        }
        
        try:
            # Test API connection and verify we can fetch content tasks
            content_tasks = self.get_content_tasks()
            
            if content_tasks:
                self.logger.info(f"ClickUp connection verified. Found {len(content_tasks)} content tasks.")
                results["tasks_found"] = len(content_tasks)
            else:
                self.logger.warning("Could not retrieve ClickUp content tasks.")
                results["warnings"] = ["Could not verify ClickUp connection or no tasks found"]
            
        except Exception as e:
            self.logger.error(f"ClickUpAgent workflow failed: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results

if __name__ == "__main__":
    # Create and run the ClickUpAgent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "config", "config.yaml")
    agent = ClickUpAgent(config_path)
    results = agent.run()
    
    print(f"ClickUpAgent execution completed with status: {results['status']}")
    print(f"Content tasks found: {results.get('tasks_found', 'None')}")
    
    if results.get("errors"):
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")