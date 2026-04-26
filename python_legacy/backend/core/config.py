"""Configuration module for AI Chemistry Chatbot Backend."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = ""
WOLFRAM_APP_ID = ""
POLLINATIONS_API_KEY = ""

try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    WOLFRAM_APP_ID = st.secrets.get("WOLFRAM_APP_ID", "")
    POLLINATIONS_API_KEY = st.secrets.get("POLLINATIONS_API_KEY", "")
except Exception:
    pass

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not WOLFRAM_APP_ID:
    WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "")
if not POLLINATIONS_API_KEY:
    POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# Backend Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Database Configuration (if needed)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chemistry_chatbot.db")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Tool Configuration
ENABLE_PUBCHEM = os.getenv("ENABLE_PUBCHEM", "true").lower() == "true"
ENABLE_WOLFRAM = os.getenv("ENABLE_WOLFRAM", "true").lower() == "true"
ENABLE_VISION = os.getenv("ENABLE_VISION", "true").lower() == "true"
ENABLE_MEDIA = os.getenv("ENABLE_MEDIA", "true").lower() == "true"

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,gif,webp,pdf,txt,doc,docx,xls,xlsx,ppt,pptx").split(",")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "chemistry_chatbot.log")

def validate_config():
    """Validate that required configuration is set."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is required for the backend. "
            "Please set it in your environment or .env file.\n"
            "Get your key at: https://aistudio.google.com/app/apikey"
        )
    
    # Check optional but recommended keys
    if not WOLFRAM_APP_ID:
        print("Warning: WOLFRAM_APP_ID not set. Wolfram Alpha features will be limited.")
    
    return True

def get_tool_status():
    """Get status of all tools based on available API keys."""
    return {
        "gemini": {
            "enabled": GEMINI_API_KEY != "",
            "status": "full" if GEMINI_API_KEY else "unavailable"
        },
        "pubchem": {
            "enabled": ENABLE_PUBCHEM,
            "status": "available" if ENABLE_PUBCHEM else "disabled"
        },
        "wolfram": {
            "enabled": ENABLE_WOLFRAM,
            "status": "full" if WOLFRAM_APP_ID else "limited"
        },
        "vision": {
            "enabled": ENABLE_VISION,
            "status": "full" if GEMINI_API_KEY else "limited"
        },
        "media": {
            "enabled": ENABLE_MEDIA,
            "status": "available" if ENABLE_MEDIA else "disabled"
        }
    }
