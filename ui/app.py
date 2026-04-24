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
from user_store import (
    init_user_store,
    get_or_create_user,
    save_chat_event,
    load_chat_events,
    save_question,
    load_questions,
    add_learning_resource,
    load_learning_resources,
    delete_learning_resource,
)
from safe_calc import evaluate_expression
from config import (
    GEMINI_API_KEY, MISTRAL_API_KEY, APP_TITLE, APP_ICON,
    SUPPORTED_FILE_TYPES, FILE_UPLOAD_LABEL, FILE_UPLOAD_HELP,
    CHAT_INPUT_PLACEHOLDER, MODEL_CONFIGS, validate_config,
    UI_THEME_MODE, DEFAULT_CHEMISTRY_LEVEL, DEFAULT_RESPONSE_STYLE
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
    st.session_state.selected_model = "Mistral (Fast)"
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "learning_resources" not in st.session_state:
    st.session_state.learning_resources = []
if "chat_draft_input" not in st.session_state:
    st.session_state.chat_draft_input = ""
if "calc_expr" not in st.session_state:
    st.session_state.calc_expr = ""
if "calc_error" not in st.session_state:
    st.session_state.calc_error = ""

init_user_store()


def append_to_draft(token: str) -> None:
    st.session_state.chat_draft_input = f"{st.session_state.chat_draft_input}{token}"


def append_to_calc(token: str) -> None:
    st.session_state.calc_expr = f"{st.session_state.calc_expr}{token}"

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

# Ensure selected model is valid and default to Mistral when available
if st.session_state.selected_model not in available_models:
    if "Mistral (Fast)" in available_models:
        st.session_state.selected_model = "Mistral (Fast)"
    else:
        st.session_state.selected_model = list(available_models.keys())[0]

# Get selected brain
brain = brains.get(st.session_state.selected_model)

# ============================================================================
# 3. CUSTOM CSS STYLING
# ============================================================================
theme_base = st.get_option("theme.base") or "light"
resolved_theme = UI_THEME_MODE if UI_THEME_MODE in {"light", "dark"} else theme_base
if resolved_theme == "dark":
    chat_bg = "#111827"
    chat_text = "#f3f4f6"
    chat_border = "#374151"
    code_bg = "#1f2937"
    code_text = "#f3f4f6"
else:
    chat_bg = "#ffffff"
    chat_text = "#111827"
    chat_border = "#e6e8ee"
    code_bg = "#f3f4f6"
    code_text = "#111827"

css = """
    <style>
    /* Gemini-like clean layout */
    .block-container {{
        max-width: 980px;
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .app-header {{
        text-align: center;
        margin-bottom: 1rem;
    }}
    .app-header h1 {{
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }}
    .app-header p {{
        color: #6b7280;
        margin-top: 0;
    }}

    .stChatMessage {{
        border-radius: 16px;
        padding: 12px 14px;
        border: 1px solid __CHAT_BORDER__;
        background-color: __CHAT_BG__;
        color: __CHAT_TEXT__ !important;
    }}

    .stChatMessage p,
    .stChatMessage li,
    .stChatMessage span,
    .stChatMessage div,
    .stChatMessage label {{
        color: __CHAT_TEXT__ !important;
    }}

    .stChatMessage code {{
        color: __CODE_TEXT__ !important;
        background-color: __CODE_BG__ !important;
    }}

    .stChatMessage pre {{
        color: #e5e7eb !important;
        background-color: #111827 !important;
    }}

    .stMarkdown p, .stMarkdown li {{
        color: inherit;
    }}

    [data-testid="stSidebar"] {{
        border-right: 1px solid #e6e8ee;
    }}
    </style>
    """
css = (
    css.replace("__CHAT_BORDER__", chat_border)
    .replace("__CHAT_BG__", chat_bg)
    .replace("__CHAT_TEXT__", chat_text)
    .replace("__CODE_TEXT__", code_text)
    .replace("__CODE_BG__", code_bg)
)
st.markdown(css, unsafe_allow_html=True)

# ============================================================================
# 4. SIDEBAR - MODEL SELECTION & HISTORY
# ============================================================================
with st.sidebar:
    st.title("🧪 Chemistry AI")
    
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

    st.markdown("---")
    st.subheader("👤 Account")
    if not st.session_state.user_id:
        email_input = st.text_input(
            "Sign in with Google email",
            placeholder="yourname@gmail.com",
            key="login_email_input"
        )
        if st.button("Sign In", use_container_width=True):
            if email_input and "@" in email_input:
                user_id = get_or_create_user(email_input)
                st.session_state.user_id = user_id
                st.session_state.user_email = email_input.strip().lower()
                st.session_state.messages = load_chat_events(user_id)
                st.session_state.history = load_questions(user_id)
                st.session_state.learning_resources = load_learning_resources(user_id)
                st.success("Signed in and progress loaded.")
                st.rerun()
            else:
                st.error("Please enter a valid email.")
    else:
        st.caption(f"Signed in as: {st.session_state.user_email}")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_email = ""
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.learning_resources = []
            st.rerun()
    
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
    st.link_button(
        "🧮 Scientific Calculator",
        "https://mathda.com/calculator/vi",
        use_container_width=True,
        help="Open external scientific calculator (MathDA)"
    )
    
    st.markdown("---")

    with st.expander("📚 Learning Resources", expanded=False):
        if st.session_state.user_id:
            title = st.text_input("Title", key="resource_title")
            link = st.text_input("Link", key="resource_link", placeholder="https://...")
            notes = st.text_area("Notes (optional)", key="resource_notes", height=80)
            if st.button("Save Resource", use_container_width=True):
                if title.strip() and link.strip():
                    add_learning_resource(st.session_state.user_id, title, link, notes)
                    st.session_state.learning_resources = load_learning_resources(st.session_state.user_id)
                    st.success("Resource saved.")
                    st.rerun()
                else:
                    st.error("Title and link are required.")

            if st.session_state.learning_resources:
                for resource in st.session_state.learning_resources:
                    st.markdown(f"**{resource['title']}**")
                    st.markdown(f"[{resource['link']}]({resource['link']})")
                    if resource["notes"]:
                        st.caption(resource["notes"])
                    if st.button("Delete", key=f"del_res_{resource['id']}", use_container_width=True):
                        delete_learning_resource(st.session_state.user_id, resource["id"])
                        st.session_state.learning_resources = load_learning_resources(st.session_state.user_id)
                        st.rerun()
                    st.markdown("---")
            else:
                st.info("No saved resources yet.")
        else:
            st.info("Sign in to save learning resources.")
    
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
st.markdown(
    f"""
    <div class="app-header">
        <h1>{APP_ICON} Chemistry AI</h1>
        <p>{st.session_state.selected_model}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Contest-ready quick chemistry tasks
quick_prompt = None
st.markdown("### Quick Solve Modes")
q1, q2, q3, q4 = st.columns(4)
with q1:
    if st.button("Balance Reaction", use_container_width=True):
        quick_prompt = "Balance this reaction and verify atom counts: Fe + O2 -> Fe2O3"
with q2:
    if st.button("Stoichiometry", use_container_width=True):
        quick_prompt = "How many grams of NaCl can be formed from 2 mol Na with excess Cl2? Show every step."
with q3:
    if st.button("Molar Mass", use_container_width=True):
        quick_prompt = "Calculate the molar mass of Ca(OH)2 and show atomic mass contributions."
with q4:
    if st.button("Acid/Base pH", use_container_width=True):
        quick_prompt = "If [H+] = 1.0e-4 M, calculate pH and provide a quick check."

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

with st.expander("Math Input Tools", expanded=False):
    st.link_button(
        "Open Scientific Calculator (MathDA)",
        "https://mathda.com/calculator/vi",
        use_container_width=False
    )
    tab_pop, tab_trig, tab_calc, tab_cmp, tab_greek, tab_calcpad = st.tabs(
        ["Popular", "Trig", "Calculus", "Comparisons", "Greek", "Calculator"]
    )

    with tab_pop:
        pop_tokens = ["→", "⇌", "Δ", "hν", "H₂O", "CO₂", "OH⁻", "H⁺", "NaCl", "=", "+", "-", "×", "÷", "π"]
        pop_cols = st.columns(5)
        for i, token in enumerate(pop_tokens):
            with pop_cols[i % 5]:
                if st.button(token, key=f"pop_tok_{i}", use_container_width=True):
                    append_to_draft(token)

    with tab_trig:
        trig_tokens = ["sin(", "cos(", "tan(", "csc(", "sec(", "cot(", "arcsin(", "arccos(", "arctan(", ")", "pi", "e"]
        trig_cols = st.columns(6)
        for i, token in enumerate(trig_tokens):
            with trig_cols[i % 6]:
                if st.button(token, key=f"trig_tok_{i}", use_container_width=True):
                    append_to_draft(token)

    with tab_calc:
        calc_tokens = ["d/dx", "∫", "∂", "∇", "lim", "Σ", "Π", "∞", "√(", "x²", "x⁻¹", "| |"]
        calc_cols = st.columns(6)
        for i, token in enumerate(calc_tokens):
            with calc_cols[i % 6]:
                if st.button(token, key=f"calc_tok_{i}", use_container_width=True):
                    append_to_draft(token)

    with tab_cmp:
        cmp_tokens = [">", "<", "=", "≥", "≤", "≠", "±", "≈", "∝", "∈", "∉", "↔", "→", "←"]
        cmp_cols = st.columns(7)
        for i, token in enumerate(cmp_tokens):
            with cmp_cols[i % 7]:
                if st.button(token, key=f"cmp_tok_{i}", use_container_width=True):
                    append_to_draft(token)

    with tab_greek:
        greek_tokens = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "λ", "μ", "ν", "ρ", "σ", "τ", "φ", "χ", "ω"]
        greek_cols = st.columns(9)
        for i, token in enumerate(greek_tokens):
            with greek_cols[i % 9]:
                if st.button(token, key=f"gr_tok_{i}", use_container_width=True):
                    append_to_draft(token)

    with tab_calcpad:
        st.text_input("Expression", key="calc_expr", placeholder="e.g. (2+3)*sqrt(16)")
        k1 = st.columns(5)
        for i, token in enumerate(["7", "8", "9", "/", "("]):
            with k1[i]:
                if st.button(token, key=f"kp1_{token}", use_container_width=True):
                    append_to_calc(token)
        k2 = st.columns(5)
        for i, token in enumerate(["4", "5", "6", "*", ")"]):
            with k2[i]:
                if st.button(token, key=f"kp2_{token}", use_container_width=True):
                    append_to_calc(token)
        k3 = st.columns(5)
        for i, token in enumerate(["1", "2", "3", "-", "^"]):
            with k3[i]:
                if st.button(token, key=f"kp3_{token}", use_container_width=True):
                    append_to_calc(token)
        k4 = st.columns(5)
        for i, token in enumerate(["0", ".", "pi", "+", "sqrt("]):
            with k4[i]:
                if st.button(token, key=f"kp4_{token}", use_container_width=True):
                    append_to_calc(token)
        k5 = st.columns(5)
        with k5[0]:
            if st.button("⌫", key="kp_backspace", use_container_width=True):
                st.session_state.calc_expr = st.session_state.calc_expr[:-1]
        with k5[1]:
            if st.button("Clear", key="kp_clear", use_container_width=True):
                st.session_state.calc_expr = ""
                st.session_state.calc_error = ""
        with k5[2]:
            if st.button("Result → Draft", key="kp_eval_append", use_container_width=True):
                try:
                    result = evaluate_expression(st.session_state.calc_expr)
                    append_to_draft(str(result))
                    st.session_state.calc_error = ""
                except Exception as exc:
                    st.session_state.calc_error = f"Calculator error: {exc}"
        with k5[3]:
            if st.button("Expr=Res → Draft", key="kp_eval_expr", use_container_width=True):
                try:
                    result = evaluate_expression(st.session_state.calc_expr)
                    append_to_draft(f"{st.session_state.calc_expr} = {result}")
                    st.session_state.calc_error = ""
                except Exception as exc:
                    st.session_state.calc_error = f"Calculator error: {exc}"
        with k5[4]:
            if st.button("e", key="kp_e", use_container_width=True):
                append_to_calc("e")
        if st.session_state.calc_error:
            st.error(st.session_state.calc_error)

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
    st.text_area(
        "Message",
        key="chat_draft_input",
        height=90,
        label_visibility="collapsed",
        placeholder=CHAT_INPUT_PLACEHOLDER
    )
    send_col, clear_col = st.columns([0.8, 0.2])
    with send_col:
        send_clicked = st.button("Send", key="send_draft_btn", use_container_width=True)
    with clear_col:
        if st.button("Clear", key="clear_draft_btn", use_container_width=True):
            st.session_state.chat_draft_input = ""
    prompt = st.session_state.chat_draft_input.strip() if send_clicked else None

if quick_prompt:
    prompt = quick_prompt

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
            if st.session_state.user_id:
                save_question(st.session_state.user_id, f"📎 {prompt[:30]}...")
        else:
            st.session_state.history.append(prompt)
            if st.session_state.user_id:
                save_question(st.session_state.user_id, prompt)
        
        st.session_state.messages.append(new_message)
        if st.session_state.user_id:
            save_chat_event(
                st.session_state.user_id,
                role="user",
                content=prompt,
                file_name=new_message.get("file_name"),
            )
        
        # Get AI response
        with st.spinner(f"🤖 {st.session_state.selected_model} is thinking..."):
            try:
                if image_data:
                    # Use appropriate method based on model
                    if st.session_state.selected_model == "Gemini (Accurate)":
                        ai_response = brain.chat_with_file(
                            prompt,
                            image_data,
                            chemistry_context={
                                "level": DEFAULT_CHEMISTRY_LEVEL,
                                "style": DEFAULT_RESPONSE_STYLE
                            }
                        )
                    elif st.session_state.selected_model == "Mistral (Fast)":
                        ai_response = brain.chat_with_file(
                            prompt,
                            image_data,
                            chemistry_context={
                                "level": DEFAULT_CHEMISTRY_LEVEL,
                                "style": DEFAULT_RESPONSE_STYLE
                            }
                        )
                    else:  # Ollama
                        ai_response = "⚠️ File analysis requires Gemini or Mistral API"
                    
                    # Cleanup
                    try:
                        os.unlink(image_data)
                    except:
                        pass
                else:
                    # Text only
                    ai_response = brain.chat(
                        prompt,
                        chat_history=st.session_state.messages[:-1],
                        chemistry_context={
                            "level": DEFAULT_CHEMISTRY_LEVEL,
                            "style": DEFAULT_RESPONSE_STYLE
                        }
                    )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
                if st.session_state.user_id:
                    save_chat_event(
                        st.session_state.user_id,
                        role="assistant",
                        content=ai_response,
                    )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        st.session_state.chat_draft_input = ""
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
