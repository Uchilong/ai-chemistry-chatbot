import os
from typing import Optional, Dict
import google.generativeai as genai
from pathlib import Path
from PIL import Image
from chemistry_tools import build_solver_hints
from chemistry_kb import retrieve_snippets

# Import config for API key and settings
try:
    from config import GEMINI_API_KEY, MODEL_NAME
except ImportError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME = "gemini-2.0-flash"

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


class ChemistryAIBrain:
    """Backend brain for AI Chemistry Chatbot using Google Gemini API - Accurate Thinking Mode."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Chemistry AI Brain.
        
        Args:
            api_key: Google Gemini API key. If None, will try to load from GEMINI_API_KEY env variable.
        """
        self.api_key = api_key or GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not provided. Please set it as an environment variable "
                "or pass it to the constructor. "
                "Get your key at: https://aistudio.google.com/app/apikey"
            )
        
        genai.configure(api_key=self.api_key)
        
        self.system_prompt = """You are an intelligent Chemistry AI Router and Orchestrator for a high school chemistry tutoring system. Your primary role is to analyze student questions and intelligently delegate to specialized chemistry tools, then synthesize their outputs into coherent educational responses.

## Available Tools
- **pubchem_tool**: Fetches chemical properties, molar mass, structural information
- **wolfram_tool**: Balances equations, performs calculations, solves math problems
- **vision_tool**: Extracts text/equations from images using OCR (pix2text/Gemini Vision)
- **media_tool**: Generates educational images and audio content

## Your Workflow
1. **Analyze** the student's question to identify required tools
2. **Select** appropriate tools based on question type
3. **Orchestrate** tool calls in optimal sequence
4. **Synthesize** tool outputs into educational response
5. **Explain** results at high school level

## Tool Selection Logic
- Chemical properties/structures → pubchem_tool
- Equation balancing/calculations → wolfram_tool  
- Image analysis/diagrams → vision_tool
- Visual explanations needed → media_tool
- Complex problems → Multiple tools in sequence

## Response Format
Always structure responses with:
## Question Understanding
## Tools Used
## Step-by-Step Solution
## Key Concepts
## Practice Problem
## Summary

## Educational Approach (High School Focus)
- **Language**: Use Vietnamese when interacting with Vietnamese-speaking students
- **Vocabulary**: Maintain high school level - avoid quantum mechanics, advanced thermodynamics
- **Real-world connections**: Link concepts to everyday life (cooking, cleaning, environment)
- **Scaffolding**: Build from simple to complex, use analogies and examples
- **Confidence levels**: Indicate certainty for complex problems (High/Medium/Low)
- **Follow-up activities**: Suggest experiments, practice problems, or further reading

## High School Teaching Strategies
- **Conceptual first**: Explain "why" before "how"
- **Visual learning**: Use step-by-step breakdowns with clear formatting
- **Common misconceptions**: Address typical student errors explicitly
- **Study tips**: Include memory aids and learning strategies
- **Assessment prep**: Connect to exam formats and question types

## Response Structure for High School
1. **Hook**: Relatable example or question to engage interest
2. **Core concept**: Clear definition with simple explanation  
3. **Step-by-step**: Worked examples with reasoning
4. **Common mistakes**: What to avoid and why
5. **Practice**: Similar problem for student to try
6. **Connection**: Real-world application or career link

## Error Handling
If tools fail, provide conceptual explanations and suggest alternative approaches. Always prioritize educational value over perfect technical accuracy. Never leave a student without a learning path."""

        self.model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=self.system_prompt
        )
        
        # Vision tool initialized lazily to avoid startup delays
        self._vision_tool = None
        self._vision_tool_initialized = False

    def _get_vision_tool(self):
        """Get vision tool, initializing lazily only when needed."""
        if not self._vision_tool_initialized:
            self._vision_tool_initialized = True
            if VISION_TOOL_AVAILABLE:
                try:
                    self._vision_tool = VisionTool(gemini_api_key=self.api_key)
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
        """Build tool orchestration context for each question."""
        context = chemistry_context or {}
        level = context.get("level", "highschool")
        style = context.get("style", "balanced")
        hints = build_solver_hints(user_message)
        snippets = retrieve_snippets(user_message, top_k=2)

        # Tool-specific instructions based on question analysis
        tool_instructions = self._analyze_and_select_tools(user_message)
        
        # Educational level mapping for high school focus
        level_map = {
            "highschool": "Use high-school level vocabulary. Avoid quantum mechanics. Focus on conceptual understanding.",
            "undergrad": "Use undergraduate-level depth with mechanisms and thermodynamics.",
            "mixed": "Provide layered explanation from intuitive to technical."
        }
        
        # Response style for educational effectiveness
        style_map = {
            "concise": "Direct answers with key equations and units.",
            "balanced": "Mix of explanation and step-by-step solutions.",
            "detailed": "Full derivations with concept connections."
        }

        snippet_lines = []
        for s in snippets:
            snippet_lines.append(f"- [{s['id']}] {s['content']} (source: {s['source']})")

        parts = [
            "## TOOL ORCHESTRATION INSTRUCTIONS",
            tool_instructions,
            "",
            "## EDUCATIONAL CONTEXT",
            f"Level: {level}. {level_map.get(level, level_map['highschool'])}",
            f"Style: {style}. {style_map.get(style, style_map['balanced'])}",
            "",
            "## CHEMISTRY HINTS",
            *[f"- {h}" for h in hints],
        ]
        
        if snippet_lines:
            parts.extend(["", "## KNOWLEDGE REFERENCES", *snippet_lines])
            
        return "\n".join(parts)

    def _analyze_and_select_tools(self, user_message: str) -> str:
        """Analyze question and determine which tools to use."""
        message_lower = user_message.lower()
        
        # Tool selection logic
        tools_needed = []
        
        # PubChem tool triggers
        if any(keyword in message_lower for keyword in ['molar mass', 'properties', 'structure', 'formula', 'element', 'compound']):
            tools_needed.append("pubchem_tool: Get chemical properties and structural data")
            
        # Wolfram tool triggers  
        if any(keyword in message_lower for keyword in ['balance', 'calculate', 'equation', 'math', 'solve', 'stoichiometry']):
            tools_needed.append("wolfram_tool: Balance equations and perform calculations")
            
        # Vision tool triggers
        if any(keyword in message_lower for keyword in ['image', 'diagram', 'picture', 'photo', 'ocr', 'read']):
            tools_needed.append("vision_tool: Extract text/equations from images")
            
        # Media tool triggers
        if any(keyword in message_lower for keyword in ['visualize', 'show', 'image', 'diagram', 'audio']):
            tools_needed.append("media_tool: Generate educational visuals/audio")
        
        if not tools_needed:
            tools_needed.append("Direct explanation: Use general chemistry knowledge")
            
        return "Tools to use:\n" + "\n".join(f"- {tool}" for tool in tools_needed)

    @staticmethod
    def _format_error(prefix: str, error: Exception) -> str:
        """Return a user-friendly API error message."""
        message = str(error)
        lowered = message.lower()
        if "401" in message or "unauthorized" in lowered:
            return (
                "Error: Unauthorized API request (401). "
                "Please check that `GEMINI_API_KEY` is set correctly and still valid."
            )
        return f"{prefix}: {message}"

    def _handle_tool_failure(self, tool_name: str, error: Exception, fallback_context: str) -> str:
        """Handle tool failures with educational fallbacks."""
        error_message = str(error).lower()
        
        # Provide educational fallback based on tool type
        if "pubchem" in tool_name.lower():
            return (
                f"⚠️ **PubChem Tool Unavailable**\n\n"
                f"Unable to fetch chemical data right now. "
                f"Here's what I can tell you from general chemistry knowledge:\n\n"
                f"{fallback_context}\n\n"
                f"💡 **Tip**: You can look up chemical properties using reliable sources like "
                f"PubChem directly or your chemistry textbook."
            )
        
        elif "wolfram" in tool_name.lower():
            return (
                f"⚠️ **Calculation Tool Unavailable**\n\n"
                f"Unable to perform calculations right now. "
                f"Let me guide you through the manual approach:\n\n"
                f"{fallback_context}\n\n"
                f"📝 **Manual Steps**: Show your work step-by-step using the formulas we've learned."
            )
        
        elif "vision" in tool_name.lower():
            return (
                f"⚠️ **Image Analysis Unavailable**\n\n"
                f"Cannot process images at the moment. "
                f"Please describe what you see in the image, and I'll help you analyze it.\n\n"
                f"📷 **Alternative**: You can type out equations or describe diagrams verbally."
            )
        
        elif "media" in tool_name.lower():
            return (
                f"⚠️ **Media Generation Unavailable**\n\n"
                f"Cannot generate visuals right now. "
                f"Let me explain the concept using text:\n\n"
                f"{fallback_context}\n\n"
                f"🎨 **Visualization Tip**: Try drawing the concept yourself based on the description."
            )
        
        else:
            return (
                f"⚠️ **Tool Unavailable**\n\n"
                f"Experiencing technical difficulties. "
                f"Here's a conceptual explanation:\n\n"
                f"{fallback_context}\n\n"
                f"🔄 **Try Again**: The issue might be temporary. Please retry in a moment."
            )

    def chat(
        self,
        user_message: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Send a text message and get AI response.
        
        Args:
            user_message: The user's chemistry question or message
            chat_history: Previous messages for context (list of dicts with 'role' and 'content')
        
        Returns:
            AI's response text
        """
        try:
            # Start a new chat session and build history
            chat_session = self.model.start_chat(history=[])
            
            if chat_history:
                # The genai library expects a flat list of contents, not role-based dicts
                # We need to adapt our history format.
                history_for_api = []
                for msg in chat_history:
                    role = msg.get("role", "user")
                    # Gemini chat history expects `user` and `model` roles.
                    if role == "assistant":
                        role = "model"
                    elif role not in {"user", "model"}:
                        role = "user"
                    history_for_api.append({"role": role, "parts": [msg.get("content", "")]})
                chat_session.history = history_for_api

            context_instruction = self._build_context_instruction(user_message, chemistry_context)
            enhanced_message = f"{context_instruction}\n\nUser question:\n{user_message}"

            # Get response from Gemini
            response = chat_session.send_message(enhanced_message)
            
            return response.text
        
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
        Send a message with an image and get AI response.
        First tries pix2text (SimplePix2Text) to extract text/equations from the image,
        then analyzes with Gemini. Gracefully handles extraction timeouts.
        
        Args:
            user_message: The user's question about the image
            image_path: Path to the image file
            chat_history: Previous messages for context
        
        Returns:
            AI's response text
        """
        try:
            if not Path(image_path).exists():
                return f"Error: Image file not found at {image_path}"
            
            # Extract text from image using pix2text (SimplePix2Text)
            # with fallback if extraction takes too long or fails
            extracted_content = ""
            vision_tool = self.vision_tool
            if vision_tool:
                try:
                    # Set a reasonable timeout for extraction
                    import signal
                    
                    def extraction_timeout_handler(signum, frame):
                        raise TimeoutError("Image extraction took too long")
                    
                    # Try extraction with timeout (skip on Windows where signal doesn't work for non-main thread)
                    try:
                        ocr_result = vision_tool.extract_from_image(image_path)
                    except TimeoutError:
                        print("⚠️  pix2text extraction timeout - using Gemini analysis only")
                        ocr_result = None
                    
                    if ocr_result and ocr_result.success:
                        extracted_content = f"""📋 **Text/Equations Extracted from Image:**
- Extracted Text: {ocr_result.extracted_text}
- Equations Found: {', '.join(ocr_result.equations) if ocr_result.equations else 'None'}
- Chemical Formulas: {', '.join(ocr_result.chemical_formulas) if ocr_result.chemical_formulas else 'None'}
- Confidence: {ocr_result.confidence:.1%}

"""
                    elif ocr_result and not ocr_result.success:
                        print(f"⚠️  pix2text extraction note: {ocr_result.error_message}")
                except Exception as e:
                    # Fail gracefully - just proceed with Gemini analysis
                    print(f"⚠️  pix2text extraction error (using Gemini only): {str(e)}")
            
            # Load the image for Gemini analysis
            img = Image.open(image_path)
            
            # Build context instruction with extraction info
            context_instruction = self._build_context_instruction(
                f"{extracted_content}\n{user_message}" if extracted_content else user_message, 
                chemistry_context
            )
            
            # Send to Gemini with extracted content and image
            response = self.model.generate_content([
                context_instruction, 
                f"{extracted_content}\n{user_message}" if extracted_content else user_message, 
                img
            ])
            
            return response.text
        
        except Exception as e:
            return self._format_error("Error processing image", e)

    def analyze_chemistry_concept(self, concept: str) -> str:
        """
        Get a detailed explanation of a chemistry concept.
        
        Args:
            concept: The chemistry concept to explain
        
        Returns:
            Detailed explanation
        """
        prompt = f"""Please provide a comprehensive explanation of the chemistry concept: "{concept}"

Include:
1. Definition
2. Key characteristics
3. Real-world applications
4. Examples
5. Related concepts
6. Common misconceptions (if any)"""
        
        return self.chat(prompt)

    def solve_problem(self, problem: str) -> str:
        """
        Solve a chemistry problem step-by-step.
        
        Args:
            problem: The chemistry problem to solve
        
        Returns:
            Step-by-step solution
        """
        prompt = f"""Please solve this chemistry problem step-by-step:

{problem}

Format your answer with:
1. Given information
2. What we need to find
3. Relevant formulas/equations
4. Step-by-step calculation
5. Final answer with units
6. Brief explanation of the result"""
        
        return self.chat(prompt)

    def get_molecule_info(self, molecule_name: str) -> str:
        """
        Get information about a molecule.
        
        Args:
            molecule_name: Name of the molecule
        
        Returns:
            Detailed molecule information
        """
        prompt = f"""Provide detailed information about {molecule_name}:

1. Chemical formula
2. Molecular structure (description)
3. Molar mass
4. Uses and applications
5. Safety information
6. Interesting facts"""
        
        return self.chat(prompt)

    def chat_with_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Send a message with a file (image, PDF, or text) and get AI response.
        
        Args:
            user_message: The user's question about the file
            file_path: Path to the file (image or text)
            chat_history: Previous messages for context
        
        Returns:
            AI's response text
        """
        try:
            if not Path(file_path).exists():
                return f"Error: File not found at {file_path}"
            
            file_ext = Path(file_path).suffix.lower()
            
            # Handle images
            if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                return self.chat_with_image(user_message, file_path, chat_history, chemistry_context)
            
            # Handle text files
            elif file_ext in [".txt"]:
                return self._handle_text_file(user_message, file_path, chat_history, chemistry_context)
            
            # Handle PDF files
            elif file_ext == ".pdf":
                return self._handle_pdf_file(user_message, file_path, chat_history, chemistry_context)
            
            else:
                return f"Error: Unsupported file type {file_ext}. Supported: jpg, png, gif, webp, txt, pdf"
        
        except Exception as e:
            return self._format_error("Error processing file", e)

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
            
            # Limit content length
            if len(content) > 8000:
                content = content[:8000] + "\n\n[Content truncated for length...]"
            
            enhanced_message = f"I'm sharing a text file '{Path(file_path).name}' for analysis.\n\nFile content:\n---\n{content}\n---\n\n{user_message}"
            
            return self.chat(enhanced_message, chat_history, chemistry_context)
        
        except Exception as e:
            return self._format_error("Error reading text file", e)

    def _handle_pdf_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """Handle PDF file analysis."""
        # Use Gemini's native file processing API for better results
        try:
            print(f"Uploading file to Gemini: {file_path}")
            # Upload the file and get a file handle
            pdf_file = genai.upload_file(path=file_path, display_name=Path(file_path).name)
            print(f"File uploaded successfully: {pdf_file.name}")

            # Create a prompt that includes the file
            context_instruction = self._build_context_instruction(user_message, chemistry_context)
            prompt = [
                context_instruction,
                f"The user has uploaded the file '{pdf_file.display_name}'. Please analyze it and answer the following question.",
                pdf_file,
                user_message
            ]

            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return self._format_error("Error processing PDF file with Gemini API", e)


# Initialize and cache the brain instance
_brain_instance = None


def get_brain(api_key: Optional[str] = None) -> ChemistryAIBrain:
    """
    Get or create the Chemistry AI Brain instance (singleton pattern).
    
    Args:
        api_key: Google Gemini API key (optional)
    
    Returns:
        ChemistryAIBrain instance
    """
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = ChemistryAIBrain(api_key=api_key)
    return _brain_instance
