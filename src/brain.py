import os
import base64
from typing import Optional, List, Union
import google.generativeai as genai
from pathlib import Path

# Import config for API key and settings
try:
    from config import GEMINI_API_KEY, MODEL_NAME
except ImportError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME = "gemini-2.0-flash"


class ChemistryAIBrain:
    """Backend brain for AI Chemistry Chatbot using Google Gemini API - Accurate Thinking Mode."""
    
    def __init__(self, api_key: Optional[str] = None, thinking_mode: bool = True):
        """
        Initialize the Chemistry AI Brain.
        
        Args:
            api_key: Google Gemini API key. If None, will try to load from GEMINI_API_KEY env variable.
            thinking_mode: Enable extended thinking for more accurate responses.
        """
        self.api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not provided. Please set it as an environment variable "
                "or pass it to the constructor. "
                "Get your key at: https://aistudio.google.com/app/apikey"
            )
        
        genai.configure(api_key=self.api_key)
        self.thinking_mode = thinking_mode
        self.model = genai.GenerativeModel(MODEL_NAME)
        
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

    def chat(self, user_message: str, chat_history: Optional[list] = None) -> str:
        """
        Send a text message and get AI response.
        
        Args:
            user_message: The user's chemistry question or message
            chat_history: Previous messages for context (list of dicts with 'role' and 'content')
        
        Returns:
            AI's response text
        """
        try:
            # Build conversation history for context
            conversation = [
                {"role": "user", "parts": [self.system_prompt]},
                {"role": "model", "parts": ["I understand. I'm ready to help you learn chemistry!"]}
            ]
            
            # Add previous messages if provided
            if chat_history:
                for msg in chat_history:
                    role = "user" if msg.get("role") == "user" else "model"
                    parts = [msg.get("content", "")]
                    conversation.append({"role": role, "parts": parts})
            
            # Add current message
            conversation.append({"role": "user", "parts": [user_message]})
            
            # Get response from Gemini
            response = self.model.generate_content(
                [{"text": self.system_prompt + "\n\nUser: " + user_message}]
            )
            
            return response.text
        
        except Exception as e:
            return f"Error processing your question: {str(e)}"

    def chat_with_image(
        self, 
        user_message: str, 
        image_path: str, 
        chat_history: Optional[list] = None
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
            
            # Read and encode image
            with open(image_path, "rb") as img_file:
                image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
            
            # Determine image type
            file_ext = Path(image_path).suffix.lower()
            mime_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }
            mime_type = mime_type_map.get(file_ext, "image/jpeg")
            
            # Build prompt with image context
            full_prompt = f"{self.system_prompt}\n\nUser Question: {user_message}"
            
            # Send to Gemini with image
            response = self.model.generate_content(
                [
                    full_prompt,
                    {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                ]
            )
            
            return response.text
        
        except Exception as e:
            return f"Error processing image: {str(e)}"

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
        chat_history: Optional[list] = None
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
                return self.chat_with_image(user_message, file_path, chat_history)
            
            # Handle text files
            elif file_ext in [".txt"]:
                return self._handle_text_file(user_message, file_path, chat_history)
            
            # Handle PDF files
            elif file_ext == ".pdf":
                return self._handle_pdf_file(user_message, file_path, chat_history)
            
            else:
                return f"Error: Unsupported file type {file_ext}. Supported: jpg, png, gif, webp, txt, pdf"
        
        except Exception as e:
            return f"Error processing file: {str(e)}"

    def _handle_text_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None
    ) -> str:
        """Handle text file analysis."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Limit content length
            if len(content) > 8000:
                content = content[:8000] + "\n\n[Content truncated for length...]"
            
            enhanced_message = f"I'm sharing a text file '{Path(file_path).name}' for analysis.\n\nFile content:\n---\n{content}\n---\n\n{user_message}"
            
            return self.chat(enhanced_message, chat_history)
        
        except Exception as e:
            return f"Error reading text file: {str(e)}"

    def _handle_pdf_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None
    ) -> str:
        """Handle PDF file analysis."""
        try:
            try:
                import PyPDF2
            except ImportError:
                return "Error: PyPDF2 not installed. Please install it to read PDF files: pip install PyPDF2"
            
            content = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                # Limit to first 20 pages
                page_count = min(len(reader.pages), 20)
                for i in range(page_count):
                    page = reader.pages[i]
                    content += page.extract_text() + "\n"
            
            # Limit content length
            if len(content) > 8000:
                content = content[:8000] + "\n\n[PDF content truncated for length...]"
            
            enhanced_message = f"I'm sharing a PDF file '{Path(file_path).name}' (first {page_count} pages) for analysis.\n\nPDF content:\n---\n{content}\n---\n\n{user_message}"
            
            return self.chat(enhanced_message, chat_history)
        
        except Exception as e:
            return f"Error reading PDF file: {str(e)}"


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

