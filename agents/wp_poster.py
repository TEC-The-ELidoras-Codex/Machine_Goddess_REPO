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
        # Support both naming conventions for compatibility
        self.wp_site_url = os.getenv("WP_SITE_URL") or os.getenv("WP_URL", "https://elidorascodex.com")
        self.wp_user = os.getenv("WP_USER")
        self.wp_app_pass = os.getenv("WP_APP_PASS") or os.getenv("WP_PASS")
        
        # Check for required environment variables
        if not self.wp_site_url or not self.wp_user or not self.wp_app_pass:
            self.logger.warning("WordPress credentials not fully configured in environment variables.")
        
        # WordPress REST API endpoints
        self.api_base_url = f"{self.wp_site_url.rstrip('/')}/wp-json/wp/v2" if self.wp_site_url else None
        
        # Predefined categories and tags for TEC content
        self.categories = {
            "airths_codex": None,  # Will be populated during get_categories
            "technology_ai": None,
            "reviews_deepdives": None,
            "uncategorized": None
        }
        
        # Common tags for AI content
        self.common_ai_tags = [
            "ai-ethics", "ai-storytelling", "ai-assisted-writing", 
            "ai-driven-creativity", "ai-generated-content", "ai-human-collaboration",
            "creative-ai-tools"
        ]
        
        # Cache categories on initialization
        if self.api_base_url:
            self.get_categories()
    
    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get the authorization header for WordPress API requests.
        Uses Basic Authentication that works with WordPress.com sites.
        
        Returns:
            Dictionary containing the Authorization header
        """
        if not self.wp_user or not self.wp_app_pass:
            self.logger.error("Cannot create auth header: WordPress credentials not configured")
            return {}
            
        # Convert username to lowercase for consistency
        username = self.wp_user.lower()
        
        # Use Basic Authentication with username and password with spaces
        credentials = f"{username}:{self.wp_app_pass}"
        token = b64encode(credentials.encode()).decode()
        
        self.logger.debug(f"Generated Basic Auth token for WordPress API")
        return {"Authorization": f"Basic {token}"}
    
    def _try_multiple_auth_methods(self, method: str, url: str, data: Dict = None) -> requests.Response:
        """
        Try multiple authentication methods for WordPress API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: API URL to request
            data: Data to send (for POST/PUT)
            
        Returns:
            Response from the successful authentication method or the last attempted response
        """
        # Authentication methods to try in order
        auth_methods = [
            {
                "name": "Bearer token",
                "headers": {
                    **self._get_auth_header(),
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Basic auth with spaces",
                "auth": (self.wp_user.lower(), self.wp_app_pass)
            },
            {
                "name": "Basic auth without spaces",
                "auth": (self.wp_user.lower(), self.wp_app_pass.replace(' ', ''))
            }
        ]
        
        last_response = None
        for method_info in auth_methods:
            try:
                self.logger.debug(f"Trying authentication method: {method_info['name']}")
                
                kwargs = {}
                if "headers" in method_info:
                    kwargs["headers"] = method_info["headers"]
                if "auth" in method_info:
                    kwargs["auth"] = method_info["auth"]
                
                if data:
                    kwargs["json"] = data
                    
                # Ensure proper Content-Type for requests with data
                if data and "headers" in kwargs:
                    kwargs["headers"]["Content-Type"] = "application/json"
                elif data:
                    kwargs["headers"] = {"Content-Type": "application/json"}
                
                # Make the request
                response = requests.request(method, url, **kwargs)
                last_response = response
                
                # If successful, return the response
                if response.status_code in [200, 201]:
                    self.logger.debug(f"Authentication method {method_info['name']} succeeded")
                    return response
                    
            except Exception as e:
                self.logger.error(f"Error with authentication method {method_info['name']}: {e}")
        
        # If we get here, none of the authentication methods succeeded
        return last_response
    
    def get_categories(self) -> Dict[str, Any]:
        """
        Fetch and cache available categories from WordPress.
        
        Returns:
            Dictionary of categories with their IDs
        """
        if not self.api_base_url:
            self.logger.error("Cannot fetch categories: WordPress API URL not configured")
            return {}
            
        try:
            url = f"{self.api_base_url}/categories"
            headers = self._get_auth_header()
            
            self.logger.info("Fetching WordPress categories")
            response = requests.get(url, headers=headers, params={"per_page": 100})
            response.raise_for_status()
            
            categories = response.json()
            
            # Map category slugs to IDs
            category_map = {}
            for category in categories:
                slug = category.get("slug", "")
                
                # Match known category slugs to their IDs
                if "airth" in slug or "codex" in slug:
                    self.categories["airths_codex"] = category.get("id")
                    category_map["airths_codex"] = category.get("id")
                elif "technology" in slug or "tech" in slug or "ai" in slug:
                    self.categories["technology_ai"] = category.get("id")
                    category_map["technology_ai"] = category.get("id")
                elif "review" in slug or "deep" in slug:
                    self.categories["reviews_deepdives"] = category.get("id")
                    category_map["reviews_deepdives"] = category.get("id")
                elif "uncategorized" in slug:
                    self.categories["uncategorized"] = category.get("id")
                    category_map["uncategorized"] = category.get("id")
                
                # Also store by slug for direct lookup
                category_map[slug] = category.get("id")
                
            self.logger.info(f"Fetched {len(categories)} WordPress categories")
            return category_map
            
        except Exception as e:
            self.logger.error(f"Failed to fetch WordPress categories: {e}")
            return {}
    
    def get_tags(self, keyword_list: List[str] = None) -> List[int]:
        """
        Get tag IDs based on keywords. Creates tags if they don't exist.
        
        Args:
            keyword_list: List of keywords to match or create as tags
            
        Returns:
            List of tag IDs
        """
        if not self.api_base_url or not keyword_list:
            return []
            
        tag_ids = []
        try:
            # First try to find existing tags
            for keyword in keyword_list:
                slug = keyword.lower().replace(' ', '-')
                url = f"{self.api_base_url}/tags"
                headers = {
                    **self._get_auth_header(),
                    "Content-Type": "application/json"
                }
                
                # Search for existing tag
                response = requests.get(url, headers=headers, params={"search": keyword})
                tags = response.json()
                
                if tags and len(tags) > 0:
                    # Use the first matching tag
                    tag_ids.append(tags[0]["id"])
                else:
                    # Create new tag
                    tag_data = {
                        "name": keyword,
                        "slug": slug
                    }
                    response = requests.post(url, headers=headers, json=tag_data)
                    
                    if response.status_code == 201:
                        new_tag = response.json()
                        tag_ids.append(new_tag["id"])
            
            return tag_ids
        except Exception as e:
            self.logger.error(f"Error processing tags: {e}")
            return []
    
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
            
            # Get authentication headers - using Bearer token auth that worked for categories
            headers = {
                **self._get_auth_header(),
                "Content-Type": "application/json"
            }
            
            # Log headers for debugging (without sensitive info)
            self.logger.debug(f"Using headers: {', '.join(headers.keys())}")
            
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
            
            # Log more details if there's an error
            if response.status_code != 201:
                self.logger.error(f"Post creation failed with status {response.status_code}: {response.text[:200]}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
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
    
    def create_airth_post(self, title: str, content: str, keywords: List[str] = None,
                         excerpt: str = "", status: str = "draft") -> Dict[str, Any]:
        """
        Create a post specifically for Airth's Codex category with appropriate tags.
        
        Args:
            title: Post title
            content: Post content
            keywords: Keywords to use as tags
            excerpt: Post excerpt
            status: Post status (draft, publish, etc.)
            
        Returns:
            Result of post creation
        """
        # Ensure categories are loaded
        if not any(self.categories.values()):
            self.get_categories()
            
        # Set up categories for Airth's posts
        post_categories = []
        # Add Airth's Codex category if available
        if self.categories["airths_codex"]:
            post_categories.append(self.categories["airths_codex"])
        # Add Technology & AI category as backup
        if self.categories["technology_ai"]:
            post_categories.append(self.categories["technology_ai"])
        # Fallback to uncategorized
        if not post_categories and self.categories["uncategorized"]:
            post_categories.append(self.categories["uncategorized"])
            
        # Process tags based on keywords
        tag_list = []
        if keywords:
            # Add common AI tags plus specific keywords
            effective_keywords = keywords + self.common_ai_tags[:3]  # Add a few common AI tags
            tag_list = self.get_tags(effective_keywords)
            
        # Create the post with categories and tags
        return self.create_post(
            title=title,
            content=content,
            excerpt=excerpt,
            status=status,
            categories=post_categories,
            tags=tag_list
        )
    
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
            # Test API connection and verify categories
            categories = self.get_categories()
            if categories:
                self.logger.info(f"WordPress connection verified. Found {len(categories)} categories.")
                results["categories_found"] = len(categories)
            else:
                self.logger.warning("Could not retrieve WordPress categories.")
                results["warnings"] = ["Could not verify WordPress connection"]
            
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
    print(f"Categories found: {results.get('categories_found', 'None')}")
    
    if results["errors"]:
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")