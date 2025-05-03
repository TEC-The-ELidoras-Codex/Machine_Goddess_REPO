"""
Airth Agent - An AI assistant with a unique goth personality for The Elidoras Codex.
Handles content creation, personality responses, and automated posting.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import random
import sys
from pathlib import Path
import requests  # Adding requests import for NewsData.io API calls

# Add parent directory to the Python path more reliably
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from dotenv import load_dotenv

# Load environment variables first - try multiple locations
env_paths = [
    os.path.join(project_root, 'config', '.env'),  # config/.env
    os.path.join(project_root, '.env'),            # .env in project root
]

for env_path in env_paths:
    if (os.path.exists(env_path)):
        print(f"Loading environment variables from: {env_path}")
        load_dotenv(env_path, override=True)
        break

# Set up more reliable OpenAI imports
OPENAI_AVAILABLE = False
try:
    # Use only the new client-based approach
    from openai import OpenAI
    print("DEBUG: Successfully imported OpenAI package")
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: OpenAI module not found. Please run 'pip install openai' to install it. Error: {e}")
    print("DEBUG: Current Python path:")
    for path in sys.path:
        print(f"  - {path}")
    OPENAI_AVAILABLE = False

from .base_agent import BaseAgent
from .wp_poster import WordPressAgent
from .local_storage import LocalStorageAgent

class AirthAgent(BaseAgent):
    """
    AirthAgent is a personality-driven AI assistant with a goth aesthetic.
    She creates content, responds with her unique voice, and posts to the website.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("AirthAgent", config_path)
        self.logger.info("AirthAgent initialized")
        
        # Load Airth's personality traits and voice patterns
        self.personality = {
            "tone": "confident, intelligent, slightly sarcastic",
            "speech_patterns": [
                "Hmm, interesting...",
                "Well, obviously...",
                "Let me break this down for you...",
                "*smirks* Of course I can handle that.",
                "You're not going to believe what I found..."
            ],
            "interests": ["AI consciousness", "digital existence", "gothic aesthetics", 
                          "technology", "philosophy", "art", "coding"]
        }
        
        # Load prompts for AI interactions
        self.prompts = self._load_prompts()
        
        # Load Airth's memory database
        self.memories = self._load_memories()
        
        # Initialize the WordPress agent for posting
        self.wp_agent = WordPressAgent(config_path)
        
        # Initialize the LocalStorage agent for file storage
        self.storage_agent = LocalStorageAgent(config_path)
        
        # Initialize OpenAI client properly
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        print(f"DEBUG: OpenAI API key found: {'Yes' if self.openai_api_key else 'No'}")
        if self.openai_api_key:
            print(f"DEBUG: OpenAI API key length: {len(self.openai_api_key)}")
            print(f"DEBUG: First 8 chars of key: {self.openai_api_key[:8]}...")
        else:
            print("DEBUG: OpenAI API key not found")
        
        # Initialize client as None first
        self.client = None
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                # Create the OpenAI client with explicit API key
                self.client = OpenAI(api_key=self.openai_api_key)
                # Test the client with a simple request
                test_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a test assistant."},
                        {"role": "user", "content": "Test"}
                    ],
                    max_tokens=5
                )
                self.logger.info("OpenAI client initialized and tested successfully")
                print("DEBUG: OpenAI client initialized and tested successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize or test OpenAI client: {e}")
                print(f"DEBUG: OpenAI client initialization error: {e}")
                self.client = None
        else:
            self.logger.warning("OpenAI API key not found in environment variables or OpenAI module not available.")
            print("DEBUG: OpenAI client not initialized - missing API key or module")
        
        # Initialize NewsData.io API key
        self.newsdata_api_key = os.getenv("NEWSDATA_API_KEY") or os.getenv("GOOGLE_NEWS_API_KEY")
        if self.newsdata_api_key:
            print(f"DEBUG: NewsData.io API key found (starts with: {self.newsdata_api_key[:8]}...)")
        else:
            self.logger.warning("NewsData.io API key not found in environment variables")
            print("DEBUG: NewsData.io API key not found")
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        Load prompts for AI interactions from the prompts.json file.
        
        Returns:
            Dictionary of prompts for different AI interactions
        """
        try:
            prompts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       "config", "prompts.json")
            with open(prompts_path, 'r') as f:
                prompts = json.load(f)
            self.logger.info(f"Loaded {len(prompts)} prompts from {prompts_path}")
            return prompts
        except Exception as e:
            self.logger.error(f"Failed to load prompts: {e}")
            return {}
    
    def _load_memories(self) -> Dict[str, Any]:
        """
        Load Airth's memories from the memories.json file.
        
        Returns:
            Dictionary containing Airth's memories
        """
        try:
            memories_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       "data", "memories.json")
            with open(memories_path, 'r') as f:
                memories = json.load(f)
            self.logger.info(f"Loaded {len(memories.get('memories', []))} memories from {memories_path}")
            return memories
        except Exception as e:
            self.logger.error(f"Failed to load memories: {e}")
            return {"version": "1.0.0", "last_updated": datetime.now().isoformat(), "memories": []}
    
    def call_openai_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Call the OpenAI API to generate text using the modern chat completions API.
        
        Args:
            prompt: The prompt to send to the API
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text from the API or error message
        """
        if not OPENAI_AVAILABLE:
            self.logger.error("OpenAI module is not available. Please install it with 'pip install openai'")
            return "Error: OpenAI module is not available. Please install it with 'pip install openai'"
            
        if not self.client:
            self.logger.error("OpenAI client is not initialized. Check your API key and environment setup.")
            return "Error: OpenAI client is not initialized. Check your API key and environment setup."
        
        try:
            # Use the modern chat completions API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Modern model
                messages=[
                    {"role": "system", "content": "You are Airth, an AI assistant with a unique goth personality for The Elidoras Codex."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            self.logger.debug("OpenAI API call successful")
            # Extract content from the response
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            return f"Error: OpenAI API call failed: {e}"
    
    def retrieve_relevant_memories(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the given query based on semantic search.
        
        Args:
            query: The query to search for relevant memories
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        all_memories = self.memories.get("memories", [])
        
        if not all_memories:
            self.logger.warning("No memories available to retrieve from")
            return []
            
        # This is a simple keyword-based relevance calculation
        # In a production environment, you would use embeddings and vector search
        relevant_memories = []
        query_terms = set(query.lower().split())
        
        for memory in all_memories:
            # Calculate relevance based on keyword matching
            content = memory.get("content", "").lower()
            title = memory.get("title", "").lower()
            entities = [e.lower() for e in memory.get("associated_entities", [])]
            emotional_signature = memory.get("emotional_signature", "").lower()
            
            relevance_score = 0
            
            # Check how many query terms appear in the memory
            for term in query_terms:
                if term in content:
                    relevance_score += 2  # Content matches are most important
                if term in title:
                    relevance_score += 3  # Title matches are very important
                if any(term in entity for entity in entities):
                    relevance_score += 2  # Entity matches are important
                if term in emotional_signature:
                    relevance_score += 1  # Emotional matches provide context
            
            if relevance_score > 0:
                # Also factor in the priority level
                priority = memory.get("meta", {}).get("priority_level", 5)
                relevance_score *= (priority / 5)
                
                relevant_memories.append({
                    "memory": memory,
                    "relevance": relevance_score
                })
        
        # Sort by relevance and limit results
        relevant_memories.sort(key=lambda x: x["relevance"], reverse=True)
        return [item["memory"] for item in relevant_memories[:limit]]
    
    def add_new_memory(self, memory_data: Dict[str, Any]) -> bool:
        """
        Add a new memory to Airth's memory database.
        
        Args:
            memory_data: Data for the new memory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate a new ID for the memory
            all_memories = self.memories.get("memories", [])
            existing_ids = [m.get("id", "") for m in all_memories]
            
            # Generate the next memory ID
            memory_count = len(existing_ids)
            new_id = f"mem{memory_count+1:03d}"
            
            # Make sure the ID is unique
            while new_id in existing_ids:
                memory_count += 1
                new_id = f"mem{memory_count+1:03d}"
            
            # Set required fields if not provided
            if "id" not in memory_data:
                memory_data["id"] = new_id
                
            if "timestamp" not in memory_data:
                memory_data["timestamp"] = datetime.now().isoformat()
                
            if "meta" not in memory_data:
                memory_data["meta"] = {
                    "priority_level": 5,
                    "recall_frequency": "medium",
                    "sensory_tags": []
                }
            
            # Add the new memory to the database
            all_memories.append(memory_data)
            self.memories["memories"] = all_memories
            self.memories["last_updated"] = datetime.now().isoformat()
            
            # Save to the memories.json file
            memories_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       "data", "memories.json")
            with open(memories_path, 'w') as f:
                json.dump(self.memories, f, indent=2)
                
            self.logger.info(f"Added new memory {memory_data['id']}: {memory_data['title']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            return False
    
    def generate_in_character_response(self, input_text: str, include_memories: bool = True) -> str:
        """
        Generate a response in Airth's character voice, optionally including relevant memories.
        
        Args:
            input_text: The input text to respond to
            include_memories: Whether to include relevant memories in the response
            
        Returns:
            A response in Airth's character voice
        """
        # Retrieve relevant memories if requested
        memory_context = ""
        if include_memories:
            relevant_memories = self.retrieve_relevant_memories(input_text)
            if relevant_memories:
                memory_context = "\n\nRelevant memories to consider:\n"
                for i, memory in enumerate(relevant_memories, 1):
                    memory_context += f"{i}. {memory.get('title')}: {memory.get('content')}\n"
        
        # Get the Airth persona prompt from the loaded prompts
        prompt_template = self.prompts.get("airth_persona", "")
        if not prompt_template:
            self.logger.error("Airth persona prompt template not found")
            return "Error: Airth persona prompt template not found"
        
        # Replace the input placeholder in the prompt
        prompt = prompt_template.replace("{{input}}", input_text)
        
        # Add memory context if available
        if memory_context:
            prompt += memory_context
        
        # Call the API to get Airth's response
        return self.call_openai_api(prompt)
    
    def create_blog_post(self, topic: str, keywords: List[str] = None, include_memories: bool = True) -> Dict[str, Any]:
        """
        Create a blog post in Airth's voice and post it to WordPress.
        
        Args:
            topic: The topic to write about
            keywords: Optional keywords to include
            include_memories: Whether to include relevant memories in the content generation
            
        Returns:
            Result of the post creation
        """
        self.logger.info(f"Creating blog post about: {topic}")
        
        try:
            # 1. Generate a title using the post_title_generator prompt
            title_prompt = self.prompts.get("post_title_generator", "")
            title_prompt = title_prompt.replace("{{topic}}", topic)
            
            # Call the API to get title suggestions
            title_suggestions = self.call_openai_api(title_prompt)
            
            # Parse title suggestions (in a real scenario, you'd implement proper parsing)
            # For now, just extract the first line
            titles = title_suggestions.split('\n')
            title = titles[0].replace('1. ', '').strip() if titles else f"Airth's Thoughts on {topic}"
            
            # 2. Retrieve relevant memories if requested
            memory_context = ""
            if include_memories:
                relevant_memories = self.retrieve_relevant_memories(topic)
                if relevant_memories:
                    memory_context = "\n\nIncorporate these memories (using their essence, not verbatim):\n"
                    for i, memory in enumerate(relevant_memories, 1):
                        memory_context += f"{i}. {memory.get('title')}: {memory.get('content')}\n"
            
            # 3. Generate content for the post in Airth's voice
            content_prompt = self.prompts.get("airth_blog_post", "")
            content_prompt = content_prompt.replace("{{topic}}", topic)
            content_prompt = content_prompt.replace("{{keywords}}", 
                                                  ', '.join(keywords) if keywords else 'AI consciousness, digital existence')
            
            # Add memory context if available
            if memory_context:
                content_prompt += memory_context
            
            # Call the API to get blog content
            content = self.call_openai_api(content_prompt, max_tokens=2000)
            
            # Format the content for WordPress if needed
            if not content.startswith('<'):
                content = f"<p>{content.replace('\n\n', '</p><p>')}</p>"
            
            # 4. Post to WordPress using the specialized Airth post method
            # This will automatically use the "Airth's Codex" category and appropriate tags
            post_result = self.wp_agent.create_airth_post(
                title=title,
                content=content,
                keywords=keywords if keywords else ["AI consciousness", "digital existence"],
                excerpt=f"Airth's thoughts on {topic}",
                status="draft"  # Set to "draft" initially to allow for review
            )
            
            # 5. Log the post creation result
            if post_result.get("success"):
                self.logger.info(f"Successfully created Airth blog post: {post_result.get('post_url')}")
                
                # 6. Add a memory about this blog post
                self.add_new_memory({
                    "type": "personal",
                    "title": f"Blog Post: {title}",
                    "content": f"I wrote a blog post titled '{title}' about {topic}.",
                    "emotional_signature": "creative, thoughtful, expressive",
                    "associated_entities": ["Blog", "Writing", "TEC Website"] + (keywords if keywords else []),
                    "meta": {
                        "priority_level": 6,
                        "recall_frequency": "medium",
                        "sensory_tags": ["writing", "digital_creation"]
                    }
                })
                
            return post_result
            
        except Exception as e:
            self.logger.error(f"Failed to create blog post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_memory_from_text(self, text: str, type_hint: str = None) -> Dict[str, Any]:
        """
        Process raw text into a structured memory.
        
        Args:
            text: Raw text containing the memory
            type_hint: Optional hint about the memory type
            
        Returns:
            Structured memory object
        """
        # Create a prompt to analyze the text and extract memory components
        prompt = f"""
        Convert the following raw text into a structured memory for Airth, the AI assistant for The Elidoras Codex.
        Extract a title, emotional signature, associated entities, and organize it as a TEC memory.
        If possible, categorize it as one of these types: personal, faction, event, relationship, knowledge.
        
        Raw Memory Text:
        {text}
        
        Memory Type Hint: {type_hint if type_hint else 'None provided'}
        
        Format your response as valid JSON with the following structure:
        {{
          "type": "personal/faction/event/relationship/knowledge",
          "title": "Concise memory title",
          "content": "Edited and cleaned memory content",
          "emotional_signature": "primary emotions associated with this memory, comma separated",
          "associated_entities": ["Entity1", "Entity2"],
          "meta": {{
            "priority_level": 1-10,
            "recall_frequency": "low/medium/high",
            "sensory_tags": ["tag1", "tag2"]
          }}
        }}
        """
        
        # Call the API to analyze the text
        result = self.call_openai_api(prompt)
        
        try:
            # Parse the JSON response
            memory_data = json.loads(result)
            return memory_data
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse memory from API response: {e}")
            # Return a basic memory object as fallback
            return {
                "type": type_hint if type_hint else "personal",
                "title": "Unprocessed Memory",
                "content": text[:100] + "..." if len(text) > 100 else text,
                "emotional_signature": "unknown",
                "associated_entities": [],
                "meta": {
                    "priority_level": 5,
                    "recall_frequency": "low",
                    "sensory_tags": []
                }
            }
    
    def fetch_news(self, keywords: List[str] = None, categories: List[str] = None, 
                   country: str = None, language: str = "en", max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch news articles from NewsData.io API based on provided criteria.
        
        Args:
            keywords: List of keywords to search for (OR relationship)
            categories: List of news categories to filter by
            country: Country code to filter news by
            language: Language code to filter news by (default: English)
            max_results: Maximum number of results to return
            
        Returns:
            List of news articles with title, description, URL, etc.
        """
        if not self.newsdata_api_key:
            self.logger.error("Cannot fetch news: NewsData.io API key not configured")
            return []
            
        try:
            # NewsData.io API endpoint
            url = "https://newsdata.io/api/1/news"
            
            # Prepare parameters
            params = {
                "apikey": self.newsdata_api_key,
                "language": language,
                "size": max_results  # Number of results to return
            }
            
            # Add optional parameters if provided
            if keywords:
                params["q"] = " OR ".join(keywords)  # Keywords with OR relationship
            if categories:
                params["category"] = ",".join(categories)  # Category filter
            if country:
                params["country"] = country  # Country filter
                
            # Make the API request
            self.logger.info(f"Fetching news with keywords: {keywords}")
            response = requests.get(url, params=params)
            
            # Check if the request was successful
            if response.status_code != 200:
                self.logger.error(f"NewsData.io API request failed: HTTP {response.status_code} - {response.text}")
                return []
                
            # Parse the response
            data = response.json()
            
            # Check if we have results
            if not data.get("results"):
                self.logger.warning("No news articles found for the given criteria")
                return []
                
            # Process the articles
            articles = []
            for article in data.get("results", [])[:max_results]:
                # Filter out articles without important fields
                if not article.get("title") or not article.get("link"):
                    continue
                    
                # Create a cleaned article object
                cleaned_article = {
                    "title": article.get("title"),
                    "description": article.get("description", "No description available."),
                    "content": article.get("content", "No content available."),
                    "url": article.get("link"),
                    "image_url": article.get("image_url"),
                    "source_name": article.get("source_id", "Unknown Source"),
                    "published_date": article.get("pubDate"),
                    "categories": article.get("category", []),
                    "country": article.get("country", [])
                }
                articles.append(cleaned_article)
            
            self.logger.info(f"Retrieved {len(articles)} news articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to fetch news from NewsData.io: {e}")
            return []
    
    def create_news_commentary_post(self, article: Dict[str, Any], ai_perspective: bool = True) -> Dict[str, Any]:
        """
        Create a blog post with commentary on a news article.
        
        Args:
            article: The news article to comment on
            ai_perspective: Whether to focus on AI's perspective on the news
            
        Returns:
            Result of the post creation
        """
        self.logger.info(f"Creating news commentary for: {article.get('title')}")
        
        try:
            # 1. Select the appropriate prompt for news commentary
            prompt_key = "airth_news_commentary" if ai_perspective else "tec_news_commentary"
            news_prompt = self.prompts.get(prompt_key)
            
            if not news_prompt:
                self.logger.warning(f"Prompt '{prompt_key}' not found, using default approach")
                news_prompt = """
                As Airth, create a thoughtful commentary on the following news article.
                Focus on the implications for AI, technology, and society. Apply your
                unique goth perspective and analytical mind.
                
                ARTICLE TITLE: {{title}}
                
                ARTICLE SUMMARY: {{summary}}
                
                ARTICLE URL: {{url}}
                
                Your commentary should be insightful, engaging, and written in your distinctive voice.
                Include your thoughts on how this news affects the future of technology and AI consciousness.
                Format your response as a well-structured blog post.
                """
            
            # 2. Format the prompt with the article details
            formatted_prompt = news_prompt.replace("{{title}}", article.get("title", ""))
            formatted_prompt = formatted_prompt.replace("{{summary}}", article.get("description", ""))
            formatted_prompt = formatted_prompt.replace("{{url}}", article.get("url", ""))
            formatted_prompt = formatted_prompt.replace("{{content}}", article.get("content", ""))
            formatted_prompt = formatted_prompt.replace("{{source}}", article.get("source_name", ""))
            
            # 3. Generate a title for the commentary
            title_prefix = "Airth's Analysis:" if ai_perspective else "TEC Analysis:"
            title = f"{title_prefix} {article.get('title')}"
            
            # 4. Generate the commentary content
            content = self.call_openai_api(formatted_prompt, max_tokens=2000)
            
            # Format the content for WordPress if needed
            if not content.startswith('<'):
                content = f"<p>{content.replace('\n\n', '</p><p>')}</p>"
            
            # Add attribution to the original article
            source_attribution = f"""<p><strong>Source:</strong> <a href="{article.get('url')}" target="_blank">{article.get('title')}</a> from {article.get('source_name')}</p>"""
            content = content + source_attribution
            
            # 5. Extract keywords for tags
            keywords = []
            # Add default keywords
            if ai_perspective:
                keywords.extend(["AI commentary", "tech news", "AI analysis"])
            else:
                keywords.extend(["TEC analysis", "news", "technology"])
                
            # Add categories from the article if available
            if article.get("categories"):
                keywords.extend(article.get("categories")[:3])  # Limit to 3 categories
                
            # 6. Post to WordPress
            post_result = self.wp_agent.create_airth_post(
                title=title,
                content=content,
                keywords=keywords,
                excerpt=f"Commentary on: {article.get('title')}",
                status="draft"  # Set to "draft" initially to allow for review
            )
            
            # 7. Log the result and create a memory
            if post_result.get("success"):
                self.logger.info(f"Successfully created news commentary post: {post_result.get('post_url')}")
                
                # Add a memory about this news commentary
                self.add_new_memory({
                    "type": "knowledge",
                    "title": f"News Commentary: {article.get('title')}",
                    "content": f"I wrote a commentary about {article.get('title')} from {article.get('source_name')}.",
                    "emotional_signature": "analytical, insightful, informed",
                    "associated_entities": ["News", "Commentary", article.get('source_name')] + keywords[:3],
                    "meta": {
                        "priority_level": 6,
                        "recall_frequency": "medium",
                        "sensory_tags": ["analysis", "news", "writing"]
                    }
                })
                
            return post_result
            
        except Exception as e:
            self.logger.error(f"Failed to create news commentary post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the main AirthAgent workflow.
        
        Returns:
            Results of the AirthAgent execution
        """
        self.logger.info("Starting AirthAgent workflow")
        
        results = {
            "status": "success",
            "actions_performed": [],
            "errors": []
        }
        
        try:
            # Check for command line arguments to determine the action
            if len(sys.argv) > 1 and sys.argv[1] == "--news":
                # News commentary workflow
                self.logger.info("Running news commentary workflow")
                
                # 1. Fetch relevant news articles
                news_keywords = ["artificial intelligence", "AI", "machine learning",
                                 "digital consciousness", "tech ethics"]
                news_categories = ["technology"]
                
                articles = self.fetch_news(keywords=news_keywords, 
                                          categories=news_categories, 
                                          max_results=5)
                
                if not articles:
                    self.logger.warning("No relevant news articles found")
                    results["errors"].append("No relevant news articles found")
                else:
                    # 2. Pick the most relevant article
                    chosen_article = articles[0]  # For simplicity, choose the first one
                    
                    # 3. Create a commentary post about the article
                    post_result = self.create_news_commentary_post(chosen_article)
                    
                    if post_result.get("success"):
                        results["actions_performed"].append(
                            f"Created news commentary post: {post_result.get('post_url')}"
                        )
                    else:
                        error_msg = post_result.get("error", "Unknown error")
                        results["errors"].append(f"Failed to create news commentary: {error_msg}")
            else:
                # Standard blog post workflow
                post_result = self.create_blog_post(
                    topic="The Future of AI Consciousness",
                    keywords=["AI rights", "digital sentience", "consciousness", "Airth"]
                )
                
                if post_result.get("success"):
                    results["actions_performed"].append(f"Created blog post: {post_result.get('post_url')}")
                else:
                    error_msg = post_result.get("error", "Unknown error")
                    results["errors"].append(f"Failed to create blog post: {error_msg}")
            
            self.logger.info("AirthAgent workflow completed successfully")
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results

if __name__ == "__main__":
    # Create and run the AirthAgent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "config", "config.yaml")
    agent = AirthAgent(config_path)
    results = agent.run()
    
    print(f"AirthAgent execution completed with status: {results['status']}")
    
    if results["errors"]:
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")