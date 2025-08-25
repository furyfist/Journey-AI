# backend/schemas.py
from pydantic import BaseModel

# --- Existing Models ---
class PromptRequest(BaseModel):
    prompt: str

class ItineraryResponse(BaseModel):
    itinerary: str

class PdfRequest(BaseModel):
    markdown_text: str

class EmailRequest(BaseModel):
    email: str
    markdown_text: str

# --- New Models for Feature Endpoints ---
class FlightRequest(BaseModel):
    origin: str
    destination: str
    dates: str

class HotelRequest(BaseModel):
    destination: str
    dates: str
    guests: int

class YoutubeRequest(BaseModel):
    topic: str

# --- New Model for Calendar Feature ---
class CalendarEventRequest(BaseModel):
    title: str
    start_time: str # Expected in ISO format: "2024-09-20T20:00:00"
    end_time: str   # Expected in ISO format: "2024-09-20T21:00:00"
    description: str
    attendees: list[str] = [] # Defaults to an empty list