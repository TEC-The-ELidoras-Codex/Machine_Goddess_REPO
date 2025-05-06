#!/usr/bin/env python3
"""
Test WordPress posting using XML-RPC API
This is an alternative to REST API that might work better with WordPress.com sites
"""
import os
from datetime import datetime
from dotenv import load_dotenv
import xmlrpc.client

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# WordPress credentials
wp_site_url = os.getenv("WP_SITE_URL", "https://elidorascodex.com")
wp_user = os.getenv("WP_USER", "")
wp_app_pass = os.getenv("WP_APP_PASS", "")  # Use the password with spaces

print(f"=== WordPress XML-RPC API Test ===")
print(f"Site URL: {wp_site_url}")
print(f"Username: {wp_user}")

# XML-RPC API URL (standard for WordPress)
xmlrpc_url = f"{wp_site_url}/xmlrpc.php"
print(f"XML-RPC URL: {xmlrpc_url}")

try:
    # Create XML-RPC client
    server = xmlrpc.client.ServerProxy(xmlrpc_url)
    
    # First, check if the server supports the XML-RPC API
    print("\nChecking XML-RPC API availability...")
    methods = server.system.listMethods()
    
    print(f"XML-RPC API is available with {len(methods)} methods.")
    
    # Check if we can get blog details
    print("\nGetting blog details...")
    try:
        blog_info = server.wp.getOptions(0, wp_user, wp_app_pass)
        print(f"Blog title: {blog_info['blog_title']['value']}")
        print("✅ Authentication successful!")
    except xmlrpc.client.Fault as e:
        print(f"❌ Error getting blog details: {e}")
        print("This could indicate authentication failure.")
    
    # Create a new post
    print("\nCreating a test post...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    post_content = {
        'post_title': f'XML-RPC Test Post - {timestamp}',
        'post_content': f'<p>This is a test post created using XML-RPC API at {timestamp}.</p>',
        'post_status': 'draft'
    }
    
    try:
        post_id = server.wp.newPost(0, wp_user, wp_app_pass, post_content)
        print(f"✅ Post created successfully with ID: {post_id}")
        print(f"View post at: {wp_site_url}/?p={post_id}")
    except xmlrpc.client.Fault as e:
        print(f"❌ Error creating post: {e}")
    
except xmlrpc.client.ProtocolError as e:
    print(f"❌ XML-RPC Protocol Error: {e}")
    if e.errcode == 403:
        print("XML-RPC API might be disabled on this WordPress site.")

except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\nTest completed.")