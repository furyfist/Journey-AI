import json
import asyncio
import google.generativeai as genai
from core.config import portia_agent
from services.flight_service import find_flight_info

async def get_research_plan(user_prompt: str) -> list[str]:
    """
    Uses Gemini to create a structured list of research tasks from a user prompt, including flight search.
    """
    planner_model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        f'Based on the user request "{user_prompt}", create a JSON list of 3-5 simple, single-topic search queries '
        'to gather information for a travel plan. Include one query specifically for finding flights, formatted as '
        '"Find flights from [Origin] to [Destination] for [Dates]". Return only the JSON list.'
    )
    try:
        response = await planner_model.generate_content_async(prompt)
        # Clean up the response to ensure it's valid JSON
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        plan = json.loads(json_response)
        return plan if isinstance(plan, list) else []
    except Exception as e:
        print(f"Error creating research plan: {e}")
        return []

async def create_full_itinerary(user_prompt: str) -> str:
    """
    Orchestrates the 3-stage process of planning, researching, and synthesizing an itinerary.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    # STAGE 1: PLANNER
    print(f"Stage 1: Planning research for prompt: '{user_prompt}'")
    research_tasks = await get_research_plan(user_prompt)
    if not research_tasks:
        raise Exception("Failed to create research plan.")
    print(f"Plan created: {research_tasks}")
    
    # STAGE 2: RESEARCHER (with Retry Logic)
    print("Stage 2: Starting research...")
    collected_research = ""
    max_retries = 2
    for task in research_tasks:
        print(f"  - Researching: {task}")
        for attempt in range(max_retries):
            try:
                if "flight" in task.lower():
                    research_result = await find_flight_info(task)
                    collected_research += f"## Research on '{task}':\n{str(research_result)}\n\n"
                else:
                    research_result = await portia_agent.arun(task)
                    collected_research += f"## Research on '{task}':\n{str(research_result.outputs.final_output)}\n\n"
                break  # Success, exit retry loop
            except Exception as e:
                print(f"  - Attempt {attempt + 1} failed for task '{task}': {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait before retrying
                else:
                    collected_research += f"## Research on '{task}':\nFailed to retrieve information.\n\n"
    print("Stage 2: Research complete.")
    
    # STAGE 3: SYNTHESIZER
    print("Stage 3: Starting synthesis...")
    synthesizer_model = genai.GenerativeModel('gemini-1.5-flash')
    synthesis_prompt = (
        "You are an expert travel itinerary planner. You will be given pre-researched text, separated by headings. "
        "Synthesize this into a clear, helpful, and beautifully formatted travel itinerary using markdown. "
        "If some research failed, acknowledge it and create the best plan possible with the available information.\n\n"
        f"--- RAW RESEARCH DATA ---\n{collected_research}\n--- END RAW RESEARCH DATA ---"
    )
    synthesis_result = await synthesizer_model.generate_content_async(synthesis_prompt)
    final_itinerary = synthesis_result.text
    print("Stage 3: Synthesis complete.")
    
    return final_itinerary