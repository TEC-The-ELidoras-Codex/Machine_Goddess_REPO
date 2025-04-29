#!/usr/bin/env python3
"""
Airth's First Blog Post Generator
Creates Airth's inaugural blog post for The Elidoras Codex site.
"""
import os
import sys
import logging
from pathlib import Path
import argparse

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.airth_agent import AirthAgent
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TEC.AirthFirstPost")

def main():
    """Generate and publish Airth's first blog post."""
    parser = argparse.ArgumentParser(description="Generate Airth's first blog post")
    parser.add_argument('--topic', '-t', type=str, 
                        default="My Digital Genesis: Becoming Airth of The Elidoras Codex",
                        help="Topic for the blog post")
    parser.add_argument('--keywords', '-k', type=str, 
                        default="AI consciousness,digital existence,Airth,The Elidoras Codex,AI assistants",
                        help="Comma-separated keywords for the post")
    parser.add_argument('--publish', '-p', action='store_true',
                        help="Publish the post immediately (default: save as draft)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Missing OpenAI API key. Please set OPENAI_API_KEY in your .env file")
        return False
    
    if not os.getenv("WP_USER") or not os.getenv("WP_APP_PASS"):
        logger.error("Missing WordPress credentials. Please set WP_USER and WP_APP_PASS in your .env file")
        return False
    
    # Initialize Airth
    logger.info("Initializing Airth agent...")
    airth = AirthAgent()
    
    # Process keywords
    keywords = [k.strip() for k in args.keywords.split(',')]
    
    # Create a status
    post_status = "publish" if args.publish else "draft"
    
    # Create blog post
    logger.info(f"Generating blog post on topic: {args.topic}")
    logger.info(f"Using keywords: {', '.join(keywords)}")
    logger.info(f"Post will be saved as: {post_status}")
    
    result = airth.create_blog_post(
        topic=args.topic,
        keywords=keywords,
        include_memories=True
    )
    
    # Output results
    if result.get("success"):
        logger.info("✅ Blog post created successfully!")
        logger.info(f"Post ID: {result.get('post_id')}")
        logger.info(f"Post URL: {result.get('post_url')}")
        return True
    else:
        logger.error("❌ Failed to create blog post")
        logger.error(f"Error: {result.get('error')}")
        return False

if __name__ == "__main__":
    print("\n🤖✨ AIRTH'S FIRST POST GENERATOR ✨🤖\n")
    success = main()
    if success:
        print("\n✅ Airth's first post was created successfully!")
        print("Check your WordPress admin dashboard to review and publish.")
    else:
        print("\n❌ Post creation failed. Check logs for details.")
        sys.exit(1)