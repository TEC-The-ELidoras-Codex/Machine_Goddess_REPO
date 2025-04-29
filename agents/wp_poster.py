"""
WordPress Posting Agent for The Elidoras Codex.
Handles interactions with WordPress for publishing content.
"""
import os
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from base64 import b64encode

from .base_agent import BaseAgent

class WordPressAgent(BaseAgent):
    """
    WordPressAgent handles interactions with the WordPress API.
    It creates posts, updates content, and manages media uploads.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("WordPressAgent", config_path)
        self.logger.info("WordPressAgent initialized")
        
        # Initialize WordPress API credentials
        self.wp_site_url = os.getenv("WP_SITE_URL")
        self.wp_user = os.getenv("WP_USER")
        self.wp_app_pass = os.getenv("WP_APP_PASS")
        
        # Check for required environment variables
        if not self.wp_site_url or not self.wp_user or not self.wp_app_pass:
            self.logger.warning("WordPress credentials not fully configured in environment variables.")
        
        # WordPress REST API endpoints
        self.api_base_url = f"{self.wp_site_url.rstrip('/')}/wp-json/wp/v2" if self.wp_site_url else None
    
    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get the authorization header for WordPress API requests.
        
        Returns:
            Dictionary containing the Authorization header
        """
        if not self.wp_user or not self.wp_app_pass:
            self.logger.error("Cannot create auth header: WordPress credentials not configured")
            return {}
            
        credentials = f"{self.wp_user}:{self.wp_app_pass}"
        token = b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {token}"}
    
    def create_post(self, title: str, content: str, excerpt: str = "", 
                    status: str = "draft", categories: List[int] = None, 
                    tags: List[int] = None, featured_media_id: int = 0) -> Dict[str, Any]:
        """
        Create a new post on the WordPress site.
        
        Args:
            title: Post title
            content: Post content (can contain HTML)
            excerpt: Post excerpt
            status: Post status (draft, publish, etc.)
            categories: List of category IDs
            tags: List of tag IDs
            featured_media_id: ID of the featured image
            
        Returns:
            Dictionary containing the created post data or error information
        """
        if not self.api_base_url:
            self.logger.error("Cannot create post: WordPress API URL not configured")
            return {"error": "WordPress API URL not configured"}
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/posts"
            headers = {
                **self._get_auth_header(),
                "Content-Type": "application/json"
            }
            
            # Prepare post data
            post_data = {
                "title": title,
                "content": content,
                "status": status
            }
            
            # Add optional parameters if provided
            if excerpt:
                post_data["excerpt"] = excerpt
            if categories:
                post_data["categories"] = categories
            if tags:
                post_data["tags"] = tags
            if featured_media_id:
                post_data["featured_media"] = featured_media_id
            
            # Make the API request
            self.logger.info(f"Creating WordPress post: '{title}'")
            response = requests.post(url, headers=headers, json=post_data)
            response.raise_for_status()
            
            post_data = response.json()
            post_id = post_data.get("id")
            post_url = post_data.get("link")
            
            self.logger.info(f"Successfully created post #{post_id}: {post_url}")
            return {
                "success": True,
                "post_id": post_id,
                "post_url": post_url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create WordPress post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_media(self, file_path: str, title: str = "") -> Dict[str, Any]:
        """
        Upload media file to WordPress.
        
        Args:
            file_path: Path to the media file
            title: Optional title for the media
            
        Returns:
            Dictionary containing the uploaded media data or error information
        """
        if not self.api_base_url:
            self.logger.error("Cannot upload media: WordPress API URL not configured")
            return {"error": "WordPress API URL not configured"}
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                self.logger.error(f"Media file not found: {file_path}")
                return {"error": f"Media file not found: {file_path}"}
            
            # Prepare API request
            url = f"{self.api_base_url}/media"
            headers = {
                **self._get_auth_header(),
            }
            
            # Get file details
            file_name = os.path.basename(file_path)
            
            # Determine content type based on file extension
            _, ext = os.path.splitext(file_name)
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.pdf': 'application/pdf'
            }
            content_type = content_types.get(ext.lower(), 'application/octet-stream')
            
            # Prepare file data
            with open(file_path, 'rb') as file:
                files = {'file': (file_name, file, content_type)}
                data = {}
                
                if title:
                    data['title'] = title
                
                # Upload the media file
                self.logger.info(f"Uploading media: {file_name}")
                response = requests.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                
                media_data = response.json()
                media_id = media_data.get("id")
                media_url = media_data.get("source_url")
                
                self.logger.info(f"Successfully uploaded media #{media_id}: {media_url}")
                return {
                    "success": True,
                    "media_id": media_id,
                    "media_url": media_url
                }
                
        except Exception as e:
            self.logger.error(f"Failed to upload media: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the main WordPressAgent workflow.
        
        Returns:
            Results of the WordPressAgent execution
        """
        self.logger.info("Starting WordPressAgent workflow")
        
        results = {
            "status": "success",
            "posts_created": 0,
            "errors": []
        }
        
        try:
            # Example workflow for demonstration
            # In a real scenario, you would likely get content from another source
            
            # Example post creation
            post_result = self.create_post(
                title="Test Post from TEC Automation",
                content="<p>This is an automated post from The Elidoras Codex automation system.</p>",
                excerpt="Automated post from TEC",
                status="draft"
            )
            
            if post_result.get("success"):
                results["posts_created"] += 1
                self.logger.info(f"Created post: {post_result.get('post_url')}")
            else:
                error_msg = post_result.get("error", "Unknown error")
                results["errors"].append(f"Failed to create post: {error_msg}")
            
            self.logger.info("WordPressAgent workflow completed successfully")
            
        except Exception as e:
            self.logger.error(f"WordPressAgent workflow failed: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results

if __name__ == "__main__":
    # Create and run the WordPressAgent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "config", "config.yaml")
    agent = WordPressAgent(config_path)
    results = agent.run()
    
    print(f"WordPressAgent execution completed with status: {results['status']}")
    print(f"Posts created: {results['posts_created']}")
    
    if results["errors"]:
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")