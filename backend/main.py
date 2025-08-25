# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api import chat  # Import the router from our api module
from core import config # This ensures agents are initialized on startup

# --- FastAPI App Initialization & CORS ---
app = FastAPI(
    title="Journey AI Backend",
    description="A refactored, professional backend for the Journey AI travel planner.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173"], # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount Static Files ---
# This makes the 'temp' directory publicly accessible for file downloads
app.mount("/temp", StaticFiles(directory=config.TEMP_DIR), name="temp")

# --- Include API Router ---
# All routes from api/chat.py will be available under the /api prefix
app.include_router(chat.router, prefix="/api")

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
def read_root():
    """ A simple root endpoint to confirm the server is running. """
    return {"status": "OK", "message": "Welcome to the Journey AI v2 Backend!"}