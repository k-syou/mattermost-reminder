"""
FastAPI application for Mattermost message scheduler
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin
try:
    # Try to get existing app
    from firebase_admin import get_app
    get_app()
except ValueError:
    # App doesn't exist, initialize it
    # Use Application Default Credentials in production
    # For local development, use service account key
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        initialize_app(cred)
    else:
        # Use default credentials (for Firebase Functions)
        initialize_app()

db = firestore.client()

app = FastAPI(
    title="Mattermost Scheduler API",
    description="API for scheduling recurring messages to Mattermost via webhooks",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers (dependencies are imported within routers)
# Ensure proper Python path for Firebase Functions
import sys
import os
functions_dir = os.path.dirname(os.path.abspath(__file__))
if functions_dir not in sys.path:
    sys.path.insert(0, functions_dir)

from routers import webhooks, messages

# Include routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

# Note: Scheduler endpoint is available at /scheduler/send-messages
# but for Firebase Functions, we use scheduled_function.py instead


@app.get("/")
async def root():
    return {
        "message": "Mattermost Scheduler API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
