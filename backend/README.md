# AI Chemistry Chatbot Backend

## Overview
This backend provides specialized chemistry tools orchestrated by AI for high school chemistry education.

## Available Tools

### 🔬 PubChem Tool (`backend/tools/pubchem_tool.py`)
- **Purpose**: Chemical properties and structural information
- **Features**:
  - Get comprehensive chemical information (name, formula, molar mass, properties)
  - Search compounds by name or formula
  - Calculate molar mass from formula
  - Safety information and handling guidelines
- **API**: Uses PubChem Python library and REST API
- **Authentication**: Free (no API key required)

### 🧮 Wolfram Tool (`backend/tools/wolfram_tool.py`)
- **Purpose**: Chemical calculations and equation balancing
- **Features**:
  - Balance chemical equations
  - Perform stoichiometry calculations
  - Calculate molar mass
  - Solve general chemistry problems
- **API**: Wolfram Alpha API (requires `WOLFRAM_APP_ID`)
- **Fallback**: Basic calculations when API unavailable

### 👁️ Vision/OCR Tool (`backend/tools/vision_tool.py`)
- **Purpose**: Extract text and equations from images
- **Features**:
  - OCR for chemistry diagrams and equations
  - Extract chemical formulas from images
  - Classify diagram types (reactions, structures, graphs)
  - Support for mathematical equations
- **APIs**: 
  - Primary: Mathpix API (requires `MATHPIX_APP_ID`, `MATHPIX_APP_KEY`)
  - Fallback: Gemini Vision API (requires `GEMINI_API_KEY`)

### 🎨 Media Tool (`backend/tools/media_tool.py`)
- **Purpose**: Generate educational content
- **Features**:
  - Generate chemistry concept images
  - Create molecular structure visualizations
  - Generate reaction diagrams
  - Create laboratory equipment diagrams
  - Generate study cards and formula sheets
- **API**: Pollinations.ai (free tier available, optional `POLLINATIONS_API_KEY`)

## FastAPI Backend (`backend/main.py`)

### Endpoints

#### Health & Status
- `GET /` - API status and available tools
- `GET /health` - Tool health check

#### PubChem Endpoints
- `POST /pubchem/info` - Get chemical information
- `POST /pubchem/search` - Search compounds
- `POST /pubchem/molar-mass` - Calculate molar mass

#### Wolfram Endpoints
- `POST /wolfram/balance-equation` - Balance equations
- `POST /wolfram/stoichiometry` - Stoichiometry calculations
- `POST /wolfram/solve-problem` - General chemistry problems

#### Vision Endpoints
- `POST /vision/analyze-image` - Analyze uploaded images

#### Media Endpoints
- `POST /media/generate-image` - Generate concept images
- `POST /media/molecular-structure` - Generate molecular structures
- `POST /media/reaction-diagram` - Generate reaction diagrams

## LLM Router (`backend/core/llm_router.py`)

Intelligent AI orchestrator that:
- Analyzes student questions
- Selects appropriate tools
- Executes tool calls in sequence
- Synthesizes educational responses
- Provides step-by-step explanations

## Configuration (`backend/core/config.py`)

### Required Environment Variables
```bash
# At least one AI API key required
GEMINI_API_KEY=your_gemini_key_here
MISTRAL_API_KEY=your_mistral_key_here

# Optional but recommended
WOLFRAM_APP_ID=your_wolfram_app_id
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key
POLLINATIONS_API_KEY=your_pollinations_key
```

### Optional Configuration
```bash
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG_MODE=false
```

## Installation & Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your API keys

3. **Run backend server**:
   ```bash
   cd backend
   python main.py
   ```

4. **Or run with uvicorn**:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation

Once running, visit:
- **FastAPI Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Integration with Frontend

The backend is designed to work with the existing Streamlit frontend. The LLM router integrates with the modified Gemini brain to provide seamless tool orchestration.

## Tool Status

- ✅ **PubChem**: Fully functional (free)
- ⚠️ **Wolfram**: Requires API key for full functionality
- ⚠️ **Vision**: Requires Mathpix or Gemini API key
- ✅ **Media**: Functional with free Pollinations tier

## Error Handling

All tools include comprehensive error handling with educational fallbacks, ensuring students always receive helpful responses even when tools are unavailable.
