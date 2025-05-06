#!/usr/bin/env python3
"""
Simple WordPress public API test to verify the API is working
"""
import requests
import os
import json

# WordPress site URL
wp_url = "https://elidorascodex.com"

print("=== WordPress Public API Test ===")
print(f"Testing public API access to: {wp_url}")

# Test endpoints that don't require authentication
endpoints = [
    "/wp-json",                    # Basic WP REST API
    "/wp-json/wp/v2/posts",        # Public posts
    "/wp-json/wp/v2/categories",   # Categories
    "/wp-json/wp/v2/users"         # Users (public info only)
]

for endpoint in endpoints:
    url = f"{wp_url}{endpoint}"
    print(f"\nTesting endpoint: {url}")
    
    try:
        response = requests.get(url)
        status_code = response.status_code
        
        print(f"Status code: {status_code}")
        
        if status_code == 200:
            print("✅ Success! Endpoint is accessible without authentication")
            data = response.json()
            
            # Print some sample data
            if endpoint == "/wp-json/wp/v2/posts" and data:
                print(f"Found {len(data)} posts")
                if data:
                    print(f"Latest post title: {data[0]['title']['rendered']}")
            elif endpoint == "/wp-json/wp/v2/categories" and data:
                print(f"Found {len(data)} categories")
                if data:
                    print(f"First category: {data[0]['name']}")
            elif endpoint == "/wp-json/wp/v2/users" and data:
                print(f"Found {len(data)} public users")
                if data:
                    print(f"User: {data[0]['name']}")
        else:
            print(f"❌ Failed: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

print("\n=== REST API Access Summary ===")
print("If the endpoints above returned 200 status codes, your WordPress REST API is working correctly.")
print("The authentication issue may be related to:")
print("1. The application password format or generation")
print("2. User permissions in WordPress")
print("3. Security plugins blocking authenticated API access")