"""
Test script to verify OpenAI integration works properly.
This will help diagnose issues with the openai module import and client initialization.
"""
import os
import sys
from pathlib import Path

# Add project root to path to ensure imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Print Python environment information for debugging
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Sys.path:")
for path in sys.path:
    print(f"  - {path}")

# Load environment variables first
try:
    from dotenv import load_dotenv
    print("Successfully imported python-dotenv")
    
    # Try to load from different potential .env locations
    env_paths = [
        os.path.join(project_root, 'config', '.env'),  # config/.env
        os.path.join(project_root, '.env'),            # .env in project root
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"Loading environment variables from: {env_path}")
            load_dotenv(env_path, override=True)
            break
    else:
        print("WARNING: No .env file found!")
except ImportError as e:
    print(f"ERROR: Could not import dotenv: {e}")
    print("Please run 'pip install python-dotenv' to install it.")
    sys.exit(1)

# Verify API key was loaded
api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API key length: {len(api_key)}")
    print(f"API key prefix: {api_key[:10]}...")

# Try to import OpenAI (using the newer client approach)
try:
    from openai import OpenAI
    print("Successfully imported OpenAI (new client)")
    
    # Initialize the client 
    client = OpenAI(api_key=api_key)
    print("Successfully initialized OpenAI client")
    
    # Test a simple completion
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ]
        )
        print("Successfully made API call!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"ERROR making OpenAI API call: {e}")

except ImportError as e:
    print(f"ERROR importing OpenAI: {e}")
    
    # Try alternative import style (older client)
    try:
        import openai
        print("Successfully imported OpenAI (old client)")
        
        # Configure API key
        openai.api_key = api_key
        print("Set API key for old client")
        
        try:
            # Test with older client style
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt="Say hello!",
                max_tokens=50
            )
            print("Successfully made API call with old client!")
            print(f"Response: {response['choices'][0]['text'].strip()}")
        except Exception as e:
            print(f"ERROR making OpenAI API call with old client: {e}")
            
    except ImportError as e:
        print(f"ERROR: Could not import OpenAI in any way: {e}")
        print("Please run 'pip install openai' to install it.")
        sys.exit(1)

print("\nTest complete. Check the results above to diagnose any issues.")