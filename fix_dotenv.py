"""
This script will fix environment variable loading issues
by directly loading the .env file and printing the results
"""
import os
from dotenv import load_dotenv

# Load from the specific path
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

# Force load the .env file with verbose output
load_dotenv(env_path, verbose=True, override=True)

# Check if variables are loaded
wp_user = os.getenv("WP_USER")
wp_app_pass = os.getenv("WP_APP_PASS")
openai_key = os.getenv("OPENAI_API_KEY")

print("\nEnvironment Variables Check:")
print(f"WP_USER: {'✓ Set' if wp_user else '✗ Not set'}")
print(f"WP_APP_PASS: {'✓ Set' if wp_app_pass else '✗ Not set'}")
print(f"OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")

if not wp_user or not wp_app_pass or not openai_key:
    print("\n⚠️ Some environment variables are missing!")
    print("Make sure your .env file has the correct format and values.")
else:
    print("\n✅ All required environment variables are set!")
    print("You should be able to run your agents now.")