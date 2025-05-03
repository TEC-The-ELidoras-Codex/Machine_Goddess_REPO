#!/usr/bin/env python3
"""
Final WordPress authentication test using multiple approaches
"""
import requests
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
wp_user = os.getenv('WP_USER', 'Elidorascodex').lower()  # Convert to lowercase
wp_app_pass = os.getenv('WP_APP_PASS', 'H2SA yjUd KZy4 BUEY wdc7 7fNR')  # With spaces
wp_url = os.getenv('WP_URL', 'https://elidorascodex.com')

print("=== WordPress Alternative Authentication Test ===")
print(f"WordPress URL: {wp_url}")
print(f"Username: {wp_user}")
print(f"App Password: {wp_app_pass}")

# Test 1: Direct Requests auth parameter approach
def test_direct_auth_param():
    """Test using direct auth parameter in requests"""
    print("\nTest 1: Using requests auth parameter")
    
    try:
        response = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts",
            auth=(wp_user, wp_app_pass)
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success! Authentication worked with direct auth parameter")
            return True
        else:
            print(f"❌ Failed: {response.text[:100]}...")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test 2: WordPress.com specific authentication
def test_wpcom_auth():
    """Test WordPress.com specific authentication"""
    print("\nTest 2: Using WordPress.com specific authentication")
    
    try:
        # Try with Authorization header
        headers = {
            "User-Agent": "WordPress API Python Client",
            "Authorization": f"Bearer {wp_app_pass.replace(' ', '')}"
        }
        
        response = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts",
            headers=headers
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success! Authentication worked with Bearer token")
            return True
        else:
            print(f"❌ Failed: {response.text[:100]}...")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test 3: Try with WordPress REST API Authentication plugin format
def test_rest_api_auth():
    """Test WordPress REST API Authentication plugin format"""
    print("\nTest 3: Using WordPress REST API Authentication format")
    
    try:
        # Some plugins use a different authentication method
        headers = {
            "X-WP-Nonce": wp_app_pass.replace(' ', '')
        }
        
        response = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts",
            headers=headers
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success! Authentication worked with X-WP-Nonce")
            return True
        else:
            print(f"❌ Failed: {response.text[:100]}...")
            
            # Check if we received any posts (sometimes this works without auth)
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"NOTE: Received {len(data)} posts, but this might be public access")
            except:
                pass
                
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Run the tests
test_direct_auth_param()
test_wpcom_auth()
test_rest_api_auth()

print("\n=== Authentication Test Summary ===")
print("If any of the tests above succeeded, use that authentication method in your code.")
print("If all tests failed, you may need to:")
print("1. Double-check your WordPress username (it may be different from what's displayed)")
print("2. Try generating a password from WordPress.com's security settings instead of the site admin")
print("3. Check if there are any WordPress security plugins blocking API authentication")