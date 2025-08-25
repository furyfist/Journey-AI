# backend/services/youtube_service.py
from core.config import portia_agent

async def find_youtube_vlogs(topic: str) -> str:
    """
    Uses the Portia agent's Search tool to find YouTube travel vlogs.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    search_query = f"Find the top 3 most popular YouTube travel vlogs about '{topic}'."
    agent_prompt = f"Use the 'search_tool' with the exact query: '{search_query}'. Return only the raw text output from the search tool."

    print(f"YouTube Service: Instructing agent to search for vlogs...")
    try:
        result = await portia_agent.arun(agent_prompt)
        return str(result.outputs.final_output)
    except Exception as e:
        print(f"YouTube Service Error: {e}")
        return "Failed to retrieve YouTube vlog information."