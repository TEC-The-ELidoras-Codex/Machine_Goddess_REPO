#!/usr/bin/env python3
"""
Comprehensive WordPress authentication test
Tests multiple username and password formats to identify the correct combination
"""
import requests
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
wp_user = os.getenv('WP_USER')
wp_app_pass = os.getenv('WP_APP_PASS')
wp_url = os.getenv('WP_URL')

print(f"Original username: {wp_user}")
print(f"Original app password: {wp_app_pass}")
print(f"WordPress URL: {wp_url}")

# API endpoint
api_url = f"{wp_url}/wp-json/wp/v2/posts"

# Try different username formats
username_formats = [
    {"name": "Original", "value": wp_user},
    {"name": "Lowercase", "value": wp_user.lower()},
    {"name": "No special chars", "value": ''.join(c for c in wp_user if c.isalnum())},
    {"name": "Email format", "value": f"{wp_user.lower()}@elidorascodex.com"}
]

# Try different password formats
password_formats = [
    {"name": "Original with spaces", "value": wp_app_pass},
    {"name": "No spaces", "value": wp_app_pass.replace(' ', '')},
    {"name": "Lowercase with spaces", "value": wp_app_pass.lower()},
    {"name": "Lowercase no spaces", "value": wp_app_pass.lower().replace(' ', '')},
    {"name": "Uppercase with spaces", "value": wp_app_pass.upper()},
    {"name": "Uppercase no spaces", "value": wp_app_pass.upper().replace(' ', '')}
]

def test_auth(username, password, u_format, p_format):
    """Test authentication with given username and password format"""
    print(f"\n🔍 Testing: {u_format} username + {p_format} password")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
    # Create auth header
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {token}"
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        status_code = response.status_code
        
        print(f"Status code: {status_code}")
        
        if status_code == 200:
            print(f"✅ SUCCESS! Authentication worked with {u_format} username + {p_format} password")
            return True
        else:
            print(f"❌ Failed: {response.text[:100]}...")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test site accessibility first
print("\n🌐 Testing WordPress site accessibility...")
try:
    response = requests.get(wp_url)
    if response.status_code == 200:
        print(f"✅ WordPress site is accessible (status {response.status_code})")
    else:
        print(f"⚠️ WordPress site returned status {response.status_code}")
except Exception as e:
    print(f"❌ Error accessing WordPress site: {e}")

# Test API endpoint accessibility
print("\n🌐 Testing WordPress API accessibility...")
try:
    response = requests.get(f"{wp_url}/wp-json")
    if response.status_code == 200:
        print(f"✅ WordPress API is accessible (status {response.status_code})")
    else:
        print(f"⚠️ WordPress API returned status {response.status_code}")
except Exception as e:
    print(f"❌ Error accessing WordPress API: {e}")

print("\n🔄 Testing all username/password combinations...")
success = False

# Try all combinations
for u_format in username_formats:
    if success:
        break
    
    for p_format in password_formats:
        if test_auth(u_format["value"], p_format["value"], u_format["name"], p_format["name"]):
            success = True
            print(f"\n✅✅✅ WORKING COMBINATION FOUND: {u_format['name']} username + {p_format['name']} password")
            print(f"Username: {u_format['value']}")
            print(f"Password: {p_format['value']}")
            
            print("\nUpdate your .env file with these values:")
            print(f"WP_USER={u_format['value']}")
            print(f"WP_APP_PASS={p_format['value']}")
            
            break

if not success:
    print("\n❌❌❌ No working combination found.")
    print("Suggestions:")
    print("1. Generate a new application password in WordPress")
    print("2. Check if the REST API is enabled and accessible")
    print("3. Verify the WordPress site URL is correct")