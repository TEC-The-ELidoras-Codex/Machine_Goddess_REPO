#!/usr/bin/env python3
"""
Direct WordPress Posting Script for The Elidoras Codex.
This standalone script posts content to WordPress without relying on the full project structure.
"""
import os
import sys
import logging
import json
import requests
from base64 import b64encode
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DirectWP")

# WordPress credentials - hardcoded for testing, should be moved to .env in production
# These values are taken from your existing .env file
WP_SITE_URL = "https://elidorascodex.com"
WP_USER = "elidorascodex_admin"
WP_APP_PASS = "i6i(mY&q2+s_My*"

def get_auth_header():
    """
    Get the authorization header for WordPress API requests.
    
    Returns:
        Dictionary containing the Authorization header
    """
    credentials = f"{WP_USER}:{WP_APP_PASS}"
    token = b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {token}"}

def test_connection():
    """
    Test the WordPress connection and get basic site info.
    
    Returns:
        Boolean indicating if connection was successful
    """
    try:
        # Use a simple endpoint to test connection
        url = f"{WP_SITE_URL}/wp-json"
        headers = get_auth_header()
        
        logger.info(f"Testing connection to {WP_SITE_URL}")
        response = requests.get(url)
        
        if response.status_code == 200:
            site_info = response.json()
            logger.info(f"Successfully connected to {site_info.get('name', 'WordPress site')}")
            return True
        else:
            logger.error(f"Connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

def get_categories():
    """
    Fetch available categories from WordPress.
    
    Returns:
        Dictionary of categories with their IDs
    """
    try:
        url = f"{WP_SITE_URL}/wp-json/wp/v2/categories"
        headers = get_auth_header()
        
        logger.info("Fetching WordPress categories")
        response = requests.get(url, headers=headers, params={"per_page": 100})
        response.raise_for_status()
        
        categories = response.json()
        
        # Map category slugs to IDs
        category_map = {}
        for category in categories:
            slug = category.get("slug", "")
            name = category.get("name", "")
            cat_id = category.get("id")
            
            logger.info(f"Found category: {name} (ID: {cat_id})")
            category_map[slug] = cat_id
            
        return category_map
            
    except Exception as e:
        logger.error(f"Failed to fetch WordPress categories: {e}")
        return {}

def create_post(title, content, excerpt="", status="draft", categories=None, tags=None):
    """
    Create a new post on the WordPress site.
    
    Args:
        title: Post title
        content: Post content (can contain HTML)
        excerpt: Post excerpt
        status: Post status (draft, publish, etc.)
        categories: List of category IDs
        tags: List of tag IDs
        
    Returns:
        Dictionary containing the created post data or error information
    """
    try:
        # Prepare API request
        url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
        headers = {
            **get_auth_header(),
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
        
        # Make the API request
        logger.info(f"Creating WordPress post: '{title}'")
        response = requests.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        
        post_data = response.json()
        post_id = post_data.get("id")
        post_url = post_data.get("link")
        
        logger.info(f"Successfully created post #{post_id}: {post_url}")
        return {
            "success": True,
            "post_id": post_id,
            "post_url": post_url,
            "post_data": post_data
        }
            
    except Exception as e:
        logger.error(f"Failed to create WordPress post: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """
    Main function to test WordPress posting.
    """
    logger.info("Starting direct WordPress posting test")
    
    # Test connection first
    if not test_connection():
        logger.error("Connection test failed. Aborting.")
        return False
    
    # Get categories
    categories = get_categories()
    if not categories:
        logger.warning("No categories found. Will use default category.")
    
    # Find important categories
    category_ids = []
    if "uncategorized" in categories:
        category_ids.append(categories["uncategorized"])
    
    # Create a test post with current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"Test Post from Direct WordPress Script - {timestamp}"
    content = f"""
    <p>This is a test post created by the direct WordPress posting script.</p>
    <p>Created at: {timestamp}</p>
    <p>This post confirms that the WordPress posting functionality is working correctly.</p>
    """
    excerpt = f"Test post created at {timestamp}"
    
    # Create the post as a draft
    result = create_post(
        title=title,
        content=content,
        excerpt=excerpt,
        status="draft",  # Use "draft" so it doesn't go live immediately
        categories=category_ids
    )
    
    if result.get("success"):
        post_id = result.get("post_id")
        post_url = result.get("post_url")
        logger.info(f"Test post created successfully!")
        logger.info(f"Post ID: {post_id}")
        logger.info(f"Post URL: {post_url}")
        logger.info(f"Post Status: Draft (login to WordPress to publish)")
        return True
    else:
        logger.error(f"Failed to create test post: {result.get('error')}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)