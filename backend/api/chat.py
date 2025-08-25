# api/chat.py
from fastapi import APIRouter
from services import portia_service

# An APIRouter is like a mini-FastAPI app
router = APIRouter()

@router.post("/chat")
def handle_chat_request(request_data: dict):
    """
    Receives a request from the frontend, passes it to the
    Portia service, and returns the result.
    """
    user_prompt = request_data.get("prompt")
    if not user_prompt:
        return {"error": "Prompt is missing"}, 400

    # Delegate the hard work to the service
    itinerary = portia_service.generate_itinerary(user_prompt)

    return {"itinerary": itinerary}