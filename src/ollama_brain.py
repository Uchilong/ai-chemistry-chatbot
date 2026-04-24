import requests
from typing import Optional
import json


class OllamaChemistryBrain:
    """Backend brain for AI Chemistry Chatbot using Ollama (local)."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize the Ollama Chemistry AI Brain.
        
        Args:
            ollama_url: URL of the Ollama server
            model: Model name (default: llama2, you can use llama2, neural-chat, etc.)
        """
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
        
        self.system_prompt = """You are an expert Chemistry AI tutor specializing in helping students learn chemistry.
Your responsibilities:
- Explain chemistry concepts clearly and comprehensively
- Solve chemistry problems step-by-step
- Provide molecular structure analysis and predictions
- Explain chemical reactions and their mechanisms
- Help with homework and practice problems
- Provide real-world applications of chemistry concepts
- Use Vietnamese language when interacting with Vietnamese-speaking students

Always:
- Be accurate and scientifically correct
- Explain in a way that's easy to understand
- Use examples when helpful
- Organize your responses clearly with headings and bullet points when appropriate"""
    
    def _check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def chat(self, user_message: str, chat_history: Optional[list] = None) -> str:
        """
        Send a text message and get AI response from Ollama.
        
        Args:
            user_message: The user's chemistry question or message
            chat_history: Previous messages for context (list of dicts with 'role' and 'content')
        
        Returns:
            AI's response text
        """
        try:
            # Build conversation history
            conversation = f"{self.system_prompt}\n\n"
            
            if chat_history:
                for msg in chat_history:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    conversation += f"{role}: {msg.get('content', '')}\n"
            
            conversation += f"User: {user_message}\nAssistant:"
            
            # Call Ollama
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": conversation,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response received").strip()
            elif response.status_code == 404:
                return f"❌ Error: Model '{self.model}' not found in Ollama. Please run:\n  ollama pull {self.model}\nOr check if Ollama is running on {self.ollama_url}"
            else:
                return f"❌ Error: Ollama returned status {response.status_code}. Make sure Ollama is running on {self.ollama_url}"
        
        except requests.exceptions.ConnectionError:
            return f"❌ Error: Cannot connect to Ollama at {self.ollama_url}. Please start Ollama with: ollama serve"
        except requests.exceptions.Timeout:
            return "❌ Error: Ollama request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def chat_with_image(
        self, 
        user_message: str, 
        image_path: str, 
        chat_history: Optional[list] = None
    ) -> str:
        """
        Ollama doesn't support image analysis by default.
        Return a helpful message.
        """
        return "⚠️ Image analysis is not supported with Ollama. Please use the Gemini API for image analysis, or describe the image in text."
    
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


# Initialize and cache the Ollama brain instance
_ollama_brain_instance = None


def get_ollama_brain(
    ollama_url: str = "http://localhost:11434", 
    model: str = "llama2"
) -> OllamaChemistryBrain:
    """
    Get or create the Ollama Chemistry AI Brain instance (singleton pattern).
    
    Args:
        ollama_url: URL of Ollama server
        model: Model name to use
    
    Returns:
        OllamaChemistryBrain instance
    """
    global _ollama_brain_instance
    if _ollama_brain_instance is None:
        _ollama_brain_instance = OllamaChemistryBrain(ollama_url=ollama_url, model=model)
    return _ollama_brain_instance
