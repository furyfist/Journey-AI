# backend/api/chat.py
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas import PromptRequest, ItineraryResponse, PdfRequest, EmailRequest
from services import itinerary_service, pdf_service, email_service

router = APIRouter()

@router.post("/chat", response_model=ItineraryResponse)
async def chat_with_agent(request: PromptRequest):
    try:
        final_itinerary = await itinerary_service.create_full_itinerary(request.prompt)
        return ItineraryResponse(itinerary=final_itinerary)
    except Exception as e:
        print(f"An unexpected error occurred in /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-pdf")
async def download_pdf(request: PdfRequest):
    try:
        pdf_bytes = pdf_service.create_pdf_from_itinerary(request.markdown_text)
        return StreamingResponse(
            io.BytesIO(pdf_bytes), 
            media_type='application/pdf', 
            headers={'Content-Disposition': 'attachment; filename=itinerary.pdf'}
        )
    except Exception as e:
        print(f"An unexpected error occurred in /download-pdf: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF.")

@router.post("/send-email")
async def send_email(request: EmailRequest):
    try:
        await email_service.send_itinerary_email(request.email, request.markdown_text)
        return {"message": "Email sent successfully!"}
    except Exception as e:
        print(f"An unexpected error occurred in /send-email: {e}")
        raise HTTPException(status_code=500, detail=str(e))