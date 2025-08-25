from core.config import portia_agent

async def find_youtube_vlogs(destination: str) -> str:
    """
    Uses the Portia agent's Search tool to find popular YouTube travel vlogs.
    
    Args:
        destination: The destination city for vlog search.

    Returns:
        A string containing the raw search results for YouTube travel vlogs.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    # Create a specific search query to guide the agent
    search_query = f"Find the top 3 most popular YouTube travel vlogs for {destination}."
    
    # Create a precise prompt that tells the agent exactly which tool to use and what to do
    agent_prompt = (
        f"Your task is to find YouTube travel vlogs. Use the 'search_tool' with the following exact query: '{search_query}'. "
        f"Return only the raw text output from the search tool."
    )
    
    print(f"  - YouTube Service: Instructing agent to search for travel vlogs...")
    
    try:
        # Run the agent with the precise instructions
        research_result = await portia_agent.arun(agent_prompt)
        vlog_data = str(research_result.outputs.final_output)
        print(f"  - YouTube Service: Received vlog data.")
        return vlog_data
    except Exception as e:
        print(f"  - YouTube Service Error: {e}")
        return "Failed to retrieve YouTube vlog information."