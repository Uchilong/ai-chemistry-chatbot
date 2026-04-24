"""
AI Chemistry Chatbot - Multi-Model UI
Supports: Gemini (Accurate), Mistral (Fast), Ollama (Local)
"""

import streamlit as st
from PIL import Image
import sys
import os
from pathlib import Path
import tempfile

# Add src to path for importing brain modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brain import get_brain
from mistral_brain import get_mistral_brain
from ollama_brain import get_ollama_brain
from config import (
    GEMINI_API_KEY, MISTRAL_API_KEY, APP_TITLE, APP_ICON,
    SUPPORTED_FILE_TYPES, FILE_UPLOAD_LABEL, FILE_UPLOAD_HELP,
    CHAT_INPUT_PLACEHOLDER, MODEL_CONFIGS, validate_config
)

# ============================================================================
# 1. PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="🧪 AI Chemistry Tutor",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Gemini (Accurate)"

# ============================================================================
# 2. INITIALIZE AI BRAINS
# ============================================================================
available_models = {}
brains = {}

try:
    gemini_brain = get_brain()
    available_models["Gemini (Accurate)"] = MODEL_CONFIGS["gemini"]
    brains["Gemini (Accurate)"] = gemini_brain
except Exception as e:
    pass

try:
    mistral_brain = get_mistral_brain()
    available_models["Mistral (Fast)"] = MODEL_CONFIGS["mistral"]
    brains["Mistral (Fast)"] = mistral_brain
except Exception as e:
    pass

try:
    ollama_brain = get_ollama_brain(model="llama3.2:latest")
    if ollama_brain and ollama_brain._check_connection():
        available_models["Ollama (Local)"] = MODEL_CONFIGS["ollama"]
        brains["Ollama (Local)"] = ollama_brain
except Exception:
    pass

# Validate configuration
if not available_models:
    st.error(
        "❌ **No AI Models Available**\n\n"
        "Please configure at least one API:\n"
        "- **Gemini**: https://aistudio.google.com/app/apikey\n"
        "- **Mistral**: https://console.mistral.ai/api-keys/\n\n"
        "Set them in your `.env` file as `GEMINI_API_KEY` and `MISTRAL_API_KEY`"
    )
    st.stop()

# Get selected brain
brain = brains.get(st.session_state.selected_model)

# ============================================================================
# 3. CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.8);
    }
    
    .model-selector {
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #4CAF50;
        background-color: rgba(76, 175, 80, 0.1);
        margin-bottom: 15px;
    }
    
    .chemistry-keyboard-btn {
        background-color: #ff6b6b;
        color: white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 24px;
        border: none;
        cursor: pointer;
    }
    
    .quick-symbol {
        display: inline-block;
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    
    .quick-symbol:hover {
        background-color: #4CAF50;
        color: white;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 4. SIDEBAR - MODEL SELECTION & HISTORY
# ============================================================================
with st.sidebar:
    st.title("🧪 Chemistry Tutor AI")
    
    # Model Selection
    st.markdown("---")
    st.subheader("🤖 Select AI Model")
    
    cols = st.columns([0.8, 0.2])
    with cols[0]:
        selected = st.radio(
            "Model:",
            options=list(available_models.keys()),
            index=list(available_models.keys()).index(st.session_state.selected_model) 
                  if st.session_state.selected_model in available_models else 0,
            label_visibility="collapsed"
        )
    
    if selected != st.session_state.selected_model:
        st.session_state.selected_model = selected
        st.session_state.messages = []
        st.rerun()
    
    # Show model info
    model_info = available_models.get(st.session_state.selected_model)
    if model_info:
        with st.expander(f"ℹ️ {model_info['name']}", expanded=True):
            st.markdown(f"**{model_info['description']}**")
            st.markdown(f"⚡ Speed: {model_info['speed']}")
            st.markdown(f"✅ Best for: {model_info['best_for']}")
    
    st.markdown("---")
    
    # Chat Management
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()
    
    with col2:
        st.link_button(
            "⌨️ ChemKey",
            "https://educat.ninja/chemkey/",
            use_container_width=True,
            help="Open online chemistry symbol keyboard in a new tab"
        )
    
    st.markdown("---")
    
    # Chat History
    with st.expander("🕰️ Question History", expanded=False):
        if st.session_state.history:
            for i, q in enumerate(reversed(st.session_state.history[-20:])):
                if st.button(
                    q[:40] + "..." if len(q) > 40 else q,
                    key=f"hist_{i}",
                    use_container_width=True
                ):
                    st.session_state.chem_input_value = q
                    st.rerun()
        else:
            st.info("No history yet")

# ============================================================================
# 5. MAIN CHAT DISPLAY
# ============================================================================
st.title(f"{APP_ICON} AI Chemistry Tutor - {st.session_state.selected_model}")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"], width=300, caption=message.get("file_name", "Image"))
        if "file_name" in message and "image" not in message:
            st.caption(f"📁 File: {message['file_name']}")

# ============================================================================
# 6. INPUT AREA - FILE UPLOAD & TEXT INPUT
# ============================================================================
st.markdown("---")

# File upload
uploaded_file = None
col_file, col_chat = st.columns([0.15, 0.85])

with col_file:
    with st.popover("📎 Upload"):
        st.markdown("### 📤 Upload File")
        uploaded_file = st.file_uploader(
            FILE_UPLOAD_LABEL,
            type=SUPPORTED_FILE_TYPES,
            help=FILE_UPLOAD_HELP,
            label_visibility="collapsed"
        )
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")

# Chat input
with col_chat:
    prompt = st.chat_input(CHAT_INPUT_PLACEHOLDER, key="main_chat_input")

# ============================================================================
# 7. MESSAGE PROCESSING & RESPONSE
# ============================================================================
if prompt:
    if not brain:
        st.error(f"❌ {st.session_state.selected_model} is not available")
    else:
        # Prepare message
        new_message = {"role": "user", "content": prompt}
        image_data = None
        
        # Handle file upload
        if uploaded_file:
            if uploaded_file.type.startswith("image"):
                image = Image.open(uploaded_file)
                new_message["image"] = image
                new_message["file_name"] = uploaded_file.name
                
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    image.save(tmp.name)
                    image_data = tmp.name
            else:
                # Text or PDF file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    image_data = tmp.name
            
            new_message["file_name"] = uploaded_file.name
            st.session_state.history.append(f"📎 {prompt[:30]}...")
        else:
            st.session_state.history.append(prompt)
        
        st.session_state.messages.append(new_message)
        
        # Get AI response
        with st.spinner(f"🤖 {st.session_state.selected_model} is thinking..."):
            try:
                if image_data:
                    # Use appropriate method based on model
                    if st.session_state.selected_model == "Gemini (Accurate)":
                        ai_response = brain.chat_with_file(prompt, image_data)
                    elif st.session_state.selected_model == "Mistral (Fast)":
                        ai_response = brain.chat_with_file(prompt, image_data)
                    else:  # Ollama
                        ai_response = "⚠️ File analysis requires Gemini or Mistral API"
                    
                    # Cleanup
                    try:
                        os.unlink(image_data)
                    except:
                        pass
                else:
                    # Text only
                    ai_response = brain.chat(prompt, chat_history=st.session_state.messages[:-1])
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        st.rerun()

# ============================================================================
# 8. INFO & FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
    <small>
    🧪 AI Chemistry Tutor | Multi-Model Support | Fast & Accurate Learning
    </small>
    </div>
    """, unsafe_allow_html=True)
