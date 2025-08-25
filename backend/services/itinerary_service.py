# backend/services/itinerary_service.py
import json
import asyncio
import google.generativeai as genai
from core.config import portia_agent

# Import all the new feature services
from services import flight_service, hotel_service, youtube_service

async def get_structured_master_plan(user_prompt: str) -> dict:
    """
    Uses Gemini to parse the user's prompt and create a structured JSON master plan.
    This is a much more intelligent planner than before.
    """
    planner_model = genai.GenerativeModel('gemini-1.5-flash')
    
    # This new prompt asks the AI to act as a parser and identify key details.
    prompt = (
        "You are a travel planning assistant. Your job is to parse a user's request and extract key information into a structured JSON object. "
        "Identify the destination, travel dates, number of travelers, and any specific features they request (flights, hotels, youtube). "
        "Also, create a short list of general research topics based on their request.\n\n"
        f"User Request: \"{user_prompt}\"\n\n"
        "JSON Output:"
    )
    
    try:
        response = await planner_model.generate_content_async(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        plan = json.loads(json_response)
        return plan if isinstance(plan, dict) else {}
    except Exception as e:
        print(f"Error creating master plan: {e}")
        return {}

async def create_full_itinerary(user_prompt: str) -> str:
    """
    Orchestrates the new, more powerful 3-stage process to generate a rich itinerary.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    # STAGE 1: INTELLIGENT PLANNER
    print(f"Stage 1: Creating master plan for prompt: '{user_prompt}'")
    master_plan = await get_structured_master_plan(user_prompt)
    if not master_plan:
        raise Exception("Failed to create a structured master plan.")
    print(f"Master plan created: {master_plan}")
    
    # STAGE 2: DYNAMIC RESEARCHER (Concurrent Execution)
    print("Stage 2: Starting concurrent research...")
    
    research_coroutines = []
    features = master_plan.get("features_requested", [])
    
    # Dynamically add tasks to the list based on the master plan
    if "flights" in features:
        research_coroutines.append(flight_service.find_flight_info(
            origin=master_plan.get("origin", "user's location"), # Default origin
            destination=master_plan.get("destination"),
            dates=master_plan.get("dates")
        ))
    
    if "hotels" in features:
        research_coroutines.append(hotel_service.find_hotel_info(
            destination=master_plan.get("destination"),
            dates=master_plan.get("dates"),
            guests=master_plan.get("travelers", 1) # Default to 1 guest
        ))

    if "youtube" in features:
        research_coroutines.append(youtube_service.find_youtube_vlogs(
            topic=f"travel in {master_plan.get('destination')}"
        ))

    # Add generic research tasks
    for topic in master_plan.get("generic_research_topics", []):
        research_coroutines.append(portia_agent.arun(topic))

    # Run all research tasks in parallel for hackathon-level speed
    research_results = await asyncio.gather(*research_coroutines, return_exceptions=True)
    
    # STAGE 3: MASTER SYNTHESIZER
    print("Stage 3: Aggregating and synthesizing all research...")
    
    # Aggregate results into a single, well-structured text block
    collected_research = ""
    if "flights" in features:
        collected_research += f"## Flight Information:\n{research_results.pop(0)}\n\n"
    if "hotels" in features:
        collected_research += f"## Hotel Options:\n{research_results.pop(0)}\n\n"
    if "youtube" in features:
        collected_research += f"## Recommended YouTube Vlogs:\n{research_results.pop(0)}\n\n"
    
    # Add generic research results
    collected_research += "## General Travel Research:\n"
    for result in research_results:
        if isinstance(result, Exception):
            collected_research += "- Research failed for one topic.\n"
        else:
            collected_research += f"- {str(result.outputs.final_output)}\n"

    # Create the final, enhanced prompt for the synthesizer
    synthesizer_model = genai.GenerativeModel('gemini-1.5-flash')
    synthesis_prompt = (
        "You are an expert travel itinerary creator. You will be given pre-researched text, clearly separated by headings for flights, hotels, vlogs, and general topics. "
        "Your task is to synthesize all of this information into a single, cohesive, and beautifully formatted travel itinerary using markdown. "
        "Present the flight and hotel options clearly. Weave the YouTube links into the relevant parts of the daily plan. "
        "If any research failed, acknowledge it gracefully and create the best plan possible with the available information.\n\n"
        f"--- RAW RESEARCH DATA ---\n{collected_research}\n--- END RAW RESEARCH DATA ---"
    )
    
    synthesis_result = await synthesizer_model.generate_content_async(synthesis_prompt)
    final_itinerary = synthesis_result.text
    print("Stage 3: Master synthesis complete.")
    
    return final_itinerary