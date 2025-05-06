#!/usr/bin/env python3
"""
Simplified WordPress REST API test focusing on creating posts
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
wp_site_url = os.getenv("WP_SITE_URL", "https://elidorascodex.com")
wp_user = os.getenv("WP_USER", "").lower() 
wp_app_pass = os.getenv("WP_APP_PASS", "")

# Remove spaces from application password
app_pass_no_spaces = wp_app_pass.replace(" ", "")

print(f"=== WordPress Simple Post Test ===")
print(f"Site URL: {wp_site_url}")

# Create a test post with current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
title = f"Simple Test Post - {timestamp}"
content = f"<p>This is a test post created at {timestamp}.</p>"

# Post data in JSON format
post_data = {
    "title": title,
    "content": content,
    "status": "draft"
}

print("\nCreating test post...")
print(f"Title: {title}")

# Different authentication methods to try
auth_methods = [
    {
        "name": "Bearer token",
        "headers": {
            "Authorization": f"Bearer {app_pass_no_spaces}",
            "Content-Type": "application/json"
        }
    },
    {
        "name": "Basic auth (username + password)",
        "auth": (wp_user, wp_app_pass)
    },
    {
        "name": "Basic auth (username + password without spaces)",
        "auth": (wp_user, app_pass_no_spaces)
    },
    {
        "name": "API key as parameter",
        "params": {
            "api_key": app_pass_no_spaces
        }
    }
]

# Try each authentication method
for method in auth_methods:
    print(f"\nTrying authentication method: {method['name']}")
    
    try:
        response = None
        if "headers" in method:
            response = requests.post(
                f"{wp_site_url}/wp-json/wp/v2/posts",
                headers=method["headers"],
                json=post_data
            )
        elif "auth" in method:
            response = requests.post(
                f"{wp_site_url}/wp-json/wp/v2/posts",
                auth=method["auth"],
                json=post_data,
                headers={"Content-Type": "application/json"}
            )
        elif "params" in method:
            response = requests.post(
                f"{wp_site_url}/wp-json/wp/v2/posts",
                params=method["params"],
                json=post_data,
                headers={"Content-Type": "application/json"}
            )
        
        if response:
            print(f"Status code: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"SUCCESS! Post created with {method['name']} authentication")
                post = response.json()
                print(f"Post ID: {post.get('id')}")
                print(f"Post URL: {post.get('link')}")
                break  # Stop testing if successful
            else:
                print(f"Failed: {response.text[:150]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

print("\nTest completed.")