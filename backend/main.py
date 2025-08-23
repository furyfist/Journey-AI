# backend/main.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from portia import Config, Portia, LLMProvider, InvalidAgentOutputError

# --- Load Environment Variables ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Pydantic Models ---
class PromptRequest(BaseModel):
    prompt: str

class ItineraryResponse(BaseModel):
    itinerary: str

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Middleware ---
origins = ["http://localhost", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Portia Agent Configuration ---
portia_agent = None
try:
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PORTIA_API_KEY"):
        raise ValueError("API keys not found in .env file")

    SYSTEM_PROMPT = """
    You are Journey AI, a helpful travel research assistant. 
    Your primary job is to use your search tool to find information related to the user's prompt and then synthesize that information into a coherent final answer.
    """
    
    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        system_prompt=SYSTEM_PROMPT,
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    portia_agent = Portia(config=config)
    print("✅ Portia Agent initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing Portia Agent: {e}")

# --- API Endpoint ---
@app.post("/chat", response_model=ItineraryResponse)
async def chat_with_agent(request: PromptRequest):
    if not portia_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized. Check backend server logs.")

    print(f"Received prompt: {request.prompt}")
    
    try:
        # We run the agent with the user's prompt
        response_object = portia_agent.run(request.prompt)
        final_output = response_object.outputs.final_output

        # The response from Portia can sometimes be an object, not a string.
        # We'll safely convert it to a string to avoid errors.
        if not isinstance(final_output, str):
            final_output = str(final_output)

        print(f"Agent response: {final_output}")
        return ItineraryResponse(itinerary=final_output)

    except InvalidAgentOutputError as e:
        # This catches the specific "data handoff" error
        print(f"Agent execution error (data handoff): {e}")
        raise HTTPException(status_code=500, detail="The agent failed during the final summarization step. Please try rephrasing your prompt.")
    except Exception as e:
        # This catches any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")