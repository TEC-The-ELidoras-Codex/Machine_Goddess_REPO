"""
Direct WordPress API test using the exact successful authentication approach
"""
import requests
import json

# Use the exact authentication that worked in your test
auth_header = "Basic ZWxpZG9yYXNjb2RleDpxUmlIREcmTTE1MVdscEdycW5qITcybnE="

# API URL
api_url = "https://elidorascodex.com/wp-json/wp/v2/posts"

# Headers
headers = {
    "Authorization": auth_header,
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

def test_create_post():
    """Test creating a post in WordPress API"""
    print("\nTesting POST request to WordPress API...")
    
    # Test post data
    post_data = {
        "title": "Test Post from Direct API Script",
        "content": "This is a test post created by the direct_wordpress_test.py script.",
        "status": "draft"
    }
    
    response = requests.post(api_url, headers=headers, json=post_data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("Success! Post created successfully.")
        post = response.json()
        print(f"Created post ID: {post.get('id')}")
        print(f"Post URL: {post.get('link')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("=== WordPress API Direct Test ===")
    test_get_posts()
    test_create_post()