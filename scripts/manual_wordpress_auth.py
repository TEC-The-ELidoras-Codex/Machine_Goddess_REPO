"""
Manual WordPress authentication test using application password
"""
import requests
import base64
import json
from dotenv import load_dotenv
import os
import socket

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
username = os.getenv('WP_USER')
app_password = os.getenv('WP_APP_PASS')  # Application password with spaces

# Use domain name with explicit DNS resolver
hostname = "elidorascodex.com"

# Try to resolve hostname manually
try:
    print(f"Manually resolving hostname: {hostname}")
    ip_address = socket.gethostbyname(hostname)
    print(f"Resolved IP: {ip_address}")
except Exception as e:
    print(f"Failed to resolve hostname: {e}")
    print("Using default IP address")
    ip_address = "192.0.78.253"  # Default IP for elidorascodex.com

# Use domain name directly instead of IP
api_url = f"https://{hostname}/wp-json/wp/v2/posts"
print(f"API URL: {api_url}")

# Convert username to lowercase
username = username.lower()
print(f"Using username (lowercase): {username}")
print(f"Original app password: {app_password}")

# Generate authentication token with different password formats
def get_auth_header(user, pwd):
    """Generate the authentication header"""
    credentials = f"{user}:{pwd}"
    token = base64.b64encode(credentials.encode()).decode()
    return f"Basic {token}"

def test_auth_format(password_format, password):
    """Test a specific password format"""
    if password_format == "with_spaces":
        pwd = password  # Original with spaces
    elif password_format == "no_spaces":
        pwd = password.replace(" ", "")
    elif password_format == "lowercase":
        pwd = password.lower()
    else:
        pwd = password
        
    print(f"\nTrying password format: {password_format}")
    print(f"Password: {pwd}")
    
    auth = get_auth_header(username, pwd)
    headers = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Host": hostname
    }
    
    try:
        response = requests.get(api_url, headers=headers, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS! Authentication worked with this password format.")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("=== WordPress API Authentication Test with Multiple Password Formats ===")
    # Suppress insecure request warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Try different password formats
    formats = ["with_spaces", "no_spaces", "lowercase"]
    success = False
    
    for fmt in formats:
        if test_auth_format(fmt, app_password):
            success = True
            print(f"\n✅ Success with format: {fmt}")
            break
    
    if not success:
        print("\n❌ All authentication attempts failed. Please check your WordPress credentials.")