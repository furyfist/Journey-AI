import requests
import os
from dotenv import load_dotenv

load_dotenv() # load environtment from .env file

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(destination: str) -> str:
    """
    Fetches the current weather for a given destination
    """

    if not API_KEY:
        return "Error in whether api key"
    
    params = {
        "q": destination,
        "appid": API_KEY,
        "units": "metric"
    }

    try: 
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # extract format
        weather_description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feel_like = data["main"]["feels_like"]
        city = data["name"]
        country = data["sys"]["country"]

        return (f"The Current weather in {city}, {country} is {temp}°C" 
                f"(feels like {feel_like}°C) with {weather_description}")
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except KeyError:
        return f"Error: Could not find weather data for '{destination}'. Please check the city name."
