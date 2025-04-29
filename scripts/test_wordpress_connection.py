#!/usr/bin/env python3
"""
WordPress Connection Test Script for The Elidoras Codex.
Tests the WordPress REST API connectivity and validates category structure.
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import our modules
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from agents.wp_poster import WordPressAgent
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TEC.WP_Test")

def main():
    """Main test function to verify WordPress connectivity."""
    logger.info("Starting WordPress connection test")
    
    # Load environment variables from .env file - specify the exact path
    env_path = os.path.join(parent_dir, "config", ".env")
    logger.info(f"Loading environment from: {env_path}")
    load_dotenv(env_path)
    
    # Check required environment variables
    wp_url = os.getenv("WP_SITE_URL") or os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_APP_PASS") or os.getenv("WP_PASS")
    
    if not wp_url or not wp_user or not wp_pass:
        logger.error("Missing required WordPress environment variables.")
        logger.error(f"WP_SITE_URL/WP_URL: {'✓' if wp_url else '✗'}")
        logger.error(f"WP_USER: {'✓' if wp_user else '✗'}")
        logger.error(f"WP_APP_PASS/WP_PASS: {'✓' if wp_pass else '✗'}")
        logger.error(f"Please ensure these are set in: {env_path}")
        return False
    
    logger.info(f"WordPress URL: {wp_url}")
    logger.info(f"WordPress User: {wp_user}")
    logger.info("WordPress App Password: [REDACTED]")
    
    # Initialize WordPress agent with the config path
    config_path = os.path.join(parent_dir, "config")
    logger.info(f"Using config path: {config_path}")
    wp_agent = WordPressAgent(config_path)
    
    # Test getting categories
    logger.info("Testing category retrieval...")
    categories = wp_agent.get_categories()
    
    if not categories:
        logger.error("Failed to retrieve categories. Check credentials and API connection.")
        return False
    
    logger.info(f"Successfully retrieved {len(categories)} categories:")
    for key, cat_id in wp_agent.categories.items():
        if cat_id:
            logger.info(f"  - {key}: ID {cat_id}")
        else:
            logger.warning(f"  - {key}: Not found")
    
    # Test if Airth's category was found
    if wp_agent.categories["airths_codex"]:
        logger.info("✅ Success: Found 'Airth's Codex' category")
    else:
        logger.warning("⚠️ Warning: 'Airth's Codex' category not found")
    
    # Test tag retrieval
    logger.info("Testing tag functionality...")
    test_tags = ["AI ethics", "AI storytelling", "test-tag-" + datetime.now().strftime("%Y%m%d%H%M%S")]
    logger.info(f"Searching for tags: {', '.join(test_tags)}")
    
    tag_ids = wp_agent.get_tags(test_tags)
    if tag_ids:
        logger.info(f"✅ Success: Retrieved/created {len(tag_ids)} tags")
    else:
        logger.warning("⚠️ Warning: No tags retrieved or created")
    
    # All tests passed
    logger.info("WordPress connection test completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ WordPress connection successful!")
        sys.exit(0)
    else:
        print("\n❌ WordPress connection test failed. Check logs for details.")
        sys.exit(1)