"""Configuration module for AI Chemistry Chatbot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize API keys, which will be populated by secrets or env vars.
GEMINI_API_KEY = ""
MISTRAL_API_KEY = ""
GROQ_API_KEY = ""

# Try to load from Streamlit secrets first (for cloud deployment)
try:
    import streamlit as st
    # This will raise an error if secrets.toml is not found locally,
    # which is the desired behavior to fall back to environment variables.
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY", "")
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    # This block will be entered if:
    # 1. `streamlit` is not installed (ImportError).
    # 2. `secrets.toml` is not found when running locally (StreamlitSecretNotFoundError).
    # In either case, we'll proceed to the fallback mechanism.
    pass

# Fallback to environment variables if secrets are not available or not set.
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not MISTRAL_API_KEY:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
if not GROQ_API_KEY:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# App Configuration
APP_TITLE = "🧪 AI Trợ lý Hóa học"
APP_DESCRIPTION = "Chatbot hỗ trợ học hóa học sử dụng mô hình AI"
APP_ICON = "🧪"

# Model Configuration
MODEL_NAME = "gemini-2.0-flash"
MISTRAL_MODEL = "mistral-large-latest"

# Model Descriptions
MODEL_CONFIGS = {
    "gemini": {
        "name": "🧠 Gemini (Accurate Thinking)",
        "description": "Accurate, thorough analysis with detailed reasoning. Best for complex chemistry problems.",
        "speed": "Standard",
        "best_for": "In-depth analysis, calculations, structure analysis"
    },
    "mistral": {
        "name": "⚡ Mistral (Fast Thinking)",
        "description": "Fast, concise answers. Perfect for quick chemistry questions and definitions.",
        "speed": "Fast",
        "best_for": "Quick answers, definitions, fast lookup"
    }
}

# Supported file types
SUPPORTED_IMAGE_TYPES = ["jpg", "png", "jpeg", "gif", "webp"]
SUPPORTED_FILE_TYPES = SUPPORTED_IMAGE_TYPES + ["pdf", "txt"]

# UI Configuration
CHAT_INPUT_PLACEHOLDER = "Nhập câu hỏi hóa học..."
FILE_UPLOAD_LABEL = "Tải tệp hoặc Dán ảnh (Ctrl+V) tại đây"
FILE_UPLOAD_HELP = "Hỗ trợ: jpg, png, gif, pdf, txt. Bạn có thể dán ảnh bằng Ctrl+V"
UI_THEME_MODE = os.getenv("UI_THEME_MODE", "auto").lower()  # auto, light, dark
DEFAULT_CHEMISTRY_LEVEL = os.getenv("DEFAULT_CHEMISTRY_LEVEL", "undergrad")
DEFAULT_RESPONSE_STYLE = os.getenv("DEFAULT_RESPONSE_STYLE", "balanced")

# Validation
def validate_config():
    """Validate that all required configuration is set."""
    available_apis = []
    
    if GEMINI_API_KEY:
        available_apis.append("Gemini")
    if MISTRAL_API_KEY:
        available_apis.append("Mistral")
    
    if not available_apis:
        raise ValueError(
            "No AI APIs configured. Please set at least one:\n"
            "- GEMINI_API_KEY: https://aistudio.google.com/app/apikey\n"
            "- MISTRAL_API_KEY: https://console.mistral.ai/api-keys/"
        )
    
    return True
