"""
Test WordPress API with application password (both with and without spaces)
"""
import requests
import base64

# WordPress credentials
username = "Elidorascodex"
app_password_with_spaces = "BCI1 8qup YEan WJgV No53 i5Kf"
app_password_no_spaces = app_password_with_spaces.replace(" ", "")

# API URL
api_url = "https://elidorascodex.com/wp-json/wp/v2/posts"

def test_auth(password):
    """Test authentication with the given password"""
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {token}"
    
    print(f"\n=== Testing with {'spaces' if ' ' in password else 'no spaces'} ===")
    print(f"Password: {password}")
    print(f"Generated token: {auth_header}")
    
    # Headers
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    print("Testing GET request to WordPress API...")
    response = requests.get(api_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Authentication worked.")
        posts = response.json()
        print(f"Retrieved {len(posts)} posts.")
        print(f"First post title: {posts[0]['title']['rendered']}")
        return True
    else:
        print(f"❌ ERROR: {response.text}")
        return False

if __name__ == "__main__":
    print("=== WordPress App Password Test ===")
    
    # Try with spaces first
    with_spaces_result = test_auth(app_password_with_spaces)
    
    # Try without spaces
    no_spaces_result = test_auth(app_password_no_spaces)