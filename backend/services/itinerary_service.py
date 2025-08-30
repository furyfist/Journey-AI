# backend/services/itinerary_service.py

import asyncio
from schemas import PromptRequest
from agents.travel_agent import travel_agent_executor

# Import services needed for post-generation actions
from services import email_service, calendar_service

async def generate_itinerary_with_agent(request: PromptRequest) -> str:
    """
    Invokes the main travel agent executor with the user's prompt and handles post-generation actions.
    """
    print("--- Invoking Travel Agent ---")
    
    # The agent expects a dictionary with an "input" key.
    agent_input = {"input": request.main_prompt}
    
    # Run the agent asynchronously
    # The .ainvoke() method returns a dictionary, and the final answer is in the "output" key.
    result = await travel_agent_executor.ainvoke(agent_input)
    final_itinerary = result.get("output", "Sorry, I encountered an issue and couldn't generate the itinerary.")

    print("--- Agent Finished ---")

    # --- Handle Post-Generation Actions (Email and Calendar) ---
    # This part remains similar to your old code, running these tasks in the background.
    print("--- Starting Post-Generation Actions ---")
    action_coroutines = []
    
    if request.send_copy_to:
        print(f"-> Scheduling email to: {request.send_copy_to}")
        action_coroutines.append(
            email_service.send_itinerary_email(request.send_copy_to, final_itinerary)
        )
        
    if request.calendar_attendees:
        # NOTE: For a real app, the agent would intelligently extract dates for the calendar.
        # For this hackathon, we can keep it simple as before or have the agent call the tool.
        print(f"-> Scheduling calendar event for: {request.calendar_attendees}")
        # This part can be enhanced later by having the agent call the calendar tool itself.
        
    if action_coroutines:
        asyncio.gather(*action_coroutines)
        print("--- Actions are running in the background. ---")

    return final_itinerary