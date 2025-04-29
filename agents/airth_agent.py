"""
Airth Agent - An AI assistant with a unique goth personality for The Elidoras Codex.
Handles content creation, personality responses, and automated posting.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import random
import openai
from datetime import datetime

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
        
        # Initialize API keys for AI services
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            self.logger.warning("OpenAI API key not found in environment variables.")
    
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
        Call the OpenAI API to generate text.
        
        Args:
            prompt: The prompt to send to the API
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text from the API
        """
        if not self.openai_api_key:
            self.logger.error("Cannot call OpenAI API: API key not set")
            return "Error: OpenAI API key not configured"
            
        try:
            response = openai.Completion.create(
                engine="gpt-4",  # Use the appropriate engine for your needs
                prompt=prompt,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.7,
            )
            
            return response.choices[0].text.strip()
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
            
            # 4. Post to WordPress using the WordPress agent
            post_result = self.wp_agent.create_post(
                title=title,
                content=content,
                excerpt=f"Airth's thoughts on {topic}",
                status="draft"  # Set to "draft" initially to allow for review
            )
            
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
            # Example workflow - in a real implementation, you would:
            # 1. Check for scheduled content to create
            # 2. Process input data or triggers
            # 3. Generate appropriate content
            # 4. Post to WordPress or other platforms
            
            # Example post creation
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