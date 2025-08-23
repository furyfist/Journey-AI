# backend/main.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from portia import Config, Portia, LLMProvider

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
# We now create TWO separate agents, one for each role.

RESEARCHER_PROMPT = """
You are an expert travel research assistant. Your ONLY job is to use your search tool to find information relevant to the user's query.
Return all the information you find as a single, detailed block of text. Do not add any conversational fluff or summaries.
"""

SYNTHESIZER_PROMPT = """
You are an expert travel itinerary planner. You will be given a block of pre-researched text.
Your ONLY job is to synthesize and organize this information into a clear, helpful, and beautifully formatted travel itinerary.
Use markdown for formatting, including headings, bold text, and lists. If the provided data is insufficient, state that clearly.
"""

researcher_agent = None
synthesizer_agent = None

try:
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PORTIA_API_KEY"):
        raise ValueError("API keys not found in .env file")
    
    # --- Create Researcher Agent ---
    researcher_config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        system_prompt=RESEARCHER_PROMPT,
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    researcher_agent = Portia(config=researcher_config)
    print("✅ Researcher Agent initialized successfully.")

    # --- Create Synthesizer Agent ---
    synthesizer_config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        system_prompt=SYNTHESIZER_PROMPT,
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    synthesizer_agent = Portia(config=synthesizer_config)
    print("✅ Synthesizer Agent initialized successfully.")

except Exception as e:
    print(f"❌ Error initializing Portia Agents: {e}")

# --- API Endpoint ---
@app.post("/chat", response_model=ItineraryResponse)
async def chat_with_agent(request: PromptRequest):
    if not researcher_agent or not synthesizer_agent:
        raise HTTPException(status_code=500, detail="One or more agents are not initialized. Check backend server logs.")

    try:
        # --- STAGE 1: RESEARCH ---
        print("Stage 1: Starting research...")
        research_result = researcher_agent.run(request.prompt)
        raw_data = str(research_result.outputs.final_output)
        print(f"Stage 1: Research complete.")

        # --- STAGE 2: SYNTHESIS ---
        print("Stage 2: Starting synthesis...")
        synthesis_prompt = (
            "Here is the raw data I have gathered. Please synthesize it into a final travel plan for me:\n\n"
            "--- RAW DATA ---\n"
            f"{raw_data}\n"
            "--- END RAW DATA ---"
        )
        synthesis_result = synthesizer_agent.run(synthesis_prompt)
        final_itinerary = str(synthesis_result.outputs.final_output)
        
        print("Stage 2: Synthesis complete.")
        return ItineraryResponse(itinerary=final_itinerary)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")