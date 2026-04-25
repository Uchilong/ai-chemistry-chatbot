# 🧪 AI Chemistry Chatbot

A comprehensive AI-powered chemistry tutor and calculation assistant built with multiple AI models and specialized chemistry tools.

## 🎯 What This Does

The AI Chemistry Chatbot is an intelligent learning assistant that helps students and educators with:

- **📚 Chemistry Tutoring**: Interactive Q&A about chemical concepts, reactions, and principles
- **🧮 Chemical Calculations**: Equation balancing, molar mass calculations, and stoichiometry
- **🎨 Visual Learning**: Generate chemistry diagrams and illustrations
- **📁 File Analysis**: OCR for chemical formulas from images and PDFs
- **💾 Personal Learning**: Save resources, track progress, and maintain chat history

## 🚀 Key Features

### 🤖 Multi-Model AI Support
- **Gemini (Accurate)**: Advanced reasoning with image analysis
- **Mistral (Fast)**: Quick text responses for basic questions
- **Groq (Ultra Fast)**: Lightning-fast responses for simple queries
- **Ollama (Local)**: Privacy-focused local model option

### 🔬 Chemistry Tools
- **Equation Balancing**: Balance chemical equations with step-by-step solutions
- **Molar Mass Calculator**: Calculate molecular weights for 20+ common compounds
- **Stoichiometry**: Basic mole ratio calculations (g ↔ mol conversions)
- **Image Generation**: Create chemistry diagrams and illustrations

### 📱 User Features
- **Account System**: Gmail-based login for personalized experience
- **Resource Library**: Save and organize learning materials
- **Chat History**: Access previous questions and conversations
- **File Upload**: Analyze images and PDFs with OCR capabilities

## 🛠️ Tech Stack

### Backend
- **Python**: Core programming language
- **FastAPI**: RESTful API framework
- **SQLite**: User data and chat history storage
- **Multiple AI APIs**: Gemini, Mistral, Groq, Ollama integration

### Frontend
- **Streamlit**: Web interface framework
- **Responsive Design**: Mobile-friendly layout
- **Real-time Chat**: Interactive messaging system

### External Services
- **Pollinations AI**: Image generation
- **Wolfram Alpha**: Advanced calculations (optional)
- **EasyOCR**: Text recognition from images

## 📋 Tool Limitations

### ✅ What Works Well
- Basic chemistry tutoring and Q&A
- Simple equation balancing (H₂ + O₂ → H₂O)
- Molar mass calculations for common compounds
- Image generation for basic chemistry concepts
- File analysis for chemical formulas

### ❌ Current Limitations
- Complex stoichiometry (C₄H₁₀ + O₂ → CO₂ + H₂O)
- Advanced chemical calculations
- 3D molecular structures
- Video/audio file analysis
- Real-time chemical simulations

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git for cloning the repository

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-chemistry-chatbot.git
   cd ai-chemistry-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   streamlit run ui/app.py
   ```

### 🔑 API Keys Required

Add these to your `.env` file:

```bash
# Required for basic functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Optional but recommended
MISTRAL_API_KEY=your_mistral_api_key_here
GROQ_API_KEY=your_groq_api_key_here
WOLFRAM_APP_ID=your_wolfram_app_id_here
POLLINATIONS_API_KEY=your_pollinations_api_key_here
```

### 📍 Where to Get API Keys

- **Gemini**: https://aistudio.google.com/app/apikey
- **Mistral**: https://console.mistral.ai/api-keys/
- **Groq**: https://console.groq.com/keys
- **Wolfram Alpha**: https://developer.wolframalpha.com/
- **Pollinations**: https://pollinations.ai/

## 🎯 Usage Examples

### Chemistry Tutoring
```
User: What is the difference between ionic and covalent bonds?
AI: Ionic bonds involve transfer of electrons between atoms...
```

### Equation Balancing
```
User: Balance: Fe + O2 -> Fe2O3
AI: 4Fe + 3O2 → 2Fe₂O₃
```

### Molar Mass Calculation
```
User: Calculate molar mass of H2SO4
AI: 98.079 g/mol
```

### Image Generation
```
User: Show me a water molecule
AI: [Generates H₂O diagram]
```

## 🏗️ Project Structure

```
ai-chemistry-chatbot/
├── ui/                 # Streamlit frontend
│   └── app.py          # Main web interface
├── backend/            # FastAPI backend
│   ├── tools/          # Chemistry tools
│   └── core/           # Configuration
├── src/                # AI brains and logic
├── data/               # Database files
├── .env.example        # Environment template
└── requirements.txt    # Dependencies
```

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Development Mode
```bash
# Backend
uvicorn backend.main:app --reload

# Frontend
streamlit run ui/app.py --server.port 8501
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the limitations section above
- Ensure all API keys are properly configured

---

**🧪 Built for the AI Chemistry Hackathon**  
*Making chemistry education accessible and interactive*
