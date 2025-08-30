# backend/agents/tools.py
import os
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

# Load environment variables from .env file
load_dotenv()

# Initialize the Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def search_the_web(query: str) -> str:
    """
    Searches the web for up-to-date information using the Tavily search engine.
    This tool is best for broad, fact-based queries that require the latest information.
    """
    try:
        result = tavily_client.search(query=query, max_results=3)
        return "\n".join([f"- {res['content']} (Source: {res['url']})" for res in result['results']])
    except Exception as e:
        return f"An error occurred during the web search: {e}"

# --- NEW TOOL ADDED BELOW ---

@tool
def find_flights(origin: str, destination: str, travel_dates: str) -> str:
    """
    Finds example flight information for a given route and dates.

    Use this tool ONLY when the user explicitly asks for flight details. It provides
    realistic, up-to-date example prices and options by searching Google Flights.

    Args:
        origin (str): The starting city or airport code (e.g., "NYC").
        destination (str): The destination city or airport code (e.g., "LHR").
        travel_dates (str): A simple description of the dates (e.g., "October 5th to 10th" or "first week of July").
    """
    # This creates a very specific, "solid" query for our general search tool.
    query = f"Example round-trip flight prices and options from {origin} to {destination} for {travel_dates} on Google Flights"
    
    # We then execute the search using our other tool.
    print(f"-> Searching for flights with query: {query}")
    return search_the_web(query)