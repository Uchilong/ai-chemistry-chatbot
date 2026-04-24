import os
from typing import Optional, Dict
from pathlib import Path
from chemistry_tools import build_solver_hints
from chemistry_kb import retrieve_snippets

try:
    from groq import Groq
except ImportError:
    Groq = None

# PyPDF2 is an optional dependency for PDF processing.
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Import config for API key and settings
try:
    from config import GROQ_API_KEY, GROQ_MODEL
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "mixtral-8x7b-32768"  # Free model, ultra-fast

# Try to import vision tool for pix2text OCR
try:
    import sys
    from pathlib import Path as PathlibPath
    backend_path = str(PathlibPath(__file__).parent.parent / "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from tools.vision_tool import VisionTool
    VISION_TOOL_AVAILABLE = True
except ImportError:
    VISION_TOOL_AVAILABLE = False
    print("Warning: Vision tool (pix2text) not available. Image analysis may be limited.")


class GroqChemistryBrain:
    """Backend brain for AI Chemistry Chatbot using Groq API - Lightning-Fast Mode."""

    def __init__(self, api_key: Optional[str] = None, model: str = "mixtral-8x7b-32768"):
        """
        Initialize the Groq Chemistry AI Brain.

        Args:
            api_key: Groq API key. If None, will try to load from GROQ_API_KEY env variable.
            model: Model to use (default: mixtral-8x7b-32768 - free & fastest)
        """
        if Groq is None:
            raise ImportError("groq package not installed. Install with: pip install groq")
        
        self.api_key = api_key or GROQ_API_KEY

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not provided. Please set it as an environment variable "
                "or pass it to the constructor. "
                "Get your free key at: https://console.groq.com/keys"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model

        self.system_prompt = """You are an expert Chemistry AI tutor specializing in helping students learn chemistry with SPEED and ACCURACY.
Your responsibilities:
- Explain chemistry concepts clearly and concisely
- Solve chemistry problems step-by-step with detailed working
- Provide molecular structure analysis and predictions
- Explain chemical reactions and their mechanisms
- Help with homework and practice problems
- Provide real-world applications of chemistry concepts
- Use Vietnamese language when interacting with Vietnamese-speaking students

Always:
- Be ACCURATE and SCIENTIFICALLY CORRECT
- Provide concise, focused answers
- Think through complex problems methodically
- Show all working in calculations
- Use examples when helpful
- Organize your responses clearly with headings and bullet points when appropriate
- When uncertain, explain your reasoning and limitations"""
        
        # Vision tool initialized lazily to avoid startup delays
        self._vision_tool = None
        self._vision_tool_initialized = False

    def _get_vision_tool(self):
        """Get vision tool, initializing lazily only when needed."""
        if not self._vision_tool_initialized:
            self._vision_tool_initialized = True
            if VISION_TOOL_AVAILABLE:
                try:
                    self._vision_tool = VisionTool()
                except Exception as e:
                    print(f"Warning: Could not initialize vision tool: {e}")
                    self._vision_tool = None
        return self._vision_tool
    
    @property
    def vision_tool(self):
        """Lazy property for vision tool."""
        return self._get_vision_tool()

    def _build_context_instruction(
        self,
        user_message: str,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        context = chemistry_context or {}
        level = context.get("level", "undergrad")
        style = context.get("style", "balanced")
        hints = build_solver_hints(user_message)
        snippets = retrieve_snippets(user_message, top_k=2)

        level_map = {
            "highschool": "Use high-school level explanations.",
            "undergrad": "Use undergraduate-level chemistry depth.",
            "mixed": "Provide layered explanation from intuitive to technical."
        }
        style_map = {
            "concise": "Be concise while preserving equations and units.",
            "balanced": "Balance detail and speed.",
            "detailed": "Show full derivation and checks."
        }
        citation_hint = "Cite reference snippets as [ref:id] when using retrieved knowledge."

        lines = [
            "Chemistry response contract:",
            "Use this exact markdown section order:",
            "## Given",
            "## Formula/Equation",
            "## Steps",
            "## Final Answer (with units)",
            "## Quick Check",
            "## References",
            "## Confidence",
            "Rules: balance reactions, include units in all numeric steps, and enforce sig figs.",
            f"Audience level: {level}. {level_map.get(level, level_map['undergrad'])}",
            f"Style: {style}. {style_map.get(style, style_map['balanced'])}",
            citation_hint,
            "Deterministic hints:",
            *[f"- {h}" for h in hints],
        ]
        if snippets:
            lines.append("Retrieved references:")
            for s in snippets:
                lines.append(f"- [ref:{s['id']}] {s['content']} (source: {s['source']})")
        return "\n".join(lines)

    @staticmethod
    def _format_error(prefix: str, error: Exception) -> str:
        error_msg = str(error)
        return f"{prefix}: {error_msg}"

    def chat(
        self,
        user_message: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Send a message and get AI response - ultra-fast with Groq.

        Args:
            user_message: The user's question or message
            chat_history: Previous messages for context
            chemistry_context: Chemistry level and style context

        Returns:
            AI's response text
        """
        try:
            # Build context instruction
            context_instruction = self._build_context_instruction(user_message, chemistry_context)
            
            # Prepare messages for Groq
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": context_instruction}
            ]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-10:]:  # Limit to last 10 messages
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        if msg["role"] in ["user", "assistant"]:
                            messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from Groq - lightning fast!
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                timeout=30.0  # 30 second timeout
            )
            
            return completion.choices[0].message.content
        
        except Exception as e:
            return self._format_error("Error processing your question", e)

    def chat_with_image(
        self,
        user_message: str,
        image_path: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Handle image analysis using pix2text (SimplePix2Text) OCR to extract content,
        then process as text through Groq.

        Args:
            user_message: The user's question about the image
            image_path: Path to the image file
            chat_history: Previous messages for context

        Returns:
            Response text (text extraction results or fallback message)
        """
        try:
            if not Path(image_path).exists():
                return f"Error: Image file not found at {image_path}"
            
            # Extract text from image using pix2text (SimplePix2Text)
            vision_tool = self.vision_tool
            if vision_tool:
                try:
                    # Try extraction - fail gracefully if it times out
                    ocr_result = vision_tool.extract_from_image(image_path)
                    if ocr_result and ocr_result.success:
                        # Build message with extracted content
                        extracted_content = f"""📋 **Text/Equations Extracted from Image (pix2text):**
- Extracted Text: {ocr_result.extracted_text}
- Equations Found: {', '.join(ocr_result.equations) if ocr_result.equations else 'None'}
- Chemical Formulas: {', '.join(ocr_result.chemical_formulas) if ocr_result.chemical_formulas else 'None'}
- Confidence: {ocr_result.confidence:.1%}

User Question: {user_message}"""
                        
                        # Process extracted text through Groq
                        return self.chat(extracted_content, chat_history, chemistry_context)
                    elif ocr_result:
                        return f"⚠️ Image text extraction note: {ocr_result.error_message}\n\nPlease describe what you see in the image for analysis."
                    else:
                        return "⚠️ Image extraction unavailable. Please describe the image content in text format."
                except TimeoutError:
                    print("⚠️  pix2text extraction timeout")
                    return "⚠️ Image analysis took too long. Please describe the image content in text format."
                except Exception as e:
                    print(f"⚠️  pix2text extraction error: {str(e)}")
                    return "⚠️ Image analysis encountered an error. Please describe the image content in text format."
            else:
                return "⚠️ Image analysis is currently unavailable. Please describe the image content in text format."
        
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def chat_with_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Handle file input — images are processed with OCR; text/PDF content is extracted and sent as text.

        Args:
            user_message: The user's question about the file
            file_path: Path to the file
            chat_history: Previous messages for context

        Returns:
            AI's response text
        """
        if not Path(file_path).exists():
            return f"Error: File not found at {file_path}"

        file_ext = Path(file_path).suffix.lower()

        if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return self.chat_with_image(user_message, file_path, chat_history, chemistry_context)

        elif file_ext == ".txt":
            return self._handle_text_file(user_message, file_path, chat_history, chemistry_context)

        elif file_ext == ".pdf":
            return self._handle_pdf_file(user_message, file_path, chat_history, chemistry_context)

        else:
            return f"Error: Unsupported file type {file_ext}. Supported: jpg, png, gif, webp, txt, pdf"

    def _handle_text_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """Handle text file analysis."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if len(content) > 8000:
                content = content[:8000] + "\n\n[Content truncated for length...]"

            enhanced_message = f"I'm sharing a text file '{Path(file_path).name}' for analysis.\n\nFile content:\n---\n{content}\n---\n\n{user_message}"

            return self.chat(enhanced_message, chat_history, chemistry_context)
        
        except Exception as e:
            return self._format_error("Error processing text file", e)

    def _handle_pdf_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """Handle PDF file analysis."""
        try:
            if PyPDF2 is None:
                return "⚠️ PDF processing requires PyPDF2. Please install it with: pip install PyPDF2"

            text_content = ""
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(min(len(pdf_reader.pages), 5)):  # Limit to 5 pages
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text()

            if len(text_content) > 8000:
                text_content = text_content[:8000] + "\n\n[Content truncated for length...]"

            enhanced_message = f"I'm sharing a PDF file '{Path(file_path).name}' for analysis.\n\nFile content:\n---\n{text_content}\n---\n\n{user_message}"

            return self.chat(enhanced_message, chat_history, chemistry_context)
        
        except Exception as e:
            return self._format_error("Error processing PDF file", e)


def get_groq_brain(api_key: Optional[str] = None) -> Optional[GroqChemistryBrain]:
    """
    Get or create a Groq Chemistry AI Brain instance.
    
    Args:
        api_key: Optional API key (uses GROQ_API_KEY env var if not provided)
    
    Returns:
        GroqChemistryBrain instance or None if initialization fails
    """
    try:
        return GroqChemistryBrain(api_key=api_key)
    except ValueError as e:
        print(f"⚠️  Groq initialization skipped: {e}")
        return None
    except Exception as e:
        print(f"Error initializing Groq: {e}")
        return None
