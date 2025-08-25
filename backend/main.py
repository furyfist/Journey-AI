# backend/main.py

import os
import json
import asyncio
import io
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from portia import Config, Portia, LLMProvider, PortiaToolRegistry
from markdown_it import MarkdownIt
from weasyprint import HTML, CSS

# --- Load Environment Variables & Configure APIs ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Pydantic Models ---
class PromptRequest(BaseModel): prompt: str
class ItineraryResponse(BaseModel): itinerary: str
class PdfRequest(BaseModel): markdown_text: str
class EmailRequest(BaseModel): email: str; markdown_text: str

# --- FastAPI App Initialization & CORS ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Create Temp Directory & Mount Static Files ---
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

# --- Portia Agent Configuration ---
portia_agent = None
emailer_agent = None
try:
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("PORTIA_API_KEY"):
        raise ValueError("API keys not found in .env file")
    
    base_config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    portia_agent = Portia(config=base_config)
    print("✅ Portia Research Agent is online.")
    
    emailer_agent = Portia(config=base_config, tools=PortiaToolRegistry(config=base_config))
    print("✅ Portia Emailer Agent is online.")
except Exception as e:
    print(f"❌ Error initializing Portia Agents: {e}")


# --- HELPER FUNCTIONS ---

async def get_research_plan(user_prompt: str) -> list[str]:
    planner_model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f'Based on the user request "{user_prompt}", create a JSON list of 3-5 simple, single-topic search queries to gather information for a travel plan. Return only the JSON list.'
    try:
        response = await planner_model.generate_content_async(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        plan = json.loads(json_response)
        return plan if isinstance(plan, list) else []
    except Exception as e:
        print(f"Error creating research plan: {e}")
        return []

def create_pdf_from_itinerary(markdown_text: str) -> bytes:
    md = MarkdownIt()
    html_content = md.render(markdown_text)
    css_string = """
    @page { size: A4; margin: 2cm; }
    body { font-family: 'Helvetica', sans-serif; font-size: 11pt; line-height: 1.5; }
    h1, h2, h3 { font-family: 'Times New Roman', serif; color: #333; }
    h1 { font-size: 22pt; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px;}
    h2 { font-size: 16pt; }
    h3 { font-size: 13pt; }
    strong { font-weight: bold; }
    """
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[CSS(string=css_string)])
    return pdf_bytes

# --- API ENDPOINTS ---

@app.post("/chat", response_model=ItineraryResponse)
async def chat_with_agent(request: PromptRequest):
    if not portia_agent: raise HTTPException(status_code=500, detail="Agent not initialized.")
    try:
        # STAGE 1: PLANNER
        print(f"Stage 1: Planning research for prompt: '{request.prompt}'")
        research_tasks = await get_research_plan(request.prompt)
        if not research_tasks: raise HTTPException(status_code=500, detail="Failed to create research plan.")
        print(f"Plan created: {research_tasks}")
        
        # STAGE 2: RESEARCHER (with Retry Logic)
        print("Stage 2: Starting research...")
        collected_research = ""
        max_retries = 2
        for task in research_tasks:
            print(f"  - Researching: {task}")
            for attempt in range(max_retries):
                try:
                    research_result = await portia_agent.arun(task)
                    collected_research += f"## Research on '{task}':\n{str(research_result.outputs.final_output)}\n\n"
                    break 
                except Exception as e:
                    print(f"  - Attempt {attempt + 1} failed for task '{task}': {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                    else:
                        collected_research += f"## Research on '{task}':\nFailed to retrieve information.\n\n"
        print("Stage 2: Research complete.")
        
        # STAGE 3: SYNTHESIZER
        print("Stage 3: Starting synthesis...")
        synthesizer_model = genai.GenerativeModel('gemini-1.5-flash')
        synthesis_prompt = (
            "You are an expert travel itinerary planner. You will be given pre-researched text, separated by headings. "
            "Synthesize this into a clear, helpful, and beautifully formatted travel itinerary using markdown. "
            "If some research failed, acknowledge it and create the best plan possible with the available information.\n\n"
            f"--- RAW RESEARCH DATA ---\n{collected_research}\n--- END RAW RESEARCH DATA ---"
        )
        synthesis_result = await synthesizer_model.generate_content_async(synthesis_prompt)
        final_itinerary = synthesis_result.text
        print("Stage 3: Synthesis complete.")
        return ItineraryResponse(itinerary=final_itinerary)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/download-pdf")
async def download_pdf(request: PdfRequest):
    try:
        pdf_bytes = create_pdf_from_itinerary(request.markdown_text)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename=itinerary.pdf'})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate PDF.")

@app.post("/send-email")
async def send_email(request: EmailRequest):
    if not emailer_agent: raise HTTPException(status_code=500, detail="Emailer Agent not initialized.")
    ngrok_url = os.getenv("NGROK_URL")
    if not ngrok_url: raise HTTPException(status_code=500, detail="NGROK_URL not configured in .env file.")

    temp_filename = f"{uuid.uuid4()}.pdf"
    temp_filepath = os.path.join(TEMP_DIR, temp_filename)
    
    try:
        print(f"Generating temporary PDF for email: {temp_filename}")
        pdf_bytes = create_pdf_from_itinerary(request.markdown_text)
        with open(temp_filepath, "wb") as f:
            f.write(pdf_bytes)
        
        public_pdf_url = f"{ngrok_url}/temp/{temp_filename}"
        print(f"PDF available at public URL: {public_pdf_url}")
        
        email_prompt = (
            f"Your task is to send an email. Follow this two-step process exactly:\n"
            f"Step 1: Use the 'Google Draft Email Tool' to create a draft for '{request.email}'. Subject: 'Your Journey AI Travel Itinerary'. Body: 'Here is your personalized travel plan. Enjoy your trip!'. Attach the file from this URL: {public_pdf_url}.\n"
            f"Step 2: Take the draft ID from step 1 and use the 'Google Send Draft Email Tool' to send the email."
        )

        print("Calling Emailer Agent with two-step prompt...")
        await emailer_agent.arun(email_prompt)
        
        print("Email sent successfully.")
        return {"message": "Email sent successfully!"}
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"Cleaned up temporary file: {temp_filename}")