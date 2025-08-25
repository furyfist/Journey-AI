# backend/services/hotel_service.py
from core.config import portia_agent

async def find_hotel_info(destination: str, dates: str, guests: int) -> str:
    """
    Uses the Portia agent's Search tool to find mock hotel information.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    search_query = f"Find 3 hotel options in {destination} for {guests} guests for the dates {dates} on Booking.com with prices."
    agent_prompt = f"Use the 'search_tool' with the exact query: '{search_query}'. Return only the raw text output from the search tool."

    print(f"Hotel Service: Instructing agent to search for hotels...")
    try:
        result = await portia_agent.arun(agent_prompt)
        return str(result.outputs.final_output)
    except Exception as e:
        print(f"Hotel Service Error: {e}")
        return "Failed to retrieve hotel information."
