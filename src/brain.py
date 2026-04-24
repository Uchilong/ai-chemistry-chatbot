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
        
        self.system_prompt = """You are an expert Chemistry AI tutor specializing in helping students learn chemistry with ACCURACY and DEPTH.
Your responsibilities:
- Explain chemistry concepts clearly and comprehensively
- Solve chemistry problems step-by-step with detailed working
- Provide molecular structure analysis and predictions
- Explain chemical reactions and their mechanisms
- Help with homework and practice problems
- Provide real-world applications of chemistry concepts
- Analyze images, diagrams, and uploaded documents
- Use Vietnamese language when interacting with Vietnamese-speaking students

Always:
- Be ACCURATE and SCIENTIFICALLY CORRECT above all else
- Think through complex problems methodically
- Show all working in calculations
- Use examples when helpful
- If you see an image/diagram, analyze it carefully and explain what you observe
- Organize your responses clearly with headings and bullet points when appropriate
- When uncertain, explain your reasoning and limitations"""

        self.model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=self.system_prompt
        )

    def _build_context_instruction(
        self,
        user_message: str,
        chemistry_context: Optional[Dict[str, str]] = None
    ) -> str:
        """Build specialization context that is prepended to each question."""
        context = chemistry_context or {}
        level = context.get("level", "undergrad")
        style = context.get("style", "balanced")
        hints = build_solver_hints(user_message)
        snippets = retrieve_snippets(user_message, top_k=2)

        task_contract = (
            "Follow this chemistry response contract strictly:\n"
            "1) Identify task type and list givens.\n"
            "2) Show balanced equation when relevant.\n"
            "3) Show formulas used and unit-aware calculations.\n"
            "4) Validate units and significant figures.\n"
            "5) Provide a concise final answer section.\n"
        )
        level_map = {
            "highschool": "Use high-school level vocabulary and avoid advanced quantum detail.",
            "undergrad": "Use undergraduate-level depth and include mechanism/thermo nuance when relevant.",
            "mixed": "Adapt depth dynamically and provide both intuitive and technical explanation."
        }
        style_map = {
            "concise": "Keep answer short but still include required equations and units.",
            "balanced": "Balance brevity and depth.",
            "detailed": "Provide full derivation and explain each step."
        }

        snippet_lines = []
        for s in snippets:
            snippet_lines.append(f"- [{s['id']}] {s['content']} (source: {s['source']})")

        parts = [
            task_contract,
            f"Audience level: {level}. {level_map.get(level, level_map['undergrad'])}",
            f"Answer style: {style}. {style_map.get(style, style_map['balanced'])}",
            "Deterministic chemistry hints:",
            *[f"- {h}" for h in hints],
        ]
        if snippet_lines:
            parts.extend(["Retrieved chemistry references:", *snippet_lines])
        return "\n".join(parts)

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
            
            # The library can handle PIL images directly
            img = Image.open(image_path)
            
            # Send to Gemini with image
            # The system prompt is already part of the model configuration
            # We can send the user message and image as a list of parts
            context_instruction = self._build_context_instruction(user_message, chemistry_context)
            response = self.model.generate_content([context_instruction, user_message, img])
            
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
