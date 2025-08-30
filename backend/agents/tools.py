# backend/agents/tools.py

import os
import ast
import googlemaps
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from googleapiclient.discovery import build
from langchain_google_community.places_api import GooglePlacesTool
from langchain_google_community.calendar.create_event import CalendarCreateEvent

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
        # We return both the content and the source URL, which fulfills the user's request for links.
        return "\n".join([f"- {res['content']} (Source: {res['url']})" for res in result['results']])
    except Exception as e:
        return f"An error occurred during the web search: {e}"

@tool
def find_flights(origin: str, destination: str, travel_dates: str) -> str:
    """
    Finds example flight information for a given route and dates by searching Google Flights.
    Use this tool ONLY when the user explicitly asks for flight details.
    """
    query = f"Example round-trip flight prices and options from {origin} to {destination} for {travel_dates} on Google Flights"
    print(f"-> Searching for flights with query: {query}")
    return search_the_web(query)


@tool
def find_hotels(destination: str, dates: str, guests: int) -> str:
    """
    Finds hotel options in a given destination for specific dates and number of guests.

    Use this tool ONLY when the user explicitly asks for accommodation or hotel options.
    It provides realistic, up-to-date examples by searching Booking.com.

    Args:
        destination (str): The city or area to search for hotels in (e.g., "downtown Paris").
        dates (str): A simple description of the check-in and check-out dates (e.g., "October 5th to 10th").
        guests (int): The number of guests requiring accommodation.
    """
    # This creates a very specific, "solid" query for our general search tool.
    query = f"Find top 3 hotel options with prices and review scores in {destination} for {guests} guests for dates {dates} on Booking.com"
    
    # We then execute the search. The result will naturally include links.
    print(f"-> Searching for hotels with query: {query}")
    return search_the_web(query)

@tool
def find_place_details(query: str) -> str:
    """
    Finds detailed information and a Google Maps link for a specific place or a category of places.

    Use this tool to find restaurants, museums, landmarks, or any point of interest.
    It's the best way to get an address, rating, website, and a direct Google Maps URL for inclusion in the itinerary.

    Args:
        query (str): The search query, which can be a specific name like "Eiffel Tower" or a category like "best pizza in Rome".
    """
    print(f"-> Finding place details for query: {query}")
    try:
        api_key = os.getenv("GPLACES_API_KEY")
        if not api_key:
            return "Error: GPLACES_API_KEY is not configured in the .env file."

        gmaps = googlemaps.Client(key=api_key)

        # Step 1: Search for a list of places using the text search endpoint.
        places_result = gmaps.places(query=query)

        if not places_result or 'results' not in places_result or not places_result['results']:
            return f"Sorry, I couldn't find any places for '{query}'."

        output = f"Here are some top suggestions for '{query}':\n"

        # Step 2: Get rich details for each of the top results.
        for place in places_result['results'][:3]: # Limit to top 3 for a clean UI
            place_id = place['place_id']
            
            # This 'place' call gets the rich details like website and URL.
            # The library returns a dictionary directly, no parsing is needed.
            details = gmaps.place(place_id=place_id, fields=['name', 'rating', 'formatted_address', 'url', 'website'])
            place_details = details.get('result', {})

            name = place_details.get('name', 'N/A')
            address = place_details.get('formatted_address', 'Address not available')
            rating = place_details.get('rating', 'No rating')
            gmaps_url = place_details.get('url', '#') # This is the direct Google Maps URL
            website = place_details.get('website', '')

            output += f"#### {name}\n"
            output += f"- **Rating**: {rating} ⭐\n"
            output += f"- **Address**: {address}\n"
            output += f"- **Google Maps**: [View on Map]({gmaps_url})\n"
            if website:
                output += f"- **Website**: [Visit Website]({website})\n"
            output += "\n"

        return output.strip()

    except Exception as e:
        return f"An error occurred while searching for places: {str(e)}"
    

@tool
def find_youtube_videos(topic: str) -> str:
    """
    Finds relevant YouTube videos for a given topic, separating long-form vlogs and Shorts.

    Use this tool when the user wants video content, travel vlogs, or visual guides.
    It returns a formatted list with thumbnails and links for both video types.

    Args:
        topic (str): The subject to search for, like "things to do in Tokyo" or "Paris food guide".
    """
    print(f"-> Finding YouTube videos for topic: {topic}")
    try:
        # IMPORTANT: You need a Google API Key with the "YouTube Data API v3" enabled.
        # This is the same GOOGLE_API_KEY from your .env file.
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "YouTube API key is missing. Please set GOOGLE_API_KEY in your .env file."

        youtube = build('youtube', 'v3', developerKey=api_key)
        output = ""

        # --- 1. Search for Long-Form Videos ---
        vlog_request = youtube.search().list(
            part="snippet",
            q=f"{topic} travel vlog",
            type="video",
            videoDuration="medium", # Filters for videos between 4 and 20 minutes
            maxResults=3
        )
        vlog_response = vlog_request.execute()

        output += "### Inspiring Travel Vlogs\n"
        if vlog_response.get("items"):
            for item in vlog_response["items"]:
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                # This is the Markdown for displaying a clickable thumbnail image
                output += f"[![{title}]({thumbnail_url})]({video_url})\n"
                output += f"**[{title}]({video_url})**\n\n"
        else:
            output += "No long-form vlogs found.\n"


        # --- 2. Search for Shorts ---
        shorts_request = youtube.search().list(
            part="snippet",
            q=f"{topic} #shorts",
            type="video",
            videoDuration="short", # Filters for videos under 4 minutes
            maxResults=3
        )
        shorts_response = shorts_request.execute()

        output += "\n### Quick Shorts & Tips\n"
        if shorts_response.get("items"):
            for item in shorts_response["items"]:
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                output += f"[![{title}]({thumbnail_url})]({video_url})\n"
                output += f"**[{title}]({video_url})**\n\n"
        else:
            output += "No relevant Shorts found.\n"

        return output.strip()

    except Exception as e:
        return f"An error occurred while searching YouTube: {str(e)}"
    
@tool
def add_trip_to_calendar(title: str, start_date: str, end_date: str, attendees: list[str] = None, description: str = "") -> str:
    """
    Creates a new event in the user's Google Calendar for the entire trip.

    Use this as the final step after the itinerary has been fully generated and approved.
    It requires a clear start and end date for the event.

    Args:
        title (str): The title of the calendar event (e.g., "Trip to Paris").
        start_date (str): The start date of the trip in YYYY-MM-DD format.
        end_date (str): The end date of the trip in YYYY-MM-DD format.
        attendees (list[str], optional): A list of attendee emails. Defaults to None.
        description (str, optional): A summary of the itinerary to add to the event description. Defaults to "".
    """
    print(f"-> Adding trip to calendar: {title}")
    try:
        # This uses the robust, community-built tool for Google Calendar
        calendar_tool = GoogleCalendarCreateEventTool()
        
        # The tool expects a single string with all arguments clearly laid out.
        # The agent's LLM brain is smart enough to format this correctly based on our description.
        tool_input = (
            f"Event Title: {title}\n"
            f"Start Date: {start_date}\n"
            f"End Date: {end_date}\n"
            f"Event Description: {description}\n"
        )
        if attendees:
            tool_input += f"Attendees: {', '.join(attendees)}"

        # The tool handles authentication and API calls for us.
        result = calendar_tool.run(tool_input)
        return f"Successfully created the calendar event! Details: {result}"

    except Exception as e:
        return f"An error occurred while creating the calendar event: {str(e)}"

