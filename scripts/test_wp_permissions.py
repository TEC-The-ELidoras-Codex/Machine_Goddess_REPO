#!/usr/bin/env python3
"""
Test WordPress REST API permissions
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
wp_site_url = os.getenv("WP_SITE_URL", "https://elidorascodex.com")
wp_user = os.getenv("WP_USER", "").lower()
wp_app_pass = os.getenv("WP_APP_PASS", "").replace(" ", "") # No spaces for bearer token

print(f"=== WordPress Permissions Test ===")
print(f"Site URL: {wp_site_url}")

# Use Bearer token authentication that worked for categories
headers = {
    "Authorization": f"Bearer {wp_app_pass}",
    "Content-Type": "application/json"
}

# Test REST API discovery endpoint to check available routes and permissions
try:
    print("\nChecking available REST API routes and permissions...")
    response = requests.get(f"{wp_site_url}/wp-json", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if we have a routes section
        if "routes" in data:
            # Look specifically for post routes
            post_routes = [route for route in data["routes"].keys() if "/wp/v2/posts" in route]
            
            print(f"Found {len(post_routes)} post-related routes:")
            for route in post_routes:
                print(f" - {route}")
                
            # Check if we have a permission check endpoint
            if "/wp/v2/posts" in data["routes"]:
                post_endpoint = data["routes"]["/wp/v2/posts"]
                if "methods" in post_endpoint:
                    print(f"\nMethods allowed on /wp/v2/posts:")
                    for method in post_endpoint["methods"]:
                        print(f" - {method}")
                
                # Check if POST is listed as an allowed method
                if "methods" in post_endpoint and "POST" in post_endpoint["methods"]:
                    print("\n✅ POST method is allowed on /wp/v2/posts endpoint")
                else:
                    print("\n❌ POST method is NOT allowed on /wp/v2/posts endpoint")
        else:
            print("No routes information found in API response")
    else:
        print(f"Error accessing REST API: {response.status_code}")
        print(response.text[:200])

except Exception as e:
    print(f"Error: {str(e)}")

# Check basic site information and user details
try:
    print("\nChecking site information...")
    response = requests.get(f"{wp_site_url}/wp-json", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Site Name: {data.get('name', 'Unknown')}")
        print(f"Site Description: {data.get('description', 'No description')}")
        
        # Check current user - this should show if we're authenticated
        print("\nChecking current user...")
        response = requests.get(f"{wp_site_url}/wp-json/wp/v2/users/me", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Successfully authenticated as: {user.get('name', 'Unknown user')}")
            print(f"Username: {user.get('slug', 'Unknown')}")
            print(f"Roles: {', '.join(user.get('roles', ['Unknown']))}")
            
            # Check if the user has the "publish_posts" capability
            if "capabilities" in user and "publish_posts" in user["capabilities"]:
                if user["capabilities"]["publish_posts"]:
                    print("✅ User has the 'publish_posts' capability")
                else:
                    print("❌ User does NOT have the 'publish_posts' capability")
        else:
            print(f"❌ Not authenticated or missing permissions: {response.status_code}")
            print(response.text[:200])
    else:
        print(f"Error accessing site information: {response.status_code}")

except Exception as e:
    print(f"Error: {str(e)}")