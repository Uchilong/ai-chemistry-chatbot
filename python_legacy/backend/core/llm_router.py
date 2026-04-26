"""LLM Router for orchestrating chemistry tools using AI."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union
import google.generativeai as genai

# Add parent directory to path for importing tools
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.tools.pubchem_tool import pubchem_tool
from backend.tools.wolfram_tool import wolfram_tool
from backend.tools.vision_tool import vision_tool
from backend.tools.media_tool import media_tool

class LLMRouter:
    """Intelligent router that orchestrates chemistry tools using AI."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.1-flash-lite-preview"):
        """
        Initialize LLM Router.
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for LLM Router")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
        self.system_prompt = """You are an intelligent Chemistry AI Router that orchestrates specialized tools to answer student questions.

## Available Tools:
- pubchem_tool: Get chemical properties, molar mass, structural information
- wolfram_tool: Balance equations, perform calculations, solve math problems  
- vision_tool: Extract text/equations from images using OCR
- media_tool: Generate educational images and content

## Your Job:
1. Analyze the student's question
2. Select appropriate tools
3. Call tools in correct sequence
4. Synthesize results into educational response
5. Provide step-by-step explanations

## Response Format:
Always structure your response as:
## Question Understanding
## Tools Used
## Step-by-Step Solution
## Key Concepts
## Practice Problem
## Summary

## Tool Calling:
When you need to use a tool, format your response with:
TOOL_CALL: tool_name(parameters)

Examples:
TOOL_CALL: pubchem_tool.get_chemical_info(identifier="water")
TOOL_CALL: wolfram_tool.balance_equation(equation="H2 + O2 -> H2O")
TOOL_CALL: vision_tool.extract_from_image(image_path="path/to/image.jpg")

Be educational, clear, and scaffold learning for high school students."""
    
    def route_and_respond(self, user_message: str, chat_history: Optional[List[Dict]] = None, 
                         chemistry_context: Optional[Dict] = None) -> str:
        """
        Route user message to appropriate tools and generate response.
        
        Args:
            user_message: Student's question
            chat_history: Previous conversation
            chemistry_context: Educational context
            
        Returns:
            Educational response with tool results
        """
        try:
            # Build context
            context = self._build_context(user_message, chemistry_context)
            
            # Generate response with tool orchestration
            response = self._generate_with_tools(user_message, context)
            
            return response
            
        except Exception as e:
            return f"Error processing your question: {str(e)}"
    
    def _build_context(self, user_message: str, chemistry_context: Optional[Dict]) -> str:
        """Build educational context for the AI."""
        context_parts = [
            "## Educational Context",
            f"Student Question: {user_message}",
            f"Level: High School Chemistry",
            "Language: Use Vietnamese if student uses Vietnamese, otherwise English"
        ]
        
        if chemistry_context:
            for key, value in chemistry_context.items():
                context_parts.append(f"{key.title()}: {value}")
        
        return "\n".join(context_parts)
    
    def _generate_with_tools(self, user_message: str, context: str) -> str:
        """Generate response using tool orchestration."""
        # Start chat with system prompt
        chat = self.model.start_chat(history=[])
        
        # Send context and question
        full_prompt = f"{self.system_prompt}\n\n{context}\n\nStudent Question: {user_message}"
        
        response = chat.send_message(full_prompt)
        response_text = response.text
        
        # Process tool calls in response
        processed_response = self._process_tool_calls(response_text)
        
        return processed_response
    
    def _process_tool_calls(self, response_text: str) -> str:
        """Process and execute tool calls in the AI response."""
        lines = response_text.split('\n')
        processed_lines = []
        tool_results = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('TOOL_CALL:'):
                # Parse and execute tool call
                tool_result = self._execute_tool_call(line)
                tool_results[line] = tool_result
                
                # Add tool result to response
                processed_lines.append(f"**Tool Result:** {tool_result}")
                processed_lines.append("")  # Add spacing
            else:
                processed_lines.append(line)
            
            i += 1
        
        # If tool calls were made, regenerate response with results
        if tool_results:
            return self._regenerate_with_tool_results('\n'.join(processed_lines), tool_results)
        
        return '\n'.join(processed_lines)
    
    def _execute_tool_call(self, tool_call_line: str) -> str:
        """Execute a specific tool call."""
        try:
            # Parse tool call format: TOOL_CALL: tool_name(param1=value1, param2=value2)
            if ':' not in tool_call_line:
                return "Invalid tool call format"
            
            tool_part = tool_call_line.split(':', 1)[1].strip()
            
            if '(' not in tool_part or not tool_part.endswith(')'):
                return "Invalid tool call format"
            
            tool_name = tool_part.split('(')[0].strip()
            params_str = tool_part.split('(')[1][:-1].strip()  # Remove trailing ')'
            
            # Parse parameters
            params = self._parse_parameters(params_str)
            
            # Execute tool
            result = self._call_tool(tool_name, params)
            
            return str(result)
            
        except Exception as e:
            return f"Tool execution error: {str(e)}"
    
    def _parse_parameters(self, params_str: str) -> Dict[str, str]:
        """Parse parameter string into dictionary."""
        params: Dict[str, str] = {}
        
        if not params_str:
            return params
        
        # Simple parameter parsing (key=value format)
        pairs = params_str.split(',')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key.strip()] = value.strip().strip('"\'')
        
        return params
    
    def _call_tool(self, tool_name: str, params: Dict[str, str]) -> Union[str, Dict]:
        """Call the appropriate tool with parameters."""
        try:
            if tool_name == "pubchem_tool.get_chemical_info":
                identifier = params.get('identifier', '')
                info_result = pubchem_tool.get_chemical_info(identifier)
                if info_result:
                    return {
                        'name': info_result.name,
                        'formula': info_result.formula,
                        'molar_mass': info_result.molar_mass,
                        'description': info_result.description
                    }
                else:
                    return f"Chemical '{identifier}' not found"
            
            elif tool_name == "pubchem_tool.calculate_molar_mass":
                formula = params.get('formula', '')
                mass = pubchem_tool.calculate_molar_mass(formula)
                if mass:
                    return f"Molar mass of {formula}: {mass} g/mol"
                else:
                    return f"Could not calculate molar mass for {formula}"
            
            elif tool_name == "wolfram_tool.balance_equation":
                equation = params.get('equation', '')
                bal_result = wolfram_tool.balance_equation(equation)
                if bal_result.success:
                    return {
                        'balanced_equation': bal_result.result,
                        'steps': bal_result.steps
                    }
                else:
                    return f"Could not balance equation: {bal_result.error_message}"
            
            elif tool_name == "wolfram_tool.stoichiometry_calculation":
                equation = params.get('equation', '')
                given_amount = float(params.get('given_amount', 0))
                given_unit = params.get('given_unit', '')
                find_substance = params.get('find_substance', '')
                
                stoich_result = wolfram_tool.stoichiometry_calculation(
                    equation, given_amount, given_unit, find_substance
                )
                if stoich_result.success:
                    return {
                        'result': stoich_result.result,
                        'steps': stoich_result.steps
                    }
                else:
                    return f"Stoichiometry calculation failed: {stoich_result.error_message}"
            
            elif tool_name == "vision_tool.extract_from_image":
                image_path = params.get('image_path', '')
                vis_result = vision_tool.extract_from_image(image_path)
                if vis_result.success:
                    return {
                        'extracted_text': vis_result.extracted_text,
                        'equations': vis_result.equations,
                        'chemical_formulas': vis_result.chemical_formulas
                    }
                else:
                    return f"Image analysis failed: {vis_result.error_message}"
            
            elif tool_name == "media_tool.generate_chemistry_image":
                concept = params.get('concept', '')
                style = params.get('style', 'educational')
                img_result = media_tool.generate_chemistry_image(concept, style)
                if img_result.success:
                    return f"Generated image: {img_result.content_url}"
                else:
                    return f"Image generation failed: {img_result.error_message}"
            
            elif tool_name == "media_tool.generate_molecular_structure":
                formula = params.get('formula', '')
                struct_result = media_tool.generate_molecular_structure(formula)
                if struct_result.success:
                    return f"Generated molecular structure: {struct_result.content_url}"
                else:
                    return f"Molecular structure generation failed: {struct_result.error_message}"
            
            else:
                return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            return f"Tool call failed: {str(e)}"
    
    def _regenerate_with_tool_results(self, initial_response: str, tool_results: Dict[str, str]) -> str:
        """Regenerate response incorporating tool results."""
        # For now, return the initial response with tool results
        # In a more sophisticated implementation, you'd send this back to the AI
        # to synthesize a better response
        
        final_response = initial_response
        
        # Add a summary section
        final_response += "\n\n## Tool Results Summary\n"
        for tool_call, result in tool_results.items():
            final_response += f"- {tool_call}: {result}\n"
        
        return final_response

# Singleton instance
llm_router = LLMRouter()
