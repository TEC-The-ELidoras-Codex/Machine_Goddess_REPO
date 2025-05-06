"""
Cryptocurrency News Automation Script for The Elidoras Codex.
Fetches crypto market data, news articles, and generates insightful analysis for the blog.
Run this script with a scheduler for regular crypto updates.

Usage:
    python -m scripts.crypto_news_automation [--coins "BTC,ETH,SOL"]
    
    Optional arguments:
        --coins: Specify a comma-separated list of coin symbols to focus on
"""
import os
import sys
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path
import requests

# Add parent directory to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import required modules
from agents.airth_agent import AirthAgent
from agents.tecbot import TECBot
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_root, "logs", f"crypto_automation_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CryptoAutomation")

# Load environment variables
load_dotenv(os.path.join(project_root, 'config', '.env'))

def get_crypto_market_data(coins=None):
    """
    Fetch cryptocurrency market data from CoinGecko API.
    
    Args:
        coins: Optional list of coin symbols to fetch data for
        
    Returns:
        Dictionary of crypto market data
    """
    if not coins:
        coins = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]
    else:
        # Convert symbols to IDs (simplified mapping)
        symbol_to_id = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "ADA": "cardano",
            "DOT": "polkadot",
            "XRP": "ripple",
            "AVAX": "avalanche-2",
            "MATIC": "matic-network",
            "LINK": "chainlink"
        }
        coins = [symbol_to_id.get(coin.upper(), coin.lower()) for coin in coins]
    
    try:
        # Fetch market data from CoinGecko
        coin_ids = ",".join(coins)
        url = f"https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": coin_ids,
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h,7d,30d"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        market_data = response.json()
        
        logger.info(f"Fetched market data for {len(market_data)} cryptocurrencies")
        return market_data
    except Exception as e:
        logger.error(f"Failed to fetch crypto market data: {e}")
        return []

def get_crypto_news():
    """
    Fetch cryptocurrency news articles from NewsData.io API.
    
    Returns:
        List of crypto news articles
    """
    try:
        # Initialize the Airth agent
        config_path = os.path.join(project_root, "config", "config.yaml")
        airth = AirthAgent(config_path)
        
        # Use the existing fetch_news method with crypto keywords
        news_keywords = [
            "cryptocurrency", 
            "crypto market", 
            "bitcoin", 
            "ethereum", 
            "blockchain",
            "web3",
            "crypto regulation",
            "NFTs",
            "DeFi"
        ]
        
        articles = airth.fetch_news(
            keywords=news_keywords,
            categories=["business", "technology"],
            max_results=5
        )
        
        logger.info(f"Fetched {len(articles)} crypto news articles")
        return articles
    except Exception as e:
        logger.error(f"Failed to fetch crypto news: {e}")
        return []

def format_market_analysis(market_data):
    """
    Format cryptocurrency market data into a human-readable analysis.
    
    Args:
        market_data: List of cryptocurrency market data
        
    Returns:
        HTML-formatted market analysis
    """
    if not market_data:
        return "<p>No market data available at this time.</p>"
    
    # Start building the HTML output
    output = "<h2>Current Cryptocurrency Market Overview</h2>\n"
    output += "<div class='crypto-market-overview'>\n"
    
    # Add market summary table
    output += "<table class='crypto-table'>\n"
    output += "<thead>\n<tr>\n<th>Coin</th>\n<th>Price (USD)</th>\n<th>24h Change</th>\n<th>7d Change</th>\n<th>Market Cap</th>\n</tr>\n</thead>\n"
    output += "<tbody>\n"
    
    for coin in market_data:
        name = coin.get("name", "Unknown")
        symbol = coin.get("symbol", "").upper()
        price = coin.get("current_price", 0)
        change_24h = coin.get("price_change_percentage_24h", 0)
        change_7d = coin.get("price_change_percentage_7d_in_currency", 0)
        market_cap = coin.get("market_cap", 0)
        
        # Format the price with appropriate decimal places
        if price < 1:
            price_formatted = f"${price:.6f}"
        elif price < 10:
            price_formatted = f"${price:.4f}"
        else:
            price_formatted = f"${price:.2f}"
        
        # Format the market cap with commas
        market_cap_formatted = f"${market_cap:,}"
        
        # Format the change percentages with color
        change_24h_class = "positive" if change_24h >= 0 else "negative"
        change_7d_class = "positive" if change_7d >= 0 else "negative"
        
        change_24h_formatted = f"<span class='{change_24h_class}'>{change_24h:.2f}%</span>"
        change_7d_formatted = f"<span class='{change_7d_class}'>{change_7d:.2f}%</span>"
        
        # Add the row to the table
        output += f"<tr>\n<td><strong>{name} ({symbol})</strong></td>\n<td>{price_formatted}</td>\n<td>{change_24h_formatted}</td>\n<td>{change_7d_formatted}</td>\n<td>{market_cap_formatted}</td>\n</tr>\n"
    
    output += "</tbody>\n</table>\n"
    
    # Add market sentiment analysis
    positive_coins = sum(1 for coin in market_data if coin.get("price_change_percentage_24h", 0) > 0)
    total_coins = len(market_data)
    sentiment_ratio = positive_coins / total_coins if total_coins > 0 else 0
    
    if sentiment_ratio > 0.7:
        sentiment = "bullish"
    elif sentiment_ratio > 0.5:
        sentiment = "cautiously optimistic"
    elif sentiment_ratio > 0.3:
        sentiment = "mixed"
    else:
        sentiment = "bearish"
    
    output += f"<p>Market sentiment: <strong>{sentiment}</strong> with {positive_coins} out of {total_coins} analyzed coins showing positive 24-hour movement.</p>\n"
    output += "</div>\n"
    
    return output

def run_crypto_news_automation(focus_coins=None):
    """
    Execute the crypto news automation workflow.
    
    Args:
        focus_coins: Optional list of coin symbols to focus on
        
    Returns:
        Result of the automation workflow
    """
    logger.info(f"Starting crypto news automation")
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    try:
        # Fetch crypto market data
        market_data = get_crypto_market_data(focus_coins)
        
        # Fetch crypto news
        news_articles = get_crypto_news()
        
        if not news_articles:
            logger.warning("No crypto news articles found")
            news_content = "<p>No crypto news available at this time.</p>"
            selected_article = None
        else:
            # Select the most relevant article
            selected_article = news_articles[0]
        
        # Format market data analysis
        market_analysis = format_market_analysis(market_data)
        
        # Initialize the Airth agent for posting
        config_path = os.path.join(project_root, "config", "config.yaml")
        airth = AirthAgent(config_path)
        
        # Generate title
        today = datetime.now().strftime("%B %d, %Y")
        title = f"Crypto Market Pulse: {today} - "
        
        # Add market sentiment to title
        positive_coins = sum(1 for coin in market_data if coin.get("price_change_percentage_24h", 0) > 0)
        total_coins = len(market_data)
        sentiment_ratio = positive_coins / total_coins if total_coins > 0 else 0
        
        if sentiment_ratio > 0.7:
            title += "Bulls Take Control"
        elif sentiment_ratio > 0.5:
            title += "Cautious Optimism"
        elif sentiment_ratio > 0.3:
            title += "Markets at a Crossroads"
        else:
            title += "Bears Dominate"
        
        # Generate content
        if selected_article:
            # Use the news article for additional content
            news_content = airth.call_openai_api(f"""
            Analyze this cryptocurrency news article and provide insights as Airth:
            
            ARTICLE TITLE: {selected_article.get('title', '')}
            ARTICLE CONTENT: {selected_article.get('description', '')}
            
            Write a detailed analysis focusing on the implications for crypto investors, 
            developers, and the broader technology ecosystem. Include your unique "TEC" 
            perspective as specified in your persona.
            
            Format your response with HTML paragraph tags.
            """, max_tokens=1000)
            
            # Add attribution to the news source
            news_attribution = f"""<p><strong>Source:</strong> <a href="{selected_article.get('url')}" target="_blank">{selected_article.get('title')}</a> from {selected_article.get('source_name')}</p>"""
            news_content += news_attribution
        
        # Combine market analysis and news content
        content = f"""
        <div class="crypto-update">
            {market_analysis}
            
            <h2>Latest Crypto News Analysis</h2>
            {news_content}
            
            <div class="tec-signature">
                <p><em>This analysis is brought to you by Airth, TEC's AI assistant with a unique perspective on the digital realm.</em></p>
            </div>
        </div>
        
        <style>
        .crypto-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .crypto-table th, .crypto-table td {{
            padding: 8px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .crypto-table th {{
            background-color: #f2f2f2;
        }}
        .positive {{
            color: green;
        }}
        .negative {{
            color: red;
        }}
        .crypto-market-overview {{
            margin-bottom: 30px;
        }}
        .tec-signature {{
            margin-top: 30px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
            font-style: italic;
        }}
        </style>
        """
        
        # Post to WordPress
        keywords = ["cryptocurrency", "market analysis", "blockchain", "crypto news"]
        if focus_coins:
            keywords.extend(focus_coins)
        
        post_result = airth.wp_agent.create_airth_post(
            title=title,
            content=content,
            keywords=keywords,
            excerpt=f"Airth's cryptocurrency market analysis and news update for {today}.",
            status="draft"
        )
        
        if post_result.get("success"):
            logger.info(f"Successfully created crypto update post: {post_result.get('post_url')}")
            return {
                "success": True,
                "post_url": post_result.get("post_url"),
                "title": title
            }
        else:
            logger.error(f"Failed to create crypto update post: {post_result.get('error')}")
            return {
                "success": False,
                "error": post_result.get("error")
            }
    except Exception as e:
        logger.error(f"Crypto news automation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Crypto news automation for The Elidoras Codex")
    parser.add_argument("--coins", type=str, help="Comma-separated list of coin symbols to focus on (e.g., BTC,ETH,SOL)")
    
    args = parser.parse_args()
    
    # Parse focus coins if provided
    focus_coins = args.coins.split(",") if args.coins else None
    
    # Run the automation
    result = run_crypto_news_automation(focus_coins)
    
    # Print the result
    if result.get("success"):
        print(f"✅ Crypto news automation completed successfully!")
        print(f"📰 Title: {result.get('title')}")
        print(f"🌐 Post URL: {result.get('post_url')}")
    else:
        print(f"❌ Crypto news automation failed: {result.get('error')}")