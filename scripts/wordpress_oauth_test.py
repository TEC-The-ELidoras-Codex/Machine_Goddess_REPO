#!/usr/bin/env python3
"""
WordPress OAuth1 Authentication Test
Tests posting to WordPress.com sites using OAuth1 authentication
"""
import os
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
wp_site_url = os.getenv("WP_SITE_URL", "https://elidorascodex.com")
wp_user = os.getenv("WP_USER", "").lower()
wp_app_pass = os.getenv("WP_APP_PASS", "")

# Remove spaces from application password
app_pass_no_spaces = wp_app_pass.replace(" ", "")

print(f"=== WordPress OAuth1 Test ===")
print(f"Site URL: {wp_site_url}")
print(f"Username: {wp_user}")

try:
    # For this test, we'll try using the app password as both consumer key and secret
    auth = OAuth1(
        client_key=app_pass_no_spaces, 
        client_secret=app_pass_no_spaces,
        resource_owner_key=wp_user, 
        resource_owner_secret=app_pass_no_spaces
    )
    
    # First try to get categories to test read access
    print("\nTesting read access (categories)...")
    response = requests.get(
        f"{wp_site_url}/wp-json/wp/v2/categories",
        auth=auth
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"Success! Found {len(categories)} categories.")
        for category in categories[:3]:  # Show first 3
            print(f" - {category.get('name')} (ID: {category.get('id')})")
    else:
        print(f"Error: {response.text[:200]}")
    
    # Test writing a post
    print("\nTesting write access (create post)...")
    
    # Create post data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    post_data = {
        "title": f"OAuth1 Test Post - {timestamp}",
        "content": f"<p>This is a test post created using OAuth1 authentication at {timestamp}.</p>",
        "status": "draft"
    }
    
    # Try to create post
    response = requests.post(
        f"{wp_site_url}/wp-json/wp/v2/posts",
        auth=auth,
        json=post_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code in [200, 201]:
        post = response.json()
        print(f"Success! Created post: {post.get('title', {}).get('rendered', '')}")
        print(f"Post ID: {post.get('id')}")
        print(f"Post URL: {post.get('link')}")
    else:
        print(f"Error: {response.text[:200]}")
    
except ImportError:
    print("Error: requests_oauthlib package is not installed.")
    print("Please install it using: pip install requests-oauthlib")
except Exception as e:
    print(f"Error: {str(e)}")