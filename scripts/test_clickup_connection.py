"""
Test script to verify ClickUp API connectivity and credentials.
"""
import os
import sys
import requests
from pathlib import Path

# Add parent directory to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import dotenv for environment variable loading
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(project_root, 'config', '.env')
load_dotenv(env_path)

def test_clickup_api():
    """Test connection to the ClickUp API using credentials from .env"""
    # Get API credentials
    api_token = os.getenv("CLICKUP_TOKEN")
    workspace_id = os.getenv("CLICKUP_WORKSPACE_ID")
    list_id = os.getenv("CLICKUP_CONTENT_LIST_ID")
    
    print(f"Testing ClickUp API connection with:")
    print(f"  API Token: {api_token[:8]}...{api_token[-4:] if api_token else 'None'}")
    print(f"  Workspace ID: {workspace_id}")
    print(f"  List ID: {list_id}")
    print()
    
    if not api_token:
        print("ERROR: No ClickUp API token found in environment variables.")
        return False
    
    # Set up headers
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }
    
    # Test 1: Get authenticated user info
    print("Test 1: Fetching authenticated user info...")
    try:
        user_response = requests.get(
            "https://api.clickup.com/api/v2/user",
            headers=headers
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        print(f"✅ Success! Authenticated as: {user_data.get('user', {}).get('username', 'Unknown')}")
        print(f"   User email: {user_data.get('user', {}).get('email', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   API token may be invalid or expired.")
        return False
    
    # List all available workspaces (teams)
    print("\n=== Available Workspaces ===")
    try:
        teams_response = requests.get(
            "https://api.clickup.com/api/v2/team",
            headers=headers
        )
        teams_response.raise_for_status()
        teams_data = teams_response.json()
        teams = teams_data.get("teams", [])
        
        if not teams:
            print("No workspaces found for this user.")
        else:
            print(f"Found {len(teams)} workspace(s):")
            for team in teams:
                print(f"  • ID: {team.get('id')} - Name: {team.get('name')}")
                
                # Get spaces in this workspace
                print(f"    Spaces in this workspace:")
                spaces_response = requests.get(
                    f"https://api.clickup.com/api/v2/team/{team.get('id')}/space",
                    headers=headers
                )
                spaces_response.raise_for_status()
                spaces_data = spaces_response.json()
                spaces = spaces_data.get("spaces", [])
                
                if not spaces:
                    print("      No spaces found.")
                else:
                    for space in spaces:
                        print(f"      • Space ID: {space.get('id')} - Name: {space.get('name')}")
                        
                        # Get folders in this space
                        print(f"        Folders in this space:")
                        folders_response = requests.get(
                            f"https://api.clickup.com/api/v2/space/{space.get('id')}/folder",
                            headers=headers
                        )
                        
                        try:
                            folders_response.raise_for_status()
                            folders_data = folders_response.json()
                            folders = folders_data.get("folders", [])
                            
                            if not folders:
                                print("          No folders found.")
                            else:
                                for folder in folders:
                                    print(f"          • Folder ID: {folder.get('id')} - Name: {folder.get('name')}")
                                    
                                    # Get lists in this folder
                                    print(f"            Lists in this folder:")
                                    lists_response = requests.get(
                                        f"https://api.clickup.com/api/v2/folder/{folder.get('id')}/list",
                                        headers=headers
                                    )
                                    lists_response.raise_for_status()
                                    lists_data = lists_response.json()
                                    lists = lists_data.get("lists", [])
                                    
                                    if not lists:
                                        print("              No lists found.")
                                    else:
                                        for list_item in lists:
                                            print(f"              • List ID: {list_item.get('id')} - Name: {list_item.get('name')}")
                        except Exception as e:
                            print(f"          Error fetching folders: {e}")
                            
                        # Get folderless lists in this space
                        print(f"        Lists directly in this space:")
                        lists_response = requests.get(
                            f"https://api.clickup.com/api/v2/space/{space.get('id')}/list",
                            headers=headers
                        )
                        
                        try:
                            lists_response.raise_for_status()
                            lists_data = lists_response.json()
                            lists = lists_data.get("lists", [])
                            
                            if not lists:
                                print("          No direct lists found.")
                            else:
                                for list_item in lists:
                                    print(f"          • List ID: {list_item.get('id')} - Name: {list_item.get('name')}")
                        except Exception as e:
                            print(f"          Error fetching direct lists: {e}")
                
    except Exception as e:
        print(f"❌ Error listing workspaces: {e}")
    
    return True
    
if __name__ == "__main__":
    print("=== ClickUp API Connection Test ===")
    success = test_clickup_api()
    print("\n=== Test Completed ===")
    print(f"Overall result: {'Successful' if success else 'Failed'}")