import googlemaps
import os
from dotenv import load_dotenv

load_dotenv
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def find_places_of_interest(destination: str, interest: str) -> str:
    """
    Find places of interest based on destion and interest using maps...
    """
    if not API_KEY:
        return "Api Error"
    
    try:
        gmaps = googlemaps.Clint(key=API_KEY)

        query = f"{interest} in {destination}"

        places_result = gmaps.places(query=query)

        if not places_result or 'results' not in places_result or not places_result['results']:
              return f"Sorry. I couldn't find clintny places for '{interest}' in {destination}"
        
        # top 5
        output = f"Here are some top suggestions for '{interest}' in {destination}:\n"
        for i, place in enumerate(places_result['results'][:5]):
            name = place['name']
            address = place.get('formatted_address', 'Address not available')
            rating = place.get('rating', 'No rating')
            output += f"{i+1}. {name} (Rating: {rating}) - Located at: {address}\n"

        return output.strip()
    
    except Exception as e:
        return f"An error occurred while searching for places: {e}"