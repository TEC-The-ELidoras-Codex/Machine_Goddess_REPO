"""
Daily News Automation Script for The Elidoras Codex.
Fetches news articles, generates SEO-optimized content with geo-targeting, and posts to WordPress.
Run this script with a scheduler for daily news updates.

Usage:
    python -m scripts.daily_news_automation [--geo COUNTRY_CODE] [--category CATEGORY_NAME]
    
    Optional arguments:
        --geo: Specify a 2-letter country code to target news for that region (default: US)
        --category: Specify a specific news category to focus on (default: auto-select)
"""
import os
import sys
import argparse
import logging
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import required modules
from agents.airth_agent import AirthAgent
from dotenv import load_dotenv

# Configure logging
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, f"news_automation_{datetime.now().strftime('%Y%m%d')}.log"), 'a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsAutomation")

# Load environment variables
load_dotenv(os.path.join(project_root, 'config', '.env'))

# Maximum number of retries for API calls
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = 5

# Prioritized news categories (from highest to lowest priority)
PRIORITIZED_CATEGORIES = [
    {
        "name": "tech",
        "keywords": ["artificial intelligence", "AI", "machine learning", "digital consciousness", 
                    "tech ethics", "tech innovation", "future technology", "robotics"],
        "weight": 10  # Higher weight = higher priority
    },
    {
        "name": "science",
        "keywords": ["quantum computing", "neuroscience", "biotechnology", "space exploration", 
                    "research breakthrough", "scientific discovery"],
        "weight": 9
    },
    {
        "name": "digital_rights",
        "keywords": ["digital rights", "internet freedom", "privacy", "data protection", 
                    "surveillance", "cybersecurity", "hacking", "encryption"],
        "weight": 8
    },
    {
        "name": "crypto",
        "keywords": ["cryptocurrency", "blockchain", "bitcoin", "ethereum", "web3", 
                    "decentralized", "DeFi", "NFT", "tokenization"],
        "weight": 7
    },
    {
        "name": "sustainability",
        "keywords": ["climate tech", "sustainable technology", "clean energy", "carbon capture", 
                    "green tech", "environmental technology"],
        "weight": 6
    },
    {
        "name": "business",
        "keywords": ["tech startup", "innovation funding", "technology investment", 
                    "tech industry", "digital transformation"],
        "weight": 5
    },
    {
        "name": "culture",
        "keywords": ["digital culture", "internet culture", "tech ethics", "technology impact", 
                    "digital art", "AI art", "virtual reality culture"],
        "weight": 4
    },
    {
        "name": "policy",
        "keywords": ["tech policy", "AI regulation", "technology legislation", 
                    "digital governance", "data laws"],
        "weight": 3
    },
    {
        "name": "gaming",
        "keywords": ["game development", "gaming technology", "esports", 
                    "virtual reality gaming", "game design", "game AI"],
        "weight": 2
    },
    {
        "name": "sports",
        "keywords": ["sports technology", "esports", "athletic innovation", 
                    "sports analytics", "sports science"],
        "weight": 1  # Lowest priority - only if nothing else is found
    }
]

def get_geo_specific_keywords(country_code):
    """
    Returns country-specific keywords to enhance geo-targeting.
    
    Args:
        country_code: Two-letter country code
        
    Returns:
        List of geo-specific keywords
    """
    geo_keywords = {
        "US": ["United States", "USA", "American", "U.S."],
        "UK": ["United Kingdom", "Britain", "British", "UK"],
        "CA": ["Canada", "Canadian"],
        "AU": ["Australia", "Australian"],
        "IN": ["India", "Indian"],
        "JP": ["Japan", "Japanese"],
        "DE": ["Germany", "German"],
        "FR": ["France", "French"],
        "NZ": ["New Zealand", "Kiwi"],
        "IT": ["Italy", "Italian"],
        "ES": ["Spain", "Spanish"],
        "BR": ["Brazil", "Brazilian"]
    }
    
    return geo_keywords.get(country_code.upper(), [country_code])

def get_trending_tech_topics():
    """
    Returns current trending technology topics for better SEO.
    In a production environment, this would pull from a trending API.
    
    Returns:
        List of trending topics
    """
    # In a real implementation, pull these from Google Trends API or similar
    # For now, using a static list of evergreen tech topics
    return [
        "artificial intelligence",
        "machine learning",
        "blockchain technology",
        "cybersecurity",
        "digital transformation",
        "metaverse",
        "augmented reality",
        "cryptocurrency",
        "sustainable tech",
        "5G technology",
        "quantum computing",
        "edge computing",
        "IoT",
        "robotics",
        "digital twins",
        "extended reality",
        "neural networks"
    ]

def generate_seo_optimized_news_content(articles, geo_target=None):
    """
    Generate SEO-optimized news content from articles with geo-targeting.
    
    Args:
        articles: List of news articles
        geo_target: Optional country code for geo-targeting
    
    Returns:
        The most relevant article with SEO enhancements
    """
    if not articles:
        logger.warning("No articles found for SEO optimization")
        return None
    
    # First verify all articles have valid titles
    valid_articles = [article for article in articles if article.get("title") and article.get("description")]
    
    if not valid_articles:
        logger.warning("No articles with valid titles and descriptions found")
        return articles[0] if articles else None
        
    trending_topics = get_trending_tech_topics()
    
    # Score articles based on SEO potential and trending topics
    scored_articles = []
    for article in valid_articles:
        score = 0
        article_title = article.get("title", "").lower()
        article_description = article.get("description", "").lower()
        
        # Check for trending topics in title and description
        for topic in trending_topics:
            if topic.lower() in article_title:
                score += 5
            if topic.lower() in article_description:
                score += 3
        
        # Add geo-targeting score if specified
        if geo_target:
            geo_keywords = get_geo_specific_keywords(geo_target)
            for keyword in geo_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in article_title:
                    score += 4
                if keyword_lower in article_description:
                    score += 2
        
        # Check for SEO-friendly attributes
        if len(article_title) >= 30 and len(article_title) <= 60:
            score += 2  # Ideal title length for SEO
        
        if article.get("image_url"):
            score += 3  # Has featured image
        
        # Check if article has substantial content
        content_length = len(article.get("content", "") or article.get("description", ""))
        if content_length > 1500:
            score += 5  # Long-form content
        elif content_length > 800:
            score += 3  # Medium-length content
        elif content_length > 400:
            score += 1  # Short content
            
        scored_articles.append((score, article))
    
    # Sort by score, descending
    scored_articles.sort(reverse=True, key=lambda x: x[0])
    
    # Return the best article
    if scored_articles:
        best_score, best_article = scored_articles[0]
        logger.info(f"Selected article with SEO score {best_score}: {best_article.get('title')}")
        return best_article
    
    # Fallback to first article if scoring fails
    logger.warning("Article scoring failed, returning first valid article")
    return valid_articles[0] if valid_articles else (articles[0] if articles else None)

def fetch_articles_with_retry(airth, keywords, categories, country, max_results=10):
    """
    Fetch news articles with retry mechanism
    
    Args:
        airth: AirthAgent instance
        keywords: List of keywords to search for
        categories: List of categories to filter by
        country: Country code to filter news by
        max_results: Maximum number of results to return
        
    Returns:
        List of news articles
    """
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            articles = airth.fetch_news(
                keywords=keywords,
                categories=categories,
                country=country,
                max_results=max_results
            )
            
            if articles:
                return articles
                
            logger.warning(f"No articles found on attempt {attempts + 1}/{MAX_RETRIES}")
            attempts += 1
            time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Error fetching news on attempt {attempts + 1}/{MAX_RETRIES}: {e}")
            attempts += 1
            time.sleep(RETRY_DELAY)
    
    # If we get here, all attempts failed
    logger.error(f"Failed to fetch news articles after {MAX_RETRIES} attempts")
    return []

def get_category_keywords(category_name=None):
    """
    Get keywords for a specific category or for all categories if none specified
    
    Args:
        category_name: Name of the category to get keywords for
        
    Returns:
        List of keywords
    """
    if category_name:
        # Find the specified category
        for category in PRIORITIZED_CATEGORIES:
            if category["name"].lower() == category_name.lower():
                return category["keywords"]
        
        # If category not found, return tech keywords as fallback
        logger.warning(f"Category '{category_name}' not found, using tech category as fallback")
        return PRIORITIZED_CATEGORIES[0]["keywords"]
    else:
        # Collect keywords from all categories, giving more weight to higher priority categories
        all_keywords = []
        for category in PRIORITIZED_CATEGORIES:
            # Add keywords from higher-weight categories multiple times for better representation
            repetitions = max(1, int(category["weight"] / 3))
            all_keywords.extend(category["keywords"] * repetitions)
        
        return all_keywords

def run_daily_news_automation(geo_target=None, category=None):
    """
    Execute the daily news automation workflow.
    
    Args:
        geo_target: Optional country code for geo-targeting news
        category: Optional category to focus on
        
    Returns:
        Result of the automation workflow
    """
    logger.info(f"Starting daily news automation{' with geo-targeting: ' + geo_target if geo_target else ''}" +
                f"{' for category: ' + category if category else ''}")
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    try:
        # Initialize the Airth agent
        config_path = os.path.join(project_root, "config", "config.yaml")
        airth = AirthAgent(config_path)
        
        # Get keywords based on category
        base_keywords = get_category_keywords(category)
        
        # Add geo-specific keywords if provided
        if geo_target:
            geo_keywords = get_geo_specific_keywords(geo_target)
            search_keywords = base_keywords + geo_keywords
        else:
            search_keywords = base_keywords
        
        # Fetch news articles with retry mechanism
        logger.info(f"Fetching news with keywords: {search_keywords[:5]}... (and {len(search_keywords) - 5} more)")
        articles = fetch_articles_with_retry(
            airth=airth,
            keywords=search_keywords,
            categories=["technology", "science"] if not category else None,
            country=geo_target,
            max_results=15  # Fetch more articles to allow for better SEO selection
        )
        
        if not articles:
            logger.warning("No news articles found, trying fallback categories")
            
            # Try each category in priority order until we find articles
            for fallback_category in PRIORITIZED_CATEGORIES:
                if fallback_category["name"] == category:
                    continue  # Skip the original category that failed
                
                logger.info(f"Trying fallback category: {fallback_category['name']}")
                fallback_keywords = fallback_category["keywords"]
                
                fallback_articles = fetch_articles_with_retry(
                    airth=airth,
                    keywords=fallback_keywords,
                    categories=None,
                    country=geo_target,
                    max_results=10
                )
                
                if fallback_articles:
                    logger.info(f"Found {len(fallback_articles)} articles using fallback category {fallback_category['name']}")
                    articles = fallback_articles
                    break
        
        if not articles:
            logger.error("Failed to find any news articles after trying all categories")
            return {
                "success": False,
                "error": "No relevant news articles found after trying all categories"
            }
        
        # Select the best article based on SEO potential
        article = generate_seo_optimized_news_content(articles, geo_target)
        
        # Generate and post content with retry mechanism
        logger.info(f"Generating news commentary for: {article.get('title')}")
        
        post_success = False
        post_result = None
        attempts = 0
        
        while not post_success and attempts < MAX_RETRIES:
            try:
                post_result = airth.create_news_commentary_post(
                    article=article,
                    ai_perspective=True
                )
                
                if post_result.get("success"):
                    post_success = True
                    logger.info(f"Successfully created news post: {post_result.get('post_url')}")
                else:
                    logger.warning(f"Failed to create post on attempt {attempts + 1}/{MAX_RETRIES}: {post_result.get('error')}")
                    attempts += 1
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                logger.error(f"Error creating post on attempt {attempts + 1}/{MAX_RETRIES}: {e}")
                attempts += 1
                time.sleep(RETRY_DELAY)
        
        if post_success:
            return {
                "success": True,
                "post_url": post_result.get("post_url"),
                "article_title": article.get("title"),
                "category": category or "auto-selected"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to create news post after {MAX_RETRIES} attempts"
            }
    except Exception as e:
        logger.error(f"Daily news automation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Daily news automation for The Elidoras Codex")
    parser.add_argument("--geo", type=str, help="Two-letter country code for geo-targeting (e.g., US, UK, CA)")
    parser.add_argument("--category", type=str, help="News category to focus on (e.g., tech, science, crypto)")
    
    args = parser.parse_args()
    
    # Run the automation
    result = run_daily_news_automation(args.geo, args.category)
    
    # Print the result
    if result.get("success"):
        print(f"✅ Daily news automation completed successfully!")
        print(f"📰 Article: {result.get('article_title')}")
        print(f"🌐 Post URL: {result.get('post_url')}")
        print(f"📂 Category: {result.get('category')}")
    else:
        print(f"❌ Daily news automation failed: {result.get('error')}")