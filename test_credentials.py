"""
Test script to verify API keys and WordPress credentials
"""
import os
import sys
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
print(f"Loading environment from: {env_path}")
load_dotenv(env_path, override=True)

def test_wordpress_credentials():
    """
    Test WordPress API connection using the credentials in the .env file
    """
    # Get WordPress credentials
    wp_url = os.getenv("WP_SITE_URL") or os.getenv("WP_URL", "https://elidorascodex.com")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_APP_PASS") or os.getenv("WP_PASS")
    
    print("\n--- WordPress Credentials Check ---")
    print(f"URL: {wp_url}")
    print(f"Username: {wp_user}")
    print(f"Password/App Password: {'[Set]' if wp_pass else '[Not Set]'}")

    # Format the API URL
    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/categories"
    
    # Try both with spaces and without spaces in the password
    for password in [wp_pass, wp_pass.replace(" ", "") if wp_pass else None]:
        if not password:
            continue
        
        # Create authorization header
        user_pass = f"{wp_user}:{password}"
        auth_header = f"Basic {base64.b64encode(user_pass.encode()).decode()}"
        
        print(f"\nTesting WordPress connection with {'spaced' if ' ' in password else 'non-spaced'} password...")
        try:
            # Make API request
            response = requests.get(
                api_url, 
                headers={"Authorization": auth_header},
                params={"per_page": 5}
            )
            
            if response.status_code == 200:
                print("✅ SUCCESS! WordPress authentication successful")
                print(f"Categories found: {len(response.json())}")
                return True
            else:
                print(f"❌ ERROR: WordPress returned status code {response.status_code}")
                print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ ERROR: Connection failed: {e}")
    
    print("❌ WordPress authentication failed with all methods")
    return False

def test_openai_api():
    """
    Test OpenAI API connection using the API key in the .env file
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    print("\n--- OpenAI API Key Check ---")
    print(f"API Key: {'[Set]' if openai_key else '[Not Set]'}")
    print(f"API Key Length: {len(openai_key) if openai_key else 0} characters")
    
    if not openai_key:
        print("❌ ERROR: OpenAI API key not found in environment")
        return False
    
    print("\nInformation: To fully test the OpenAI API, you should install the openai package:")
    print("pip install openai==1.3.0")
    print("Then you can test API calls with a simple script.")
    
    return True

if __name__ == "__main__":
    print("=== CREDENTIALS TEST ===")
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Test each service
    test_wordpress_credentials()
    test_openai_api()
    
    # Provide overall results
    print("\n=== SUMMARY ===")
    print("This script tested if your credentials are being loaded correctly.")
    print("If the WordPress test failed, check:")
    print("1. Your WP_USER matches your WordPress username exactly")
    print("2. Your WP_APP_PASS is a valid application password (not login password)")
    print("3. Your WordPress site has REST API enabled")
    
    print("\nIf the OpenAI test showed [Set] but your agent still fails:")
    print("1. Make sure openai Python package is installed properly")
    print("2. Update your airth_agent.py to use the API key directly")