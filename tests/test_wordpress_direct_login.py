#!/usr/bin/env python3
"""
Test WordPress direct login using session-based authentication instead of application passwords
"""
import requests
import os
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
username = os.getenv('WP_USER', '')
if not username:
    print("WP_USER not found in environment variables")
    exit(1)

# Convert to lowercase as you mentioned it's case sensitive
username = username.lower()
print(f"Using username (lowercase): {username}")

# Try different password formats
app_password = os.getenv('WP_APP_PASS', '')
no_spaces_password = app_password.replace(" ", "")
lowercase_password = app_password.lower()

# WordPress URLs
wp_url = os.getenv('WP_SITE_URL', 'https://elidorascodex.com')
api_url = f"{wp_url}/wp-json/wp/v2"

print("=== WordPress Direct Test ===")
print(f"Site URL: {wp_url}")
print(f"API URL: {api_url}")

def test_basic_auth(user, password, password_type):
    """Test Basic Auth with the given credentials"""
    print(f"\nTesting Basic Auth with {password_type}...")
    
    auth = (user, password)
    headers = {
        "User-Agent": "Mozilla/5.0 WordPress API Test"
    }
    
    try:
        # Try to list posts
        response = requests.get(f"{api_url}/posts", auth=auth, headers=headers)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Authentication worked.")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

# Test with different password formats
print("\nTesting different password formats...")
formats = [
    ("Original with spaces", app_password),
    ("Without spaces", no_spaces_password),
    ("Lowercase", lowercase_password)
]

for desc, pwd in formats:
    success = test_basic_auth(username, pwd, desc)
    if success:
        print(f"✅ Authentication successful with {desc}")
        break
else:
    print("\n❌ All authentication attempts failed.")
    
    # Try one more test with a simple GET request to check site availability
    print("\nChecking if the WordPress site is accessible...")
    try:
        response = requests.get(wp_url)
        print(f"Site access status code: {response.status_code}")
        if response.status_code == 200:
            print("WordPress site is accessible.")
            print("Please check your application password configuration in WordPress.")
        else:
            print("WordPress site is not accessible. Check your site URL.")
    except Exception as e:
        print(f"Error connecting to WordPress site: {e}")