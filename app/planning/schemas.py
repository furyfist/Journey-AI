from typing import Optional

from pydantic import BaseModel, Field


class Activity(BaseModel):
    name: str = Field(description="Name of the activity or place")
    description: str = Field(description="1-2 sentence description")
    location: str = Field(description="Address or area name")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    duration_minutes: int = Field(description="Estimated time in minutes")
    cost_estimate: Optional[str] = Field(default=None, description="e.g. '$10-20', 'Free'")
    category: str = Field(description="food, attraction, transport, shopping, nature, culture, nightlife")
    reasoning: str = Field(description="Why this was chosen for this traveler")


class TimeBlock(BaseModel):
    label: str = Field(description="morning, afternoon, or evening")
    start_time: str = Field(description="e.g. '09:00'")
    end_time: str = Field(description="e.g. '12:30'")
    activities: list[Activity] = Field(min_length=1, max_length=4)
    block_summary: str = Field(description="One sentence summary of this block")


class DayPlan(BaseModel):
    day_number: int
    date: Optional[str] = Field(default=None, description="ISO date if dates provided")
    title: str = Field(description="Creative title for the day")
    weather: Optional[dict] = Field(default=None, description="Weather snapshot for this day")
    morning: TimeBlock
    afternoon: TimeBlock
    evening: TimeBlock
    day_summary: str


class ItinerarySchema(BaseModel):
    title: str = Field(description="Creative trip title")
    destination: str
    total_days: int
    budget_level: str
    persona: str = Field(description="Detected travel persona")
    summary: str = Field(description="2-3 sentence trip overview")
    days: list[DayPlan]
    tips: list[str] = Field(min_length=3, max_length=5, description="3-5 general tips for this destination")


# Internal pipeline transfer object

class ResearchBundle(BaseModel):
    destination: str
    prompt: str
    total_days: int
    weather: Optional[dict] = None
    places: dict[str, list[dict]] = {}
    budget: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
