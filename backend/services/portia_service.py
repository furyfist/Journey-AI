# services/portia_service.py
from portia import Portia, Config
from portia.tool_registry import DefaultToolRegistry

# Note: We are not importing 'settings' anymore because the Config object handles it.

class PortiaAgent:
    def __init__(self):
        print("Initializing Portia Config and Agent...")
        
        # 1. Load the default config. It will automatically find the API key
        #    from your .env file (e.g., GOOGLE_API_KEY).
        config = Config.from_default()

        # 2. Load the default tool registry, which contains tools like Search, Browser, etc.
        tool_registry = DefaultToolRegistry(config)

        # 3. Create the Portia instance with the config and tools.
        #    This is the correct way to initialize it.
        self.agent = Portia(config=config, tools=tool_registry)
        
        print("Portia Agent initialized successfully.")

    def run(self, prompt: str) -> dict:
        """
        This is where the actual call to the Portia agent's run method would happen.
        """
        print(f"--- Sending prompt to Portia ---")
        print(prompt)
        print(f"---------------------------------")
        
        response = self.agent.run(prompt)
        
        # The response object from portia.run() is a Pydantic model.
        # We need to convert it to a dictionary to send it as JSON.
        if response:
            return response.model_dump(indent=2)
        
        return {"status": "error", "message": "No response from agent."}

# Create a single, reusable instance of our agent class
portia_agent = PortiaAgent()

def generate_itinerary(user_prompt: str) -> dict:
    """
    A clean function that takes a user prompt and uses the Portia
    agent to generate an itinerary.
    """
    response = portia_agent.run(user_prompt)
    return response