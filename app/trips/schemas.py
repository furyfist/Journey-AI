from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    prompt: str = Field(min_length=10, max_length=2000)
    destination: Optional[str] = None
    budget: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_days: Optional[int] = Field(default=None, ge=1, le=30)
    persona_hint: Optional[str] = None
    interests: Optional[list[str]] = None
    constraints: Optional[list[str]] = None
    travel_party: Optional[str] = None


class TripResponse(BaseModel):
    id: UUID
    prompt: str
    destination: str
    title: str
    summary: Optional[str]
    persona: Optional[str]
    status: str
    total_days: int
    created_at: datetime
    updated_at: datetime


class TripDetail(TripResponse):
    itinerary: Optional[dict] = None
    conflicts: list[dict] = []
    reasoning: dict = {}
    weather_data: Optional[dict] = None


class TripListItem(BaseModel):
    id: UUID
    title: str
    destination: str
    total_days: int
    status: str
    created_at: datetime
