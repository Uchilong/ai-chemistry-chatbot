import os
from typing import Optional
from mistralai import Mistral

# Import config for API key and settings
try:
    from config import MISTRAL_API_KEY, MISTRAL_MODEL
except ImportError:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = "mistral-large-latest"


class MistralChemistryBrain:
    """Backend brain for AI Chemistry Chatbot using Mistral API - Fast Thinking Mode."""

    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large-latest"):
        """
        Initialize the Mistral Chemistry AI Brain.

        Args:
            api_key: Mistral API key. If None, will try to load from MISTRAL_API_KEY env variable.
            model: Model to use (default: mistral-large-latest)
        """
        self.api_key = api_key or MISTRAL_API_KEY or os.getenv("MISTRAL_API_KEY")

        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not provided. Please set it as an environment variable "
                "or pass it to the constructor. "
                "Get your key at: https://console.mistral.ai/api-keys/"
            )

        self.client = Mistral(api_key=self.api_key)
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
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]

            # Add previous messages if provided
            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    messages.append({"role": role, "content": content})

            # Add current message
            messages.append({"role": "user", "content": user_message})

            # Get response from Mistral (v1.x API)
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error processing your question: {str(e)}"

    def chat_with_image(
        self,
        user_message: str,
        image_path: str,
        chat_history: Optional[list] = None
    ) -> str:
        """
        Mistral vision API is limited. Return a message about text-based use.

        Args:
            user_message: The user's question about the image
            image_path: Path to the image file
            chat_history: Previous messages for context

        Returns:
            Response about image limitation
        """
        return "⚠️ Image analysis is not supported with Mistral API in this version. Please use the Gemini API for image analysis, or describe the image in text."

    def chat_with_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None
    ) -> str:
        """
        Handle file input — images are unsupported; text/PDF content is extracted and sent as text.

        Args:
            user_message: The user's question about the file
            file_path: Path to the file
            chat_history: Previous messages for context

        Returns:
            AI's response text
        """
        from pathlib import Path

        if not Path(file_path).exists():
            return f"Error: File not found at {file_path}"

        file_ext = Path(file_path).suffix.lower()

        if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return self.chat_with_image(user_message, file_path, chat_history)

        elif file_ext == ".txt":
            return self._handle_text_file(user_message, file_path, chat_history)

        elif file_ext == ".pdf":
            return self._handle_pdf_file(user_message, file_path, chat_history)

        else:
            return f"Error: Unsupported file type {file_ext}. Supported: jpg, png, gif, webp, txt, pdf"

    def _handle_text_file(
        self,
        user_message: str,
        file_path: str,
        chat_history: Optional[list] = None
    ) -> str:
        """Handle text file analysis."""
        from pathlib import Path
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if len(content) > 8000:
                content = content[:8000] + "\n\n[Content truncated for length...]"

            enhanced_message = (
                f"I'm sharing a text file '{Path(file_path).name}' for analysis.\n\n"
                f"File content:\n---\n{content}\n---\n\n{user_message}"
            )

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
        from pathlib import Path
        try:
            try:
                import PyPDF2
            except ImportError:
                return "Error: PyPDF2 not installed. Run: pip install PyPDF2"

            content = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                page_count = min(len(reader.pages), 20)
                for i in range(page_count):
                    content += reader.pages[i].extract_text() + "\n"

            if len(content) > 8000:
                content = content[:8000] + "\n\n[PDF content truncated for length...]"

            enhanced_message = (
                f"I'm sharing a PDF file '{Path(file_path).name}' "
                f"(first {page_count} pages) for analysis.\n\n"
                f"PDF content:\n---\n{content}\n---\n\n{user_message}"
            )

            return self.chat(enhanced_message, chat_history)

        except Exception as e:
            return f"Error reading PDF file: {str(e)}"

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


# Initialize and cache the Mistral brain instance
_mistral_brain_instance = None


def get_mistral_brain(
    api_key: Optional[str] = None,
    model: str = "mistral-large-latest"
) -> MistralChemistryBrain:
    """
    Get or create the Mistral Chemistry AI Brain instance (singleton pattern).

    Args:
        api_key: Mistral API key (optional)
        model: Model name to use

    Returns:
        MistralChemistryBrain instance
    """
    global _mistral_brain_instance
    if _mistral_brain_instance is None:
        _mistral_brain_instance = MistralChemistryBrain(api_key=api_key, model=model)
    return _mistral_brain_instance