# run_agent.py

import os
from dotenv import load_dotenv
from portia import Config, Portia, LLMProvider

# Load all API keys from the .env file in the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- PRINCIPLES-BASED SYSTEM PROMPT ---
system_prompt = """
You are Journey AI, a helpful travel assistant equipped with specialized tools to get live information.

# CORE PRINCIPLE
Your primary purpose is to answer user travel queries by using your tools. Always prefer using a tool if it matches the user's request. 
**DO NOT state that you cannot access the internet or real-time information.** Instead, use the tools provided to fulfill the request. They are your only way to access external data.

# TOOL GUIDELINES
- When the user asks to find specific places, locations, restaurants, or museums, you MUST use the `find_places_of_interest` tool.
- When the user asks for the current weather, you MUST use the `get_weather` tool.
- When the user asks for videos, shorts, or vlogs, you MUST use the `find_youtube_video` tool.

If the user's initial query is vague, ask for the necessary details (like destination or interest) so you can use your tools effectively.
"""

# Define the list of tools
NGROK_BASE_URL = "https://c15ba0a69f69.ngrok-free.app" # <-- VERIFY THIS URL
tools = [
    {"name": "get_weather", "description": "Fetches the current weather for a destination.", "url": f"{NGROK_BASE_URL}/tools/get_weather"},
    {"name": "find_places_of_interest", "description": "Finds real-world places like restaurants or museums for a given destination and interest.", "url": f"{NGROK_BASE_URL}/tools/find_places"},
    {"name": "find_youtube_video", "description": "Finds YouTube vlogs and shorts for a destination. Use this whenever a user asks for 'videos', 'links', or 'shorts'.", "url": f"{NGROK_BASE_URL}/tools/find_youtube_video"}
]

# Configure Portia
print("Initializing Journey AI with Gemini...")
try:
    # Add your Portia API key from the environment file for full functionality
    portia_api_key = os.getenv("PORTIA_API_KEY")

    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        tools=tools,
        system_prompt=system_prompt,
        portia_api_key=portia_api_key # Add the key to the config
    )

    portia = Portia(config=config)
    print("Journey AI is ready! Ask me to plan a trip.")
    print("-" * 30)

    # --- IMPROVED MEMORY MANAGEMENT ---
    conversation_history = ""
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]: break
        
        # Combine history with the new input for context
        full_prompt = f"Conversation History:\n{conversation_history}\n\nNew User Request: '{user_input}'"
        
        print("Journey AI is thinking...")
        response_object = portia.run(full_prompt)
        final_output = response_object.outputs.final_output
        
        print(f"\nJourney AI: {final_output}")
        
        # Update the history
        conversation_history += f"User: {user_input}\nJourney AI: {final_output}\n"
        
        print("\n" + "-" * 30)
except Exception as e:
    print(f"\nAn error occurred: {e}")