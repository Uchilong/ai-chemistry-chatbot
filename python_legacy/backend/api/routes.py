"""API routes for AI Chemistry Chatbot Backend."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path for importing tools
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.tools.pubchem_tool import pubchem_tool
from backend.tools.wolfram_tool import wolfram_tool
from backend.tools.vision_tool import vision_tool
from backend.tools.media_tool import media_tool

# Create router
router = APIRouter()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = None
    chemistry_context: Optional[Dict[str, str]] = None

class ChemicalInfoRequest(BaseModel):
    identifier: str

class EquationBalanceRequest(BaseModel):
    equation: str

class StoichiometryRequest(BaseModel):
    equation: str
    given_amount: float
    given_unit: str
    find_substance: str

class MolarMassRequest(BaseModel):
    formula: str

class MediaGenerationRequest(BaseModel):
    concept: str
    style: str = "educational"

# PubChem routes
@router.post("/pubchem/info")
async def get_chemical_info(request: ChemicalInfoRequest):
    """Get comprehensive chemical information."""
    try:
        info = pubchem_tool.get_chemical_info(request.identifier)
        if info:
            return {
                "success": True,
                "data": {
                    "name": info.name,
                    "formula": info.formula,
                    "molar_mass": info.molar_mass,
                    "iupac_name": info.iupac_name,
                    "common_name": info.common_name,
                    "description": info.description,
                    "properties": info.properties,
                    "safety_info": info.safety_info
                }
            }
        else:
            return {
                "success": False,
                "error": f"Chemical '{request.identifier}' not found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pubchem/search")
async def search_compounds(query: str = Form(...), limit: int = Form(10)):
    """Search for compounds by name or formula."""
    try:
        results = pubchem_tool.search_compounds(query, limit)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Wolfram routes
@router.post("/wolfram/balance-equation")
async def balance_equation(request: EquationBalanceRequest):
    """Balance chemical equation."""
    try:
        result = wolfram_tool.balance_equation(request.equation)
        return {
            "success": result.success,
            "input_equation": request.equation,
            "balanced_equation": result.result,
            "steps": result.steps,
            "explanation": result.explanation,
            "error": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wolfram/stoichiometry")
async def stoichiometry_calculation(request: StoichiometryRequest):
    """Perform stoichiometry calculations."""
    try:
        result = wolfram_tool.stoichiometry_calculation(
            request.equation,
            request.given_amount,
            request.given_unit,
            request.find_substance
        )
        return {
            "success": result.success,
            "input": {
                "equation": request.equation,
                "given_amount": request.given_amount,
                "given_unit": request.given_unit,
                "find_substance": request.find_substance
            },
            "result": result.result,
            "steps": result.steps,
            "explanation": result.explanation,
            "error": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vision routes
@router.post("/vision/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze image and extract text/equations."""
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analyze image
        result = vision_tool.analyze_chemistry_diagram(temp_path)
        
        # Clean up temp file
        import os
        os.remove(temp_path)
        
        return {
            "success": result["success"],
            "extracted_text": result["extracted_text"],
            "equations": result["equations"],
            "chemical_formulas": result["chemical_formulas"],
            "diagram_type": result["diagram_type"],
            "confidence": result["confidence"],
            "error": result.get("error")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Media routes
@router.post("/media/generate-image")
async def generate_chemistry_image(request: MediaGenerationRequest):
    """Generate educational chemistry image."""
    try:
        result = media_tool.generate_chemistry_image(request.concept, request.style)
        return {
            "success": result.success,
            "image_url": result.content_url,
            "content_type": result.content_type,
            "description": result.description,
            "error": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/media/molecular-structure")
async def generate_molecular_structure(formula: str = Form(...)):
    """Generate molecular structure visualization."""
    try:
        result = media_tool.generate_molecular_structure(formula)
        return {
            "success": result.success,
            "image_url": result.content_url,
            "content_type": result.content_type,
            "description": result.description,
            "error": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
