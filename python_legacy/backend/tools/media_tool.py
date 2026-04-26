"""Media tool for generating educational images and audio content."""

import os
import requests
from typing import Dict, List, Optional, Union
import base64
from dataclasses import dataclass

@dataclass
class MediaResult:
    """Data class for media generation results."""
    content_url: str
    content_type: str  # 'image', 'audio', 'video'
    description: str
    success: bool
    error_message: Optional[str] = None

class MediaTool:
    """Tool for generating educational media content."""
    
    def __init__(self, pollinations_api_key: Optional[str] = None):
        """
        Initialize Media tool.
        
        Args:
            pollinations_api_key: API key for Pollinations.ai (optional, they have free tier)
        """
        self.pollinations_api_key = pollinations_api_key or os.getenv("POLLINATIONS_API_KEY", "")
        self.pollinations_url = "https://image.pollinations.ai/prompt"
        
    def generate_chemistry_image(self, concept: str, style: str = "educational") -> MediaResult:
        """
        Generate an educational image for a chemistry concept.
        
        Args:
            concept: Chemistry concept to visualize (e.g., "water molecule structure")
            style: Image style (educational, diagram, realistic, cartoon)
            
        Returns:
            MediaResult with image URL
        """
        try:
            # Create detailed prompt for chemistry visualization
            prompt = self._create_chemistry_image_prompt(concept, style)
            
            # Generate image using Pollinations
            image_url = f"{self.pollinations_url}/{prompt}"
            
            # Add API key if available
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Educational image showing: {concept}",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating image: {str(e)}"
            )
    
    def generate_molecular_structure(self, formula: str) -> MediaResult:
        """
        Generate molecular structure visualization.
        
        Args:
            formula: Chemical formula (e.g., "H2O", "C6H12O6")
            
        Returns:
            MediaResult with molecular structure image
        """
        try:
            prompt = f"detailed molecular structure diagram of {formula}, ball and stick model, accurate chemical bonds, educational chemistry illustration, white background, professional scientific visualization"
            
            image_url = f"{self.pollinations_url}/{prompt}"
            
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Molecular structure of {formula}",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating molecular structure: {str(e)}"
            )
    
    def generate_reaction_diagram(self, reactants: List[str], products: List[str]) -> MediaResult:
        """
        Generate chemical reaction diagram.
        
        Args:
            reactants: List of reactant formulas
            products: List of product formulas
            
        Returns:
            MediaResult with reaction diagram
        """
        try:
            reactants_str = " + ".join(reactants)
            products_str = " + ".join(products)
            
            prompt = f"chemical reaction diagram showing {reactants_str} → {products_str}, balanced equation, educational chemistry illustration, molecular structures, reaction arrow, professional scientific diagram, white background"
            
            image_url = f"{self.pollinations_url}/{prompt}"
            
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Chemical reaction: {reactants_str} → {products_str}",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating reaction diagram: {str(e)}"
            )
    
    def generate_lab_equipment_diagram(self, equipment: str) -> MediaResult:
        """
        Generate laboratory equipment diagram.
        
        Args:
            equipment: Type of lab equipment (e.g., "burette", "distillation setup")
            
        Returns:
            MediaResult with equipment diagram
        """
        try:
            prompt = f"detailed scientific diagram of {equipment}, laboratory equipment, educational chemistry illustration, labeled parts, professional technical drawing, white background, clear labels"
            
            image_url = f"{self.pollinations_url}/{prompt}"
            
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Laboratory equipment: {equipment}",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating equipment diagram: {str(e)}"
            )
    
    def generate_periodic_table_element(self, element: str) -> MediaResult:
        """
        Generate periodic table element visualization.
        
        Args:
            element: Element name or symbol (e.g., "Gold", "Au")
            
        Returns:
            MediaResult with element visualization
        """
        try:
            prompt = f"periodic table element {element}, atomic number, atomic mass, electron configuration, educational chemistry poster, scientific illustration, element properties, professional design"
            
            image_url = f"{self.pollinations_url}/{prompt}"
            
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Periodic table element: {element}",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating element visualization: {str(e)}"
            )
    
    def generate_chemistry_audio_explanation(self, concept: str, language: str = "en") -> MediaResult:
        """
        Generate audio explanation of chemistry concept.
        
        Args:
            concept: Chemistry concept to explain
            language: Language code (en, vi, etc.)
            
        Returns:
            MediaResult with audio URL
        """
        try:
            # This is a placeholder - in real implementation, you'd use
            # text-to-speech services like Google TTS, Azure TTS, or Hugging Face
            
            # For now, return a placeholder response
            explanation = f"Audio explanation of {concept} would be generated here using text-to-speech technology."
            
            return MediaResult(
                content_url="audio_placeholder_url",
                content_type="audio",
                description=explanation,
                success=False,
                error_message="Audio generation requires TTS service integration"
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="audio",
                description="",
                success=False,
                error_message=f"Error generating audio: {str(e)}"
            )
    
    def _create_chemistry_image_prompt(self, concept: str, style: str) -> str:
        """Create detailed prompt for chemistry image generation."""
        base_prompt = f"{concept}"
        
        style_modifiers = {
            "educational": "educational chemistry illustration, textbook style, clear labels, professional scientific diagram",
            "diagram": "technical diagram, blueprint style, precise lines, professional engineering drawing",
            "realistic": "photorealistic, high quality, detailed, professional photography",
            "cartoon": "friendly cartoon style, colorful, educational animation style, engaging for students"
        }
        
        if style in style_modifiers:
            base_prompt += f", {style_modifiers[style]}"
        
        # Add common chemistry visualization enhancements
        base_prompt += ", white background, clear visualization, educational content, chemistry"
        
        # URL encode the prompt
        return requests.utils.quote(base_prompt)
    
    def generate_study_card(self, concept: str, definition: str) -> MediaResult:
        """
        Generate study card image for chemistry concept.
        
        Args:
            concept: Chemistry concept name
            definition: Concept definition
            
        Returns:
            MediaResult with study card image
        """
        try:
            prompt = f"chemistry study card, title: {concept}, definition: {definition}, educational flashcard design, clean layout, readable text, professional study material, white background"
            
            image_url = f"{self.pollinations_url}/{prompt}"
            
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Study card: {concept}",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating study card: {str(e)}"
            )
    
    def generate_chemistry_formula_sheet(self, formulas: List[str]) -> MediaResult:
        """
        Generate formula sheet with multiple chemistry formulas.
        
        Args:
            formulas: List of chemistry formulas
            
        Returns:
            MediaResult with formula sheet image
        """
        try:
            formulas_text = ", ".join(formulas[:5])  # Limit to first 5 formulas
            prompt = f"chemistry formula sheet, formulas: {formulas_text}, educational reference sheet, organized layout, clear mathematical notation, professional study guide, white background"
            
            image_url = f"{self.pollinations_url}/{prompt}"
            
            if self.pollinations_api_key:
                image_url += f"?key={self.pollinations_api_key}"
            
            return MediaResult(
                content_url=image_url,
                content_type="image",
                description=f"Chemistry formula sheet with {len(formulas)} formulas",
                success=True
            )
            
        except Exception as e:
            return MediaResult(
                content_url="",
                content_type="image",
                description="",
                success=False,
                error_message=f"Error generating formula sheet: {str(e)}"
            )

# Singleton instance
media_tool = MediaTool()
