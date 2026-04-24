"""Vision/OCR tool for extracting text and equations from images."""

import os
import base64
import requests
from typing import Dict, List, Optional, Union
from PIL import Image
import io
import re
from dataclasses import dataclass

# Import SimplePix2Text for free OCR
try:
    from .simple_pix2text import simple_pix2text
    PIX2TEXT_AVAILABLE = True
except ImportError:
    PIX2TEXT_AVAILABLE = False
    print("SimplePix2Text not available. Check simple_pix2text.py")

@dataclass
class OCRResult:
    """Data class for OCR results."""
    extracted_text: str
    equations: List[str]
    chemical_formulas: List[str]
    confidence: float
    success: bool
    error_message: Optional[str] = None

class VisionTool:
    """Tool for image analysis and OCR using SimplePix2Text (pix2text) and Gemini Vision."""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize Vision tool.
        
        Args:
            gemini_api_key: Gemini API Key (for fallback vision)
        """
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        
        # Initialize SimplePix2Text
        self.pix2text = simple_pix2text if PIX2TEXT_AVAILABLE else None
        
        # Warn about available OCR services
        available_services = []
        if PIX2TEXT_AVAILABLE:
            available_services.append("SimplePix2Text (Free pix2text alternative)")
        if self.gemini_api_key:
            available_services.append("Gemini Vision")
        
        if available_services:
            print(f"Available OCR services: {', '.join(available_services)}")
        else:
            print("Warning: No OCR services available. Add SimplePix2Text or Gemini API key.")
    
    def extract_from_image(self, image_path: str) -> OCRResult:
        """
        Extract text and equations from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            OCRResult with extracted content
        """
        try:
            # Try SimplePix2Text first (free and optimized for chemistry)
            if self.pix2text:
                result = self._extract_with_pix2text(image_path)
                if result.success:
                    return result
            
            # Fallback to Gemini Vision
            if self.gemini_api_key:
                result = self._extract_with_gemini(image_path)
                if result.success:
                    return result
            
            # Final fallback with basic processing
            return self._basic_ocr_fallback(image_path)
            
        except Exception as e:
            return OCRResult(
                extracted_text="",
                equations=[],
                chemical_formulas=[],
                confidence=0.0,
                success=False,
                error_message=f"Error processing image: {str(e)}"
            )
    
    def _extract_with_pix2text(self, image_path: str) -> OCRResult:
        """Extract text using SimplePix2Text (free Pix2Text alternative)."""
        try:
            # Use SimplePix2Text for chemistry-optimized recognition
            result = self.pix2text.analyze_chemistry_content(image_path)
            
            if not result["success"]:
                return OCRResult(
                    extracted_text="",
                    equations=[],
                    chemical_formulas=[],
                    confidence=0.0,
                    success=False,
                    error_message=result.get("error", "Pix2Text recognition failed")
                )
            
            # Extract equations from text
            extracted_text = result["extracted_text"]
            equations = self._extract_equations(extracted_text)
            
            return OCRResult(
                extracted_text=extracted_text,
                equations=equations,
                chemical_formulas=result["chemical_formulas"],
                confidence=result["confidence"],
                success=True
            )
            
        except Exception as e:
            return OCRResult(
                extracted_text="",
                equations=[],
                chemical_formulas=[],
                confidence=0.0,
                success=False,
                error_message=f"SimplePix2Text extraction failed: {str(e)}"
            )
    
    def _extract_with_easyocr(self, image_path: str) -> OCRResult:
        """Extract text using EasyOCR (free OCR alternative)."""
        try:
            # Read image using EasyOCR
            results = self.easyocr_reader.readtext(image_path)
            
            if not results:
                return OCRResult(
                    extracted_text="No text detected in image",
                    equations=[],
                    chemical_formulas=[],
                    confidence=0.0,
                    success=False,
                    error_message="No text found"
                )
            
            # Combine all detected text
            extracted_text = ""
            confidences = []
            
            for (bbox, text, confidence) in results:
                extracted_text += text + " "
                confidences.append(confidence)
            
            # Clean up text
            extracted_text = extracted_text.strip()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Extract equations and chemical formulas
            equations = self._extract_equations(extracted_text)
            chemical_formulas = self._extract_chemical_formulas(extracted_text)
            
            return OCRResult(
                extracted_text=extracted_text,
                equations=equations,
                chemical_formulas=chemical_formulas,
                confidence=avg_confidence,
                success=True
            )
            
        except Exception as e:
            return OCRResult(
                extracted_text="",
                equations=[],
                chemical_formulas=[],
                confidence=0.0,
                success=False,
                error_message=f"EasyOCR extraction failed: {str(e)}"
            )
    
    def _extract_with_gemini(self, image_path: str) -> OCRResult:
        """Extract text using Gemini Vision API."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Load image
            image = Image.open(image_path)
            
            # Prompt for chemistry content extraction
            prompt = """Extract all text, equations, and chemical formulas from this image. 
            Please provide:
            1. All readable text
            2. Any mathematical equations (in LaTeX format if possible)
            3. Any chemical formulas or equations
            
            Format your response clearly with sections for each type of content."""
            
            response = model.generate_content([prompt, image])
            extracted_text = response.text
            
            # Extract equations and formulas
            equations = self._extract_equations(extracted_text)
            chemical_formulas = self._extract_chemical_formulas(extracted_text)
            
            return OCRResult(
                extracted_text=extracted_text,
                equations=equations,
                chemical_formulas=chemical_formulas,
                confidence=0.8,  # Gemini doesn't provide confidence, use reasonable default
                success=True
            )
            
        except Exception as e:
            return OCRResult(
                extracted_text="",
                equations=[],
                chemical_formulas=[],
                confidence=0.0,
                success=False,
                error_message=f"Gemini Vision extraction failed: {str(e)}"
            )
    
    def _basic_ocr_fallback(self, image_path: str) -> OCRResult:
        """Basic fallback when no APIs are available."""
        try:
            # This is a placeholder - in real implementation, you'd use
            # libraries like pytesseract or EasyOCR
            return OCRResult(
                extracted_text="OCR requires pix2text (SimplePix2Text) or Gemini API credentials. Please configure API keys to extract text from images.",
                equations=[],
                chemical_formulas=[],
                confidence=0.0,
                success=False,
                error_message="No OCR service available"
            )
            
        except Exception as e:
            return OCRResult(
                extracted_text="",
                equations=[],
                chemical_formulas=[],
                confidence=0.0,
                success=False,
                error_message=f"Basic OCR failed: {str(e)}"
            )
    
    def _extract_equations(self, text: str) -> List[str]:
        """Extract mathematical equations from text."""
        equations = []
        
        # LaTeX patterns
        latex_patterns = [
            r'\$\$([^$]+)\$\$',  # Display math $$...$$
            r'\$([^$]+)\$',      # Inline math $...$
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{align\}(.*?)\\end\{align\}'
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            equations.extend(matches)
        
        # Common equation patterns
        equation_patterns = [
            r'[A-Za-z]+\s*=\s*[^.!?]+[.!?]?',  # variable = expression
            r'\d+\s*[+\-*/]\s*\d+',             # simple arithmetic
            r'[A-Za-z]+\^\d+',                  # exponents
            r'\([^)]+\)\s*[+\-*/]\s*\([^)]+\)', # parenthetical expressions
        ]
        
        for pattern in equation_patterns:
            matches = re.findall(pattern, text)
            equations.extend(matches)
        
        return list(set(equations))  # Remove duplicates
    
    def _extract_chemical_formulas(self, text: str) -> List[str]:
        """Extract chemical formulas from text with chemistry-specific optimization."""
        formulas = []
        
        # Enhanced chemical formula patterns for chemistry context
        formula_patterns = [
            # Basic element symbols with numbers and charges
            r'\b[A-Z][a-z]?\d*(?:[+-]\d*)?\b',
            # Multiple elements in compounds (H2O, NaCl, C6H12O6)
            r'\b[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+\b',
            # Parenthetical groups with coefficients (Ca(OH)2)
            r'[A-Z][a-z]?\d*\([^)]*\)\d*',
            # Chemical equations with arrows and equals
            r'[A-Z][a-z]?\d*(?:\s*[+\-]\s*[A-Z][a-z]?\d*)*\s*(?:[-=→→]\s*)?[A-Z][a-z]?\d*(?:\s*[+\-]\s*[A-Z][a-z]?\d*)*',
            # Ionic compounds with charges (Na+, Cl-, SO4^2-)
            r'[A-Z][a-z]?\d*(?:[+\-]\d+|\^[+-]\d+)',
            # Common chemistry notation (pH, pKa, etc.)
            r'\bp[HK][a-z]*\d*',
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            formulas.extend(matches)
        
        # Comprehensive chemical elements list
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
        
        # Common chemistry terms to include
        chemistry_terms = {
            'H2O', 'CO2', 'NaCl', 'CH4', 'NH3', 'O2', 'N2', 'H2', 'pH', 'pKa',
            'H2SO4', 'HCl', 'NaOH', 'KOH', 'CaCO3', 'Fe2O3', 'CuSO4', 'AgNO3'
        }
        
        # Filter and enhance formulas
        filtered_formulas = []
        for formula in formulas:
            # Clean up formula
            formula = formula.strip()
            
            # Skip if too short or too long
            if len(formula) < 1 or len(formula) > 50:
                continue
            
            # Check if it's a known chemistry term
            if formula in chemistry_terms:
                filtered_formulas.append(formula)
                continue
            
            # Extract element symbols from formula
            elements = re.findall(r'[A-Z][a-z]?', formula)
            
            # Keep only those with actual chemical elements
            if any(elem in chemical_elements for elem in elements):
                # Additional validation for chemical plausibility
                if self._is_chemically_plausible(formula):
                    filtered_formulas.append(formula)
        
        return list(set(filtered_formulas))  # Remove duplicates
    
    def _is_chemically_plausible(self, formula: str) -> bool:
        """Check if a formula looks chemically plausible."""
        # Remove common non-chemical patterns
        non_chemical_patterns = [
            r'^[A-Z]$',  # Single capital letter (likely not a formula)
            r'^\d+$',    # Pure numbers
            r'[a-z]+',   # Lowercase words
        ]
        
        for pattern in non_chemical_patterns:
            if re.match(pattern, formula):
                return False
        
        # Check for balanced parentheses
        if '(' in formula or ')' in formula:
            if formula.count('(') != formula.count(')'):
                return False
        
        # Check for reasonable element-to-number ratio
        elements = re.findall(r'[A-Z][a-z]?', formula)
        numbers = re.findall(r'\d+', formula)
        
        # If there are many numbers but few elements, might not be chemical
        if len(numbers) > len(elements) * 3:
            return False
        
        return True
    
    def analyze_chemistry_diagram(self, image_path: str) -> Dict[str, Union[str, List[str]]]:
        """
        Analyze chemistry-specific diagrams (reactions, structures, etc.).
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with analysis results
        """
        ocr_result = self.extract_from_image(image_path)
        
        analysis = {
            'extracted_text': ocr_result.extracted_text,
            'equations': ocr_result.equations,
            'chemical_formulas': ocr_result.chemical_formulas,
            'diagram_type': self._classify_diagram(ocr_result),
            'confidence': ocr_result.confidence,
            'success': ocr_result.success
        }
        
        if ocr_result.error_message:
            analysis['error'] = ocr_result.error_message
        
        return analysis
    
    def _classify_diagram(self, ocr_result: OCRResult) -> str:
        """Classify the type of chemistry diagram."""
        text = ocr_result.extracted_text.lower()
        formulas = ocr_result.chemical_formulas
        equations = ocr_result.equations
        
        # Classification logic
        if any(arrow in text for arrow in ['->', '→', '⇌', '↔']):
            if 'equilibrium' in text or '⇌' in text or '↔' in text:
                return 'equilibrium_reaction'
            else:
                return 'chemical_reaction'
        
        elif any(keyword in text for keyword in ['structure', 'bond', 'atom', 'molecule']):
            return 'molecular_structure'
        
        elif any(keyword in text for keyword in ['graph', 'plot', 'curve', 'axis']):
            return 'data_graph'
        
        elif any(keyword in text for keyword in ['lab', 'experiment', 'setup', 'apparatus']):
            return 'laboratory_setup'
        
        elif formulas and len(formulas) > 1:
            return 'formula_list'
        
        elif equations:
            return 'mathematical_equations'
        
        else:
            return 'general_text'

# Singleton instance
vision_tool = VisionTool()
