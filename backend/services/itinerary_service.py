# backend/services/itinerary_service.py
import json
import asyncio
import google.generativeai as genai
from schemas import PromptRequest as ChatRequest
from core.config import portia_agent
from services import flight_service, hotel_service, youtube_service, email_service, calendar_service

# The get_structured_master_plan function is correct and does not need changes.
async def get_structured_master_plan(user_prompt: str) -> dict:
    planner_model = genai.GenerativeModel('gemini-1.5-flash')
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


# --- THIS IS THE CORRECTED FUNCTION ---
async def create_full_itinerary(request: ChatRequest) -> str:
    """
    Orchestrates the entire process: itinerary generation AND post-generation actions.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    print(f"Stage 1: Creating master plan for prompt: '{request.main_prompt}'")
    master_plan = await get_structured_master_plan(request.main_prompt)
    if not master_plan:
        raise Exception("Failed to create a structured master plan.")
    print(f"Master plan created: {master_plan}")
    
    print("Stage 2: Starting concurrent research...")
    research_coroutines = []
    
    # --- FIX START ---
    # Correctly parse the 'features' dictionary from the master plan
    features = master_plan.get("features", {})
    
    if features.get("flights"): # Check the boolean value in the dictionary
        research_coroutines.append(flight_service.find_flight_info(
            origin=master_plan.get("origin", "user's location"),
            destination=master_plan.get("destination"),
            dates=str(master_plan.get("travel_dates")) # Pass dates as string
        ))
    
    if features.get("hotels"): # Check the boolean value in the dictionary
        research_coroutines.append(hotel_service.find_hotel_info(
            destination=master_plan.get("destination"),
            dates=str(master_plan.get("travel_dates")),
            guests=master_plan.get("num_travelers", 1)
        ))

    if features.get("youtube"): # Check the boolean value in the dictionary
        research_coroutines.append(youtube_service.find_youtube_vlogs(
            topic=f"travel in {master_plan.get('destination')}"
        ))

    # Correctly get the list of topics from the 'research_topics' key
    for topic in master_plan.get("research_topics", []):
        research_coroutines.append(portia_agent.arun(topic))
    # --- FIX END ---

    if not research_coroutines:
        print("Warning: No research tasks were generated from the master plan.")
        return "I was able to create a plan, but couldn't identify specific research tasks. Could you try rephrasing your request?"

    research_results = await asyncio.gather(*research_coroutines, return_exceptions=True)
    
    print("Stage 3: Aggregating and synthesizing all research...")
    collected_research = ""
    
    # This logic handles the dynamic nature of the results
    result_index = 0
    if features.get("flights"):
        collected_research += f"## Flight Information:\n{research_results[result_index]}\n\n"
        result_index += 1
    if features.get("hotels"):
        collected_research += f"## Hotel Options:\n{research_results[result_index]}\n\n"
        result_index += 1
    if features.get("youtube"):
        collected_research += f"## Recommended YouTube Vlogs:\n{research_results[result_index]}\n\n"
        result_index += 1
    
    collected_research += "## General Travel Research:\n"
    # The rest of the results are from the generic topics
    for i in range(result_index, len(research_results)):
        result = research_results[i]
        if isinstance(result, Exception):
            collected_research += "- Research failed for one topic.\n"
        else:
            collected_research += f"- {str(result.outputs.final_output)}\n"

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

    print("Stage 4: Starting post-generation actions (email, calendar)...")
    action_coroutines = []
    
    if request.send_copy_to:
        action_coroutines.append(
            email_service.send_itinerary_email(request.send_copy_to, final_itinerary)
        )
        
    if request.calendar_attendees:
        action_coroutines.append(
            calendar_service.add_event_to_calendar(
                title=f"Trip to {master_plan.get('destination', 'your destination')}",
                start_time="2025-11-10T09:00:00",
                end_time="2025-11-14T18:00:00",
                description="Your travel itinerary created by Journey AI.",
                attendees=request.calendar_attendees
            )
        )
        
    if action_coroutines:
        # Run these tasks in the background
        asyncio.gather(*action_coroutines)
        print("Stage 4: Actions are running in the background.")

    return final_itinerary