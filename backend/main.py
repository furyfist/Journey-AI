from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tools.weather import get_weather
from tools.places import find_places_of_interest 
from tools.youtube import find_youtube_video
#initialize 
app = FastAPI(
    title="Journey AI Tools",
    description="API endpoints for the tools used by the Journey AI agent.",
    version="1.0.0"
)


class WeatherRequest(BaseModel):
    destination: str

class PlacesRequest(BaseModel):
    destination: str
    interest: str


@app.post("/tools/get_weather")
def weather_endpoint(request: WeatherRequest):
    """API endpoint to get the weather for a destination."""
    try:
        weather_data = get_weather(destination=request.destination)
        return {"result": weather_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/find_places") 
def places_endpoint(request: PlacesRequest):
    """API endpoint to find places of interest."""
    try:
        places_data = find_places_of_interest(
            destination=request.destination,
                        interest=request.interest
        )
        return {"result": places_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/find_youtube_video") 
def youtube_endpoint(request: WeatherRequest):
    """API endpoint to find a YouTube video for a destination."""
    try:
        video_data = find_youtube_video(destination=request.destination)
        return {"result": video_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """Check server status."""
    return {"status": "Journey AI backend is running!"}