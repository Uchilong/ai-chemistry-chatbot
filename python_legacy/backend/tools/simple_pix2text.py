"""Simple Pix2Text-like implementation for free OCR without compilation issues."""

import os
import re
from typing import Dict, List, Optional, Union
from PIL import Image
import numpy as np
from dataclasses import dataclass

# Try to import available OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

@dataclass
class Pix2TextResult:
    """Data class for Pix2Text-like results."""
    markdown: str
    text_blocks: List[str]
    equations: List[str]
    confidence: float
    success: bool
    error_message: Optional[str] = None

class SimplePix2Text:
    """Simplified Pix2Text implementation using available OCR libraries."""
    
    def __init__(self):
        """Initialize SimplePix2Text."""
        self.easyocr_reader = None
        
        # Initialize EasyOCR if available
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = easyocr.Reader(['en', 'vi'])  # English and Vietnamese
                print("SimplePix2Text initialized with EasyOCR")
            except Exception as e:
                print(f"EasyOCR initialization failed: {e}")
                self.easyocr_reader = None
        else:
            print("EasyOCR not available. Install with: pip install easyocr")
    
    def recognize(self, image_path: str) -> Pix2TextResult:
        """
        Recognize text and equations from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Pix2TextResult with recognized content
        """
        try:
            if not os.path.exists(image_path):
                return Pix2TextResult(
                    markdown="",
                    text_blocks=[],
                    equations=[],
                    confidence=0.0,
                    success=False,
                    error_message=f"Image file not found: {image_path}"
                )
            
            # Use EasyOCR for text recognition
            if self.easyocr_reader:
                return self._recognize_with_easyocr(image_path)
            else:
                return self._fallback_recognition(image_path)
                
        except Exception as e:
            return Pix2TextResult(
                markdown="",
                text_blocks=[],
                equations=[],
                confidence=0.0,
                success=False,
                error_message=f"Recognition failed: {str(e)}"
            )
    
    def _recognize_with_easyocr(self, image_path: str) -> Pix2TextResult:
        """Recognize using EasyOCR with enhanced processing."""
        try:
            # Read image with EasyOCR
            results = self.easyocr_reader.readtext(image_path)
            
            if not results:
                return Pix2TextResult(
                    markdown="No text detected",
                    text_blocks=[],
                    equations=[],
                    confidence=0.0,
                    success=False,
                    error_message="No text found"
                )
            
            # Process results
            text_blocks = []
            equations = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                text_blocks.append(text)
                confidences.append(confidence)
                
                # Extract potential equations
                if self._is_likely_equation(text):
                    equations.append(text)
            
            # Combine into markdown format
            markdown = self._format_as_markdown(text_blocks, equations)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return Pix2TextResult(
                markdown=markdown,
                text_blocks=text_blocks,
                equations=equations,
                confidence=avg_confidence,
                success=True
            )
            
        except Exception as e:
            return Pix2TextResult(
                markdown="",
                text_blocks=[],
                equations=[],
                confidence=0.0,
                success=False,
                error_message=f"EasyOCR recognition failed: {str(e)}"
            )
    
    def _fallback_recognition(self, image_path: str) -> Pix2TextResult:
        """Fallback recognition when EasyOCR is not available."""
        return Pix2TextResult(
            markdown="OCR requires EasyOCR. Install with: pip install easyocr",
            text_blocks=[],
            equations=[],
            confidence=0.0,
            success=False,
            error_message="OCR service not available"
        )
    
    def _is_likely_equation(self, text: str) -> bool:
        """Check if text is likely a mathematical equation."""
        equation_indicators = [
            r'[=+\-*/]',
            r'[a-z]\s*[=+\-*/]',
            r'\d+\s*[=+\-*/]',
            r'[a-zA-Z]\^\d',
            r'\\[a-zA-Z]+',  # LaTeX commands
            r'\$.*\$',      # LaTeX math mode
            r'∫∑∏√±≤≥≠≈',
        ]
        
        for pattern in equation_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _format_as_markdown(self, text_blocks: List[str], equations: List[str]) -> str:
        """Format recognized text as markdown."""
        if not text_blocks:
            return "No text detected"
        
        markdown_parts = []
        
        # Add equations if found
        if equations:
            markdown_parts.append("## Equations")
            for eq in equations:
                markdown_parts.append(f"$$ {eq} $$")
            markdown_parts.append("")
        
        # Add all text blocks
        markdown_parts.append("## Text Content")
        for text in text_blocks:
            # Skip if it's already in equations
            if text not in equations:
                markdown_parts.append(text)
        
        return "\n".join(markdown_parts)
    
    def analyze_chemistry_content(self, image_path: str) -> Dict[str, Union[str, List[str]]]:
        """
        Analyze chemistry-specific content from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with chemistry analysis
        """
        result = self.recognize(image_path)
        
        if not result.success:
            return {
                "success": False,
                "error": result.error_message,
                "extracted_text": "",
                "chemical_formulas": [],
                "equations": []
            }
        
        # Extract chemical formulas from text
        chemical_formulas = self._extract_chemical_formulas(result.text_blocks)
        
        return {
            "success": True,
            "extracted_text": result.markdown,
            "chemical_formulas": chemical_formulas,
            "equations": result.equations,
            "confidence": result.confidence
        }
    
    def _extract_chemical_formulas(self, text_blocks: List[str]) -> List[str]:
        """Extract chemical formulas from text blocks."""
        formulas = []
        chemical_elements = {
            'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al',
            'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn',
            'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag',
            'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce',
            'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm',
            'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa',
            'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No',
            'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh',
            'Fl', 'Mc', 'Lv', 'Ts', 'Og'
        }
        
        # Common chemistry terms
        chemistry_terms = {
            'H2O', 'CO2', 'NaCl', 'CH4', 'NH3', 'O2', 'N2', 'H2', 'pH', 'pKa',
            'H2SO4', 'HCl', 'NaOH', 'KOH', 'CaCO3', 'Fe2O3', 'CuSO4', 'AgNO3'
        }
        
        # Chemical formula patterns
        formula_patterns = [
            r'\b[A-Z][a-z]?\d*\b',
            r'\b[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+\b',
            r'[A-Z][a-z]?\d*\([^)]*\)\d*',
            r'[A-Z][a-z]?\d*\s*[-=]\s*[A-Z][a-z]?\d*',
        ]
        
        for text in text_blocks:
            for pattern in formula_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # Check if it's a known chemistry term
                    if match in chemistry_terms:
                        formulas.append(match)
                    else:
                        # Check if it contains chemical elements
                        elements = re.findall(r'[A-Z][a-z]?', match)
                        if any(elem in chemical_elements for elem in elements):
                            formulas.append(match)
        
        return list(set(formulas))  # Remove duplicates

# Singleton instance
simple_pix2text = SimplePix2Text()
