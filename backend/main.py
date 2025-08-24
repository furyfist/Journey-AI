# backend/main.py

import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from portia import Config, Portia, LLMProvider

# --- Load Environment Variables & Configure APIs ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Pydantic Models ---
class PromptRequest(BaseModel):
    prompt: str

class ItineraryResponse(BaseModel):
    itinerary: str

# --- FastAPI App Initialization & CORS ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Portia Agent Configuration ---
portia_agent = None
try:
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PORTIA_API_KEY"):
        raise ValueError("API keys not found in .env file")
    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    portia_agent = Portia(config=config)
    print("✅ Portia Research Agent is online.")
except Exception as e:
    print(f"❌ Error initializing Portia Agent: {e}")

# --- Helper Functions ---
async def get_research_plan(user_prompt: str) -> list[str]:
    """Uses Gemini to break a complex prompt into simple search queries."""
    # --- CHANGE 1: Switched back to gemini-1.5-flash ---
    planner_model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f'Based on the user request "{user_prompt}", create a JSON list of 3-5 simple, single-topic search queries to gather information for a travel plan. Return only the JSON list.'
    try:
        response = await planner_model.generate_content_async(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        plan = json.loads(json_response)
        return plan if isinstance(plan, list) else []
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
        max_retries = 2
        for task in research_tasks:
            print(f"  - Researching: {task}")
            for attempt in range(max_retries):
                try:
                    research_result = await portia_agent.arun(task)
                    collected_research += f"## Research on '{task}':\n{str(research_result.outputs.final_output)}\n\n"
                    break 
                except Exception as e:
                    print(f"  - Attempt {attempt + 1} failed for task '{task}': {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                    else:
                        collected_research += f"## Research on '{task}':\nFailed to retrieve information.\n\n"
        print("Stage 2: Research complete.")

        # --- STAGE 3: THE SYNTHESIZER ---
        print("Stage 3: Starting synthesis...")
        # --- CHANGE 2: Switched back to gemini-1.5-flash ---
        synthesizer_model = genai.GenerativeModel('gemini-1.5-flash')
        synthesis_prompt = (
            "You are an expert travel itinerary planner... Synthesize this information into a clear, helpful, and beautifully formatted travel itinerary using markdown.\n\n"
            f"--- RAW RESEARCH DATA ---\n{collected_research}\n--- END RAW RESEARCH DATA ---"
        )
        synthesis_result = await synthesizer_model.generate_content_async(synthesis_prompt)
        final_itinerary = synthesis_result.text
        
        print("Stage 3: Synthesis complete.")
        return ItineraryResponse(itinerary=final_itinerary)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")