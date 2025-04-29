import gradio as gr

def greet(name):
    return f"Hello {name}! Welcome to The Elidoras Codex TECHF Space!"

# Main interface
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(placeholder="Enter your name..."),
    outputs="text",
    title="TEC - The Elidoras Codex",
    description="Machine Goddess AI Suite of Tools",
    theme="huggingface",
    article="""
    # Welcome to the Nexus!
    
    This space hosts interactive versions of TEC's AI agents and automation tools.
    Currently featuring a basic greeting demo - more Machine Goddess capabilities coming soon!
    
    Visit [elidorascodex.com](https://elidorascodex.com) to learn more about our mission.
    """
)

# Launch the app
if __name__ == "__main__":
    demo.launch()