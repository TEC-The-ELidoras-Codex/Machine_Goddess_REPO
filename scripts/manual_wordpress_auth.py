"""
Manual WordPress authentication test using direct username and password
"""
import requests
import base64
import json

# WordPress credentials
username = "Elidorascodex"
password = "qRiHDG&M151WlpGrqnj!72nq"

# API URL
api_url = "https://elidorascodex.com/wp-json/wp/v2/posts"

# Generate authentication token
def get_auth_header(user, pwd):
    """Generate the authentication header"""
    credentials = f"{user}:{pwd}"
    token = base64.b64encode(credentials.encode()).decode()
    print(f"Generated token: Basic {token}")
    return f"Basic {token}"

# Headers
auth = get_auth_header(username, password)
headers = {
    "Authorization": auth,
    "Content-Type": "application/json"
}

def test_get_posts():
    """Test retrieving posts from WordPress API"""
    print("Testing GET request to WordPress API...")
    
    response = requests.get(api_url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! Authentication worked.")
        posts = response.json()
        print(f"Retrieved {len(posts)} posts.")
        print(f"First post title: {posts[0]['title']['rendered']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("=== WordPress API Manual Authentication Test ===")
    test_get_posts()