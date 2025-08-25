## from grok

from core.config import portia_agent

async def find_hotel_info(destination: str, travel_dates: str) -> str:
    """
    Uses the Portia agent's Search tool to find mock hotel information.
    
    Args:
        destination: The destination city for hotel search.
        travel_dates: A string describing the travel dates (e.g., "next weekend").

    Returns:
        A string containing the raw search results for hotels.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    # Create a specific search query to guide the agent
    search_query = f"Find example hotel options in {destination} for {travel_dates} on Booking.com or Google Hotels."
    
    # Create a precise prompt that tells the agent exactly which tool to use and what to do
    agent_prompt = (
        f"Your task is to find hotel information. Use the 'search_tool' with the following exact query: '{search_query}'. "
        f"Return only the raw text output from the search tool."
    )
    
    print(f"  - Hotel Service: Instructing agent to search for hotels...")
    
    try:
        # Run the agent with the precise instructions
        research_result = await portia_agent.arun(agent_prompt)
        hotel_data = str(research_result.outputs.final_output)
        print(f"  - Hotel Service: Received hotel data.")
        return hotel_data
    except Exception as e:
        print(f"  - Hotel Service Error: {e}")
        return "Failed to retrieve hotel information."