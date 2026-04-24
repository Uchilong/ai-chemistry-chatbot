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
    page_title="🧪 Gia Sư Hóa Học AI",
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
        "❌ **Không Có Mô Hình AI Nào**\n\n"
        "Vui lòng cấu hình ít nhất một API:\n"
        "- **Gemini**: https://aistudio.google.com/app/apikey\n"
        "- **Mistral**: https://console.mistral.ai/api-keys/\n\n"
        "Thêm chúng vào tệp `.env` với tên `GEMINI_API_KEY` và `MISTRAL_API_KEY`"
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
    st.title("🧪 Hóa Học AI")
    
    # Model Selection
    st.markdown("---")
    st.subheader("🤖 Chọn Mô Hình AI")
    
    cols = st.columns([0.8, 0.2])
    with cols[0]:
        selected = st.radio(
            "Mô hình:",
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
    st.subheader("👤 Tài Khoản")
    if not st.session_state.user_id:
        email_input = st.text_input(
            "Đăng nhập bằng Gmail",
            placeholder="tenban@gmail.com",
            key="login_email_input"
        )
        if st.button("Đăng Nhập", use_container_width=True):
            if email_input and "@" in email_input:
                user_id = get_or_create_user(email_input)
                st.session_state.user_id = user_id
                st.session_state.user_email = email_input.strip().lower()
                st.session_state.messages = load_chat_events(user_id)
                st.session_state.history = load_questions(user_id)
                st.session_state.learning_resources = load_learning_resources(user_id)
                st.success("Đăng nhập thành công và đã tải tiến trình.")
                st.rerun()
            else:
                st.error("Vui lòng nhập email hợp lệ.")
    else:
        st.caption(f"Đã đăng nhập: {st.session_state.user_email}")
        if st.button("Đăng Xuất", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_email = ""
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.learning_resources = []
            st.rerun()
    
    # Chat Management
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Chat Mới", use_container_width=True):
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()
    with col2:
        st.link_button(
            "⌨️ ChemKey",
            "https://educat.ninja/chemkey/",
            use_container_width=True,
            help="Mở bàn phím ký hiệu hóa học trực tuyến trong tab mới"
        )
    st.link_button(
        "🧮 Máy Tính Khoa Học",
        "https://mathda.com/calculator/vi",
        use_container_width=True,
        help="Mở máy tính khoa học ngoài (MathDA)"
    )

    st.markdown("---")

    with st.expander("📚 Tài Liệu Học Tập", expanded=False):
        if st.session_state.user_id:
            title = st.text_input("Tiêu đề", key="resource_title")
            link = st.text_input("Đường dẫn", key="resource_link", placeholder="https://...")
            notes = st.text_area("Ghi chú (tuỳ chọn)", key="resource_notes", height=80)
            if st.button("Lưu Tài Liệu", use_container_width=True):
                if title.strip() and link.strip():
                    add_learning_resource(st.session_state.user_id, title, link, notes)
                    st.session_state.learning_resources = load_learning_resources(st.session_state.user_id)
                    st.success("Đã lưu tài liệu.")
                    st.rerun()
                else:
                    st.error("Tiêu đề và đường dẫn là bắt buộc.")

            if st.session_state.learning_resources:
                for resource in st.session_state.learning_resources:
                    st.markdown(f"**{resource['title']}**")
                    st.markdown(f"[{resource['link']}]({resource['link']})")
                    if resource["notes"]:
                        st.caption(resource["notes"])
                    if st.button("Xoá", key=f"del_res_{resource['id']}", use_container_width=True):
                        delete_learning_resource(st.session_state.user_id, resource["id"])
                        st.session_state.learning_resources = load_learning_resources(st.session_state.user_id)
                        st.rerun()
                    st.markdown("---")
            else:
                st.info("Chưa có tài liệu nào được lưu.")
        else:
            st.info("Đăng nhập để lưu tài liệu học tập.")
    
    # Chat History
    with st.expander("🕰️ Lịch Sử Câu Hỏi", expanded=False):
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
            st.info("Chưa có lịch sử nào")

# ============================================================================
# 5. MAIN CHAT DISPLAY
# ============================================================================
st.markdown(
    f"""
    <div class="app-header">
        <h1>{APP_ICON} Hóa Học AI</h1>
        <p>{st.session_state.selected_model}</p>
    </div>
    """,
    unsafe_allow_html=True
)

quick_prompt = None

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
    with st.popover("📎 Tải lên"):
        st.markdown("### 📤 Tải Lên Tệp")
        uploaded_file = st.file_uploader(
            FILE_UPLOAD_LABEL,
            type=SUPPORTED_FILE_TYPES,
            help=FILE_UPLOAD_HELP,
            label_visibility="collapsed"
        )
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            st.caption(f"Kích thước: {uploaded_file.size / 1024:.1f} KB")

# Chat input
with col_chat:
    st.text_area(
        "Tin nhắn",
        key="chat_draft_input",
        height=90,
        label_visibility="collapsed",
        placeholder=CHAT_INPUT_PLACEHOLDER
    )
    send_col, clear_col = st.columns([0.8, 0.2])
    with send_col:
        send_clicked = st.button("Gửi", key="send_draft_btn", use_container_width=True)
    with clear_col:
        if st.button("Xoá", key="clear_draft_btn", use_container_width=True):
            st.session_state.chat_draft_input = ""
    prompt = st.session_state.chat_draft_input.strip() if send_clicked else None

if quick_prompt:
    prompt = quick_prompt

# ============================================================================
# 7. MESSAGE PROCESSING & RESPONSE
# ============================================================================
if prompt:
    if not brain:
        st.error(f"❌ {st.session_state.selected_model} không khả dụng")
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
        with st.spinner(f"🤖 {st.session_state.selected_model} đang xử lý..."):
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
                        ai_response = "⚠️ Phân tích tệp yêu cầu Gemini hoặc Mistral API"
                    
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
                st.error(f"❌ Lỗi: {str(e)}")
        
        st.session_state.chat_draft_input = ""
        st.rerun()

# ============================================================================
# 8. INFO & FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
    <small>
    🧪 Gia Sư Hóa Học AI | Hỗ Trợ Đa Mô Hình | Học Tập Nhanh & Chính Xác
    </small>
    </div>
    """, unsafe_allow_html=True)