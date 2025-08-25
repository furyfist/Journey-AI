import os
from dotenv import load_dotenv
import google.generativeai as genai
from portia import Config, Portia, LLMProvider, PortiaToolRegistry

# --- Load Environment Variables ---
# Construct the path to the .env file relative to this file's location
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Configure Google Gemini API ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Create Temp Directory ---
TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Portia Agent Initialization ---
portia_agent = None
emailer_agent = None

try:
    # Check for necessary API keys
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PORTIA_API_KEY"):
        raise ValueError("API keys (GOOGLE_API_KEY, PORTIA_API_KEY) not found in .env file")

    # Base configuration for Portia agents
    base_config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )

    # Initialize the main research agent
    portia_agent = Portia(config=base_config)
    print("✅ Portia Research Agent is online.")

    # Initialize the agent responsible for emailing (with tools enabled)
    emailer_agent = Portia(config=base_config, tools=PortiaToolRegistry(config=base_config))
    print("✅ Portia Emailer Agent is online.")

except Exception as e:
    print(f"❌ Error initializing Portia Agents: {e}")
    # Set agents to None if initialization fails
    portia_agent = None
    emailer_agent = None