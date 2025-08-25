# backend/services/flight_service.py
from core.config import portia_agent

async def find_flight_info(origin: str, destination: str, travel_dates: str) -> str:
    """
    Uses the Portia agent's Search tool to find mock flight information.
    
    Args:
        origin: The starting city or airport.
        destination: The destination city or airport.
        travel_dates: A string describing the travel dates (e.g., "next weekend").

    Returns:
        A string containing the raw search results for flights.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    # Create a very specific search query to guide the agent
    search_query = f"Find example round-trip flight prices from {origin} to {destination} for {travel_dates} on Google Flights."
    
    # Create a precise prompt that tells the agent exactly which tool to use and what to do
    agent_prompt = (
        f"Your task is to find flight information. Use the 'search_tool' with the following exact query: '{search_query}'. "
        f"Return only the raw text output from the search tool."
    )
    
    print(f"  - Flight Service: Instructing agent to search for flights...")
    
    try:
        # Run the agent with the precise instructions
        research_result = await portia_agent.arun(agent_prompt)
        flight_data = str(research_result.outputs.final_output)
        print(f"  - Flight Service: Received flight data.")
        return flight_data
    except Exception as e:
        print(f"  - Flight Service Error: {e}")
        return "Failed to retrieve flight information."