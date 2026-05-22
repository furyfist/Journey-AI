WEATHER_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Fetch weather forecast for a city. Returns daily temperature, precipitation, and "
            "weather description. Also returns the city's lat and lon — use those values for "
            "subsequent search_places calls."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Tokyo', 'Paris'",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of forecast days (1–16)",
                    "minimum": 1,
                    "maximum": 16,
                },
            },
            "required": ["city", "days"],
        },
    },
}

PLACES_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "search_places",
        "description": (
            "Search for points of interest near a location by category. "
            "Call multiple times for different categories to gather diverse options."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude of the search center"},
                "lon": {"type": "number", "description": "Longitude of the search center"},
                "category": {
                    "type": "string",
                    "enum": ["attractions", "food", "nature", "nightlife"],
                    "description": "Category of places to search",
                },
                "radius": {
                    "type": "integer",
                    "description": "Search radius in meters (500–20000). Default: 5000.",
                    "minimum": 500,
                    "maximum": 20000,
                },
            },
            "required": ["lat", "lon", "category"],
        },
    },
}

RESEARCHER_TOOLS: list[dict] = [WEATHER_TOOL, PLACES_TOOL]
