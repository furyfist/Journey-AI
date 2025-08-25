from pydantic import BaseModel

# Defines the structure for the /chat endpoint request
class PromptRequest(BaseModel):
    prompt: str

# Defines the structure for the /chat endpoint response
class ItineraryResponse(BaseModel):
    itinerary: str

# Defines the structure for the /download-pdf endpoint request
class PdfRequest(BaseModel):
    markdown_text: str

# Defines the structure for the /send-email endpoint request
class EmailRequest(BaseModel):
    email: str
    markdown_text: str