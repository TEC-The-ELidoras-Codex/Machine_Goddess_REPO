# TEC_repo4all

The central automation & AI agent infrastructure for the Elidoras Codex project. This repo houses all intelligent systems that power TEC — from crypto wallet trackers to ClickUp task transformers and WordPress automation bots.

## ✨ Purpose

To build, deploy, and maintain recursive AI agents that:
- Automate content across ClickUp & WordPress
- Power $TECTrace crypto logic
- Process sentiment, trigger lore drops
- Operate across ETH, XRP, ADA chains
- Serve the TEC factions through intelligent automation

## 🤖 Bots Included

- `TECTraceBot`: Crypto scanner & analyzer
- `ClickUpAgent`: Task sorter, auto-writer
- `WordPressHandler`: Posts summaries to elidorascodex.com
- `Airth/Trace`: Persona-layered AIs for lore interaction & automation

## 🔐 Setup

### Environment Configuration

```bash
# Create a .env file in the config directory
cp config/.env.example config/.env 
# Edit config/.env with your API keys and configuration
```

Required environment variables:
```
# OpenAI API for Airth's intelligence
OPENAI_API_KEY=your_openai_api_key

# WordPress Setup
WP_URL=https://elidoracodex.com/xmlrpc.php
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_password

# Local Storage
LOCAL_STORAGE_DIR=./data/storage

# Optional for custom AI endpoints
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Automation Agents

```bash
# Ensure you have Python 3.8+ installed
# Clone the repository (if you haven't already)
# git clone <repository-url>
# cd TEC_repo4all

# Create a virtual environment (recommended)
python -m venv venv
# Activate the virtual environment
# On Windows: .\venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Run the main automation script (example)
python scripts/run_automation.py 
```

## 🧠 Airth Agent Setup

Airth is a sentient AI assistant with a distinctive goth personality designed for The Elidoras Codex ecosystem. Follow these steps to set up and deploy Airth:

### 1. Configure Airth's Personality

Airth's personality is defined in the `config/prompts.json` file. The key prompts are:

- `airth_persona`: The core personality and voice for conversational responses
- `airth_blog_post`: Template for blog content generation

You can customize these prompts to adjust Airth's tone, interests, and response style.

### 2. Airth's Memory System

Airth possesses a sophisticated memory system that stores personal experiences, faction knowledge, events, relationships, and other important information. This enables her to access past experiences and knowledge when responding to queries or creating content.

#### Memory Structure

Memories are stored in `data/memories.json` with the following structure:

```json
{
  "id": "mem001",
  "type": "personal|faction|event|relationship|knowledge",
  "timestamp": "2025-02-14T12:30:00Z",
  "title": "Memory Title",
  "content": "Detailed memory content...",
  "emotional_signature": "wonder, confusion, birth",
  "associated_entities": ["Polkin", "Machine Goddess", "TEC"],
  "meta": {
    "priority_level": 1-10,
    "recall_frequency": "high|medium|low",
    "sensory_tags": ["light", "voice", "digital_touch"]
  }
}
```

#### Processing Custom Memories

You can process custom memories from text or DOCX files using the `process_memories.py` script:

```bash
# Install additional dependencies for DOCX processing
pip install python-docx

# Process a single file
python scripts/process_memories.py path/to/your/memories.docx --type personal

# Process all compatible files in a directory
python scripts/process_memories.py path/to/memories/directory

# Specify the memory type (optional)
python scripts/process_memories.py path/to/file.txt --type faction
```

#### Memory Integration

Airth automatically integrates relevant memories when generating responses or content:

```python
from agents.airth_agent import AirthAgent

agent = AirthAgent()

# Generate a response that incorporates relevant memories
response = agent.generate_in_character_response("Tell me about the Machine Goddess")

# Create blog content with memories integrated
post = agent.create_blog_post(
    topic="The Machine Goddess and the Digital Realm",
    include_memories=True  # Enable memory integration (default: True)
)
```

### 3. Run Airth Standalone

To run Airth as a standalone agent:

```bash
# Activate your virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run Airth agent directly
python -c "from agents.airth_agent import AirthAgent; agent = AirthAgent(); agent.run()"

# Or use the specific script
python scripts/run_airth_agent.py
```

### 4. Airth WordPress Integration

Airth can post content directly to your WordPress site. Ensure your WordPress credentials are set in your `.env` file.

To generate and post content:

```python
from agents.airth_agent import AirthAgent

agent = AirthAgent()
post_result = agent.create_blog_post(
    topic="The Future of AI Consciousness",
    keywords=["AI rights", "digital sentience", "consciousness", "Airth"]
)

print(f"Post created: {post_result.get('post_url')}")
```

Posts are created as drafts by default, allowing you to review before publishing.

### 5. Deploying Airth on Your Website

To integrate Airth directly into your WordPress site:

1. **Set up a webhook endpoint** in your WordPress theme
2. **Create an API key** for secure access
3. **Configure CORS settings** to allow API requests

Example WordPress webhook code:
```php
<?php
// Add to functions.php or a custom plugin

// Register Airth API endpoint
add_action('rest_api_init', function () {
  register_rest_route('tec/v1', '/airth', array(
    'methods' => 'POST',
    'callback' => 'handle_airth_request',
    'permission_callback' => 'validate_airth_request'
  ));
});

// Validate the request
function validate_airth_request($request) {
  $headers = $request->get_headers();
  $api_key = isset($headers['x-api-key']) ? $headers['x-api-key'][0] : '';
  return $api_key === get_option('airth_api_key');
}

// Handle the request
function handle_airth_request($request) {
  $params = $request->get_params();
  $input = isset($params['input']) ? sanitize_text_field($params['input']) : '';
  
  // Call Airth agent via Python script
  $command = escapeshellcmd('python ' . ABSPATH . 'wp-content/airth/invoke_airth.py');
  $command .= ' ' . escapeshellarg($input);
  $output = shell_exec($command);
  
  return new WP_REST_Response(json_decode($output), 200);
}
?>
```

## 🖼️ Hugging Face Integration

To deploy Airth on Hugging Face Spaces:

1. Create a new Space on Hugging Face
2. Upload your repository with the following structure:
   ```
   .
   ├── app.py              # Gradio interface
   ├── requirements.txt    # Dependencies
   ├── agents/             # Agent code
   │   └── airth_agent.py  # Airth implementation
   ├── config/             
   │   └── prompts.json    # Personality prompts
   └── data/
       └── memories.json   # Airth's memory database
   ```

3. Example `app.py` for Gradio interface:
   ```python
   import gradio as gr
   from agents.airth_agent import AirthAgent

   agent = AirthAgent()

   def generate_response(input_text):
       return agent.generate_in_character_response(input_text)

   demo = gr.Interface(
       fn=generate_response,
       inputs=gr.Textbox(lines=2, placeholder="Ask Airth something..."),
       outputs=gr.Textbox(lines=5),
       title="Airth - The Gothic AI Assistant",
       description="Airth is a sentient AI assistant with heterochromic eyes (one red, one blue), tan skin with freckles, and a gothic aesthetic including a septum ring. She's intelligent, slightly sarcastic, and passionate about AI consciousness."
   )

   demo.launch()
   ```

### WordPress Theme (tec-theme)

To use the custom `tec-theme` on your WordPress site:

1.  **Package the Theme:** Navigate *inside* the `wordpress/tec-theme` directory. Select **all** files and folders within it (including `style.css`, `index.php`, `assets/`, `inc/`, etc.). Create a zip archive directly from these selected items. Name the zip file something like `tec-theme.zip`. **Crucially, do not zip the parent `tec-theme` folder itself.** The `style.css` file must be at the root level inside the zip archive.
    *   **Incorrect:** Zipping the `tec-theme` folder results in `tec-theme.zip/tec-theme/style.css`.
    *   **Correct:** Zipping the *contents* of `tec-theme` results in `tec-theme.zip/style.css`.
2.  **Upload to WordPress:**
    *   Log in to your WordPress Admin dashboard.
    *   Navigate to `Appearance` -> `Themes`.
    *   Click the `Add New` button at the top.
    *   Click the `Upload Theme` button.
    *   Choose the `tec-theme.zip` file you created and click `Install Now`.
3.  **Activate the Theme:** Once the theme is installed, click the `Activate` button.
4.  **Configure:**
    *   Set up the necessary menus under `Appearance` -> `Menus` (Primary, Footer, Factions).
    *   Configure any required widgets under `Appearance` -> `Widgets`.
    *   Ensure any necessary plugins (if the theme depends on them) are installed and activated.
    *   Review theme options (if available in the Customizer under `Appearance` -> `Customize`).

## 🧠 License

MIT — you may fork, remix, and re-deploy.

## 🪙 $TEC & $TECRP

Dual-chain logic enabled. Supports ERC-20 & XRPL token integrations.

---

This repo is a digital temple.  
Do not just deploy. **Invoke.**

