# WMO weather interpretation codes → human label
# https://open-meteo.com/en/docs#weathervariables
WMO_WEATHER_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight showers",
    81: "Moderate showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}

# Overpass tag groups used when querying places
OSM_TAG_GROUPS: dict[str, list[str]] = {
    "attractions": [
        'node["tourism"~"attraction|museum|viewpoint|gallery|artwork"]',
        'node["historic"~"monument|castle|ruins|memorial|church"]',
    ],
    "food": [
        'node["amenity"~"restaurant|cafe|bar|pub|fast_food|food_court"]',
        'node["amenity"="marketplace"]',
    ],
    "nature": [
        'node["leisure"~"park|garden|nature_reserve|beach_resort"]',
    ],
    "nightlife": [
        'node["amenity"~"nightclub|bar|pub"]',
    ],
}

# Conflict detection thresholds
MAX_WALKABLE_DISTANCE_KM = 2.0
MAX_TRANSIT_DISTANCE_KM = 10.0
HEAVY_RAIN_MM = 5.0
