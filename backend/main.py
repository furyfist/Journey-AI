import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from portia import Config, Portia, LLMProvider

# --- Load Environment Variables & Configure Google AI ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Pydantic Models ---
class PromptRequest(BaseModel):
    prompt: str

class ItineraryResponse(BaseModel):
    itinerary: str

# --- FastAPI App Initialization ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Portia Agent Configuration ---
RESEARCHER_PROMPT = "You are a research assistant. Your ONLY job is to use your search tool to find information on this single, specific query: "
SYNTHESIZER_PROMPT = """
You are an expert travel itinerary planner. You will be given a block of pre-researched text.
Your ONLY job is to synthesize and organize this information into a clear, helpful, and beautifully formatted travel itinerary.
Use markdown for formatting. If the research is insufficient, state what's missing.
"""

portia_agent = None
try:
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PORTIA_API_KEY"):
        raise ValueError("API keys not found in .env file")
    
    # We only need one Portia agent instance for research
    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        system_prompt=RESEARCHER_PROMPT,
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    portia_agent = Portia(config=config)
    print("✅ Portia Research Agent is online.")
except Exception as e:
    print(f"❌ Error initializing Portia Agent: {e}")

# --- NEW HELPER FUNCTION FOR THE PLANNER ---
async def get_research_plan(user_prompt: str) -> list[str]:
    """Uses Gemini to break a complex prompt into simple search queries."""
    planner_model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = f"""
    Based on the following user request, create a concise list of 3 to 5 simple, single-topic search queries that will gather the necessary information to build a travel plan.
    Return ONLY a valid JSON list of strings. Do not include any other text or markdown.

    Example:
    User Request: "Plan a 3-day budget trip to Rome with a focus on ancient history and pasta."
    Your Response:
    [
        "3 day budget itinerary for Rome",
        "opening times and ticket prices for the Colosseum and Roman Forum",
        "highly-rated budget pasta restaurants in Rome",
        "safety tips for tourists in Rome"
    ]

    User Request: "{user_prompt}"
    Your Response:
    """
    
    try:
        response = await planner_model.generate_content_async(prompt)
        # Clean up the response to ensure it's valid JSON
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        plan = json.loads(json_response)
        if isinstance(plan, list):
            return plan
        return []
    except Exception as e:
        print(f"Error creating research plan: {e}")
        return []

# --- API Endpoint ---
@app.post("/chat", response_model=ItineraryResponse)
async def chat_with_agent(request: PromptRequest):
    if not portia_agent:
        raise HTTPException(status_code=500, detail="Agent is not initialized.")

    try:
        # --- STAGE 1: THE PLANNER ---
        print(f"Stage 1: Planning research for prompt: '{request.prompt}'")
        research_tasks = await get_research_plan(request.prompt)
        if not research_tasks:
            raise HTTPException(status_code=500, detail="Failed to create a research plan.")
        print(f"Plan created: {research_tasks}")

        # --- STAGE 2: THE RESEARCHER ---
        print("Stage 2: Starting research...")
        collected_research = ""
        for task in research_tasks:
            print(f"  - Researching: {task}")
            research_result = await portia_agent.arun(task) # Using async version
            collected_research += f"Research on '{task}':\n{str(research_result.outputs.final_output)}\n\n"
        print("Stage 2: Research complete.")

        # --- STAGE 3: THE SYNTHESIZER ---
        print("Stage 3: Starting synthesis...")
        synthesizer_model = genai.GenerativeModel('gemini-1.5-pro-latest')
        synthesis_prompt = f"{SYNTHESIZER_PROMPT}\n\n--- RAW DATA ---\n{collected_research}\n--- END RAW DATA ---"
        synthesis_result = await synthesizer_model.generate_content_async(synthesis_prompt)
        final_itinerary = synthesis_result.text
        
        print("Stage 3: Synthesis complete.")
        return ItineraryResponse(itinerary=final_itinerary)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")