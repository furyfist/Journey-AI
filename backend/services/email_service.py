# backend/services/email_service.py
import os
import uuid
from core.config import emailer_agent, TEMP_DIR
from services.pdf_service import create_pdf_from_itinerary

async def send_itinerary_email(email: str, markdown_text: str):
    """
    Generates a PDF, creates a public URL, and uses the Portia agent to send an email.
    """
    if not emailer_agent:
        raise Exception("Emailer Agent not initialized.")

    ngrok_url = os.getenv("NGROK_URL")
    if not ngrok_url:
        raise Exception("NGROK_URL not configured in .env file.")

    # Create a unique filename for the temporary PDF
    temp_filename = f"{uuid.uuid4()}.pdf"
    temp_filepath = os.path.join(TEMP_DIR, temp_filename)
    
    try:
        print(f"Generating temporary PDF for email: {temp_filename}")
        pdf_bytes = create_pdf_from_itinerary(markdown_text)
        with open(temp_filepath, "wb") as f:
            f.write(pdf_bytes)
        
        # Construct the public URL for the PDF file
        public_pdf_url = f"{ngrok_url}/temp/{temp_filename}"
        print(f"PDF available at public URL: {public_pdf_url}")
        
        # Create a precise, multi-step prompt for the emailer agent
        email_prompt = (
            f"Your task is to send an email. Follow this two-step process exactly:\n"
            f"Step 1: Use the 'Google Draft Email Tool' to create a draft for '{email}'. Subject: 'Your Journey AI Travel Itinerary'. Body: 'Here is your personalized travel plan. Enjoy your trip!'. Attach the file from this URL: {public_pdf_url}.\n"
            f"Step 2: Take the draft ID from step 1 and use the 'Google Send Draft Email Tool' to send the email."
        )

        print("Calling Emailer Agent with two-step prompt...")
        await emailer_agent.arun(email_prompt)
        print("Email agent task completed.")

    finally:
        # Ensure the temporary file is always cleaned up
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"Cleaned up temporary file: {temp_filename}")