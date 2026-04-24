"""FastAPI main entry point for AI Chemistry Chatbot Backend."""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
import os
import sys
from pathlib import Path

# Add parent directory to path for importing tools
sys.path.append(str(Path(__file__).parent.parent))

from backend.tools.pubchem_tool import pubchem_tool
from backend.tools.wolfram_tool import wolfram_tool
from backend.tools.vision_tool import vision_tool
from backend.tools.media_tool import media_tool

# Initialize FastAPI app
app = FastAPI(
    title="AI Chemistry Chatbot Backend",
    description="Backend API for chemistry tutoring with specialized tools",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
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

# API Routes
@app.get("/")
async def root():
    """Root endpoint to check API status."""
    return {
        "message": "AI Chemistry Chatbot Backend API",
        "version": "1.0.0",
        "status": "running",
        "tools": {
            "pubchem": "Chemical properties and data",
            "wolfram": "Calculations and equation balancing",
            "vision": "Image analysis and OCR",
            "media": "Educational content generation"
        }
    }

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Main chat endpoint that orchestrates all tools.
    
    This endpoint analyzes the user's message and routes to appropriate tools,
    then synthesizes the response using the LLM orchestrator.
    """
    try:
        # This would integrate with the Gemini brain for tool orchestration
        # For now, return a placeholder response
        return {
            "response": "Chat functionality requires integration with Gemini brain",
            "tools_used": [],
            "confidence": "medium",
            "message": "This endpoint will be connected to the Gemini orchestrator"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PubChem Tool Endpoints
@app.post("/pubchem/info")
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

@app.post("/pubchem/search")
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

@app.post("/pubchem/molar-mass")
async def calculate_molar_mass(request: MolarMassRequest):
    """Calculate molar mass from formula."""
    try:
        mass = pubchem_tool.calculate_molar_mass(request.formula)
        if mass:
            return {
                "success": True,
                "formula": request.formula,
                "molar_mass": mass,
                "units": "g/mol"
            }
        else:
            return {
                "success": False,
                "error": f"Could not calculate molar mass for '{request.formula}'"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Wolfram Tool Endpoints
@app.post("/wolfram/balance-equation")
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

@app.post("/wolfram/stoichiometry")
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

@app.post("/wolfram/solve-problem")
async def solve_chemistry_problem(problem: str = Form(...)):
    """Solve general chemistry problem."""
    try:
        result = wolfram_tool.solve_chemistry_problem(problem)
        return {
            "success": result.success,
            "problem": problem,
            "solution": result.result,
            "steps": result.steps,
            "explanation": result.explanation,
            "error": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vision/OCR Tool Endpoints
@app.post("/vision/analyze-image")
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

# Media Tool Endpoints
@app.post("/media/generate-image")
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

@app.post("/media/molecular-structure")
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

@app.post("/media/reaction-diagram")
async def generate_reaction_diagram(
    reactants: str = Form(...),
    products: str = Form(...)
):
    """Generate chemical reaction diagram."""
    try:
        reactant_list = [r.strip() for r in reactants.split("+")]
        product_list = [p.strip() for p in products.split("+")]
        
        result = media_tool.generate_reaction_diagram(reactant_list, product_list)
        return {
            "success": result.success,
            "image_url": result.content_url,
            "content_type": result.content_type,
            "description": result.description,
            "error": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Check health of all tools."""
    health_status = {
        "status": "healthy",
        "tools": {
            "pubchem": "available",
            "wolfram": "available" if wolfram_tool.app_id else "limited (no API key)",
            "vision": "available" if vision_tool.mathpix_app_id or vision_tool.gemini_api_key else "limited (no API keys)",
            "media": "available"
        }
    }
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
