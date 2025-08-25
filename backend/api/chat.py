# backend/api/chat.py
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

# Import all schemas
from schemas import (
    PromptRequest as ChatRequest, ItineraryResponse, PdfRequest, EmailRequest,
    FlightRequest, HotelRequest, YoutubeRequest, CalendarEventRequest
)

# Import all services
from services import (
    itinerary_service, pdf_service, email_service,
    flight_service, hotel_service, youtube_service, calendar_service
)

router = APIRouter()

# --- Main Itinerary Endpoint ---
@router.post("/chat", response_model=ItineraryResponse, tags=["Main Flow"])
async def chat_with_agent(request: ChatRequest): # <-- This now correctly uses the ChatRequest model
    try:
        # --- THIS IS THE FIX ---
        # We now pass the entire 'request' object to the service,
        # not just the prompt string.
        final_itinerary = await itinerary_service.create_full_itinerary(request)
        # --- END OF FIX ---
        
        return ItineraryResponse(itinerary=final_itinerary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Utility Endpoints ---
@router.post("/download-pdf", tags=["Utilities"])
async def download_pdf(request: PdfRequest):
    try:
        pdf_bytes = pdf_service.create_pdf_from_itinerary(request.markdown_text)
        return StreamingResponse(
            io.BytesIO(pdf_bytes), 
            media_type='application/pdf', 
            headers={'Content-Disposition': 'attachment; filename=itinerary.pdf'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate PDF.")

@router.post("/send-email", tags=["Utilities"])
async def send_email(request: EmailRequest):
    try:
        await email_service.send_itinerary_email(request.email, request.markdown_text)
        return {"message": "Email sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Feature Test Endpoints ---
@router.post("/find-flights", tags=["Feature Tests"])
async def find_flights(request: FlightRequest):
    try:
        flight_data = await flight_service.find_flight_info(request.origin, request.destination, request.dates)
        return {"flight_data": flight_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-hotels", tags=["Feature Tests"])
async def find_hotels(request: HotelRequest):
    try:
        hotel_data = await hotel_service.find_hotel_info(request.destination, request.dates, request.guests)
        return {"hotel_data": hotel_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-youtube-vlogs", tags=["Feature Tests"])
async def find_youtube_vlogs(request: YoutubeRequest):
    try:
        youtube_data = await youtube_service.find_youtube_vlogs(request.topic)
        return {"youtube_data": youtube_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-calendar-event", tags=["Feature Tests"])
async def add_calendar_event(request: CalendarEventRequest):
    try:
        result = await calendar_service.add_event_to_calendar(
            title=request.title,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            attendees=request.attendees
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))