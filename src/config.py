"""Configuration module for AI Chemistry Chatbot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import Streamlit for cloud deployment
try:
    import streamlit as st
    # On Streamlit Cloud, try to use secrets if available
    try:
        if "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        else:
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    except Exception:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    try:
        if "MISTRAL_API_KEY" in st.secrets:
            MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
        else:
            MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    except Exception:
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
        
except ImportError:
    # Not running in Streamlit context - just use env vars
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# App Configuration
APP_TITLE = "🧪 AI Trợ lý Hóa học"
APP_DESCRIPTION = "Chatbot hỗ trợ học hóa học sử dụng múa mô hình AI"
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
    },
    "ollama": {
        "name": "💻 Ollama (Local)",
        "description": "Works offline on your computer. No API keys needed.",
        "speed": "Variable",
        "best_for": "Privacy, offline use"
    }
}

# Supported file types
SUPPORTED_IMAGE_TYPES = ["jpg", "png", "jpeg", "gif", "webp"]
SUPPORTED_FILE_TYPES = SUPPORTED_IMAGE_TYPES + ["pdf", "txt"]

# Chemistry Keyboard Configuration
CHEMISTRY_SYMBOLS = {
    "Elements": {
        "H": "Hydrogen", "C": "Carbon", "N": "Nitrogen", "O": "Oxygen",
        "S": "Sulfur", "P": "Phosphorus", "F": "Fluorine", "Cl": "Chlorine",
        "Br": "Bromine", "I": "Iodine", "Na": "Sodium", "K": "Potassium",
        "Ca": "Calcium", "Fe": "Iron", "Cu": "Copper", "Zn": "Zinc",
        "Ag": "Silver", "Au": "Gold", "Pb": "Lead", "Hg": "Mercury"
    },
    "Bonds & Reactions": {
        "→": "Reaction arrow (forward)",
        "⇌": "Equilibrium",
        "=": "Double bond",
        "≡": "Triple bond",
        "•": "Unpaired electron",
        "Δ": "Heat",
        "hν": "Light",
        "[±]": "Charged"
    },
    "Operators": {
        "+": "Plus/Addition",
        "-": "Minus/Removal",
        "(": "Bracket open",
        ")": "Bracket close",
        "²": "Superscript 2",
        "³": "Superscript 3",
        "⁻": "Superscript minus"
    },
    "Common Ions": {
        "H⁺": "Hydrogen ion",
        "OH⁻": "Hydroxide",
        "Na⁺": "Sodium ion",
        "Cl⁻": "Chloride",
        "SO₄²⁻": "Sulfate",
        "NO₃⁻": "Nitrate",
        "HCO₃⁻": "Bicarbonate",
        "NH₄⁺": "Ammonium"
    }
}

# UI Configuration
CHAT_INPUT_PLACEHOLDER = "Nhập câu hỏi hóa học..."
FILE_UPLOAD_LABEL = "Tải tệp hoặc Dán ảnh (Ctrl+V) tại đây"
FILE_UPLOAD_HELP = "Hỗ trợ: jpg, png, gif, pdf, txt. Bạn có thể dán ảnh bằng Ctrl+V"

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
