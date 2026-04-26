# 🧪 AI Trợ lý Hóa học

A modern, full-stack AI chemistry assistant built with **Next.js 16**, powered by **Google Gemini 3.1**, featuring real-time streaming, file uploads, and rich Markdown + LaTeX rendering.

> **Live URL**: Deploy to [Vercel](https://vercel.com) by connecting this repo and setting the root directory to `web/`.

---

## ✨ Features

- **🤖 AI Streaming** — Real-time token-by-token responses from Gemini 3.1 Flash Lite
- **📄 File Upload** — Supports PDF, Word (.docx), plain text, and images (PNG, JPG, WebP)
- **📋 Ctrl+V Paste** — Paste images or files directly from your clipboard into the chat
- **🧮 LaTeX / Math Rendering** — Chemical formulas and equations rendered beautifully via KaTeX
- **📝 Markdown Support** — Bold, lists, headings, code blocks — all properly formatted
- **🔐 Auth Shell** — Login and Register pages with NextAuth.js integration
- **💬 Chat History** — Per-session conversation memory with sidebar navigation
- **🌙 Premium Dark UI** — Glassmorphism, Framer Motion animations, and a fully responsive layout

---

## 🗂️ Project Structure

```
ai-chemistry-chatbot/
├── web/                        # ✅ Active Next.js Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Landing page
│   │   │   ├── login/          # Login page
│   │   │   ├── register/       # Register page
│   │   │   ├── chat/           # Main chat interface
│   │   │   ├── api/
│   │   │   │   ├── chat/       # Gemini AI streaming endpoint
│   │   │   │   └── auth/       # NextAuth.js handler
│   │   │   └── globals.css     # Design system (glassmorphism, KaTeX)
│   │   └── lib/
│   │       └── file-parser.ts  # Server-side PDF & Word parser
│   ├── .env                    # API keys (see setup below)
│   └── package.json
│
└── python_legacy/              # 🗃️ Original Streamlit app (archived)
    ├── src/brain.py
    └── ui/app.py
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 20+
- A [Google AI Studio](https://aistudio.google.com/app/apikey) API key

### 1. Clone and Install

```bash
git clone https://github.com/Uchilong/ai-chemistry-chatbot.git
cd ai-chemistry-chatbot/web
npm install
```

### 2. Set up Environment Variables

Create `web/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
NEXTAUTH_SECRET=your_random_secret_here
NEXTAUTH_URL=http://localhost:3000
```

### 3. Run Locally

```bash
cd web
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧠 AI Model

This app uses **`gemini-3.1-flash-lite-preview`** by default, with **`gemini-3.1-pro-preview`** available as an option in the chat interface.

Supported models on this API key:
- `gemini-3.1-flash-lite-preview` ⚡ (Default — fast, efficient)
- `gemini-3.1-pro-preview` 🧠 (Advanced reasoning)

---

## 📁 File Support

| File Type | Extension | Handling |
|-----------|-----------|----------|
| Images | `.jpg`, `.png`, `.webp`, `.gif` | Sent directly to Gemini vision API |
| PDF | `.pdf` | Parsed server-side with `pdf-parse` |
| Word | `.docx` | Parsed server-side with `mammoth` |
| Text | `.txt` | Read as UTF-8 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| AI | Google Generative AI (`@google/generative-ai`) |
| Auth | NextAuth.js |
| Styling | Tailwind CSS v4 + Custom Glassmorphism |
| Animations | Framer Motion |
| Icons | Lucide React |
| Markdown | `react-markdown` + `remark-gfm` |
| Math | `rehype-katex` + `remark-math` |
| File Parsing | `mammoth` (Word), `pdf-parse` (PDF) |

---

## ☁️ Deploy to Vercel

1. Push this repo to GitHub
2. Connect to [Vercel](https://vercel.com)
3. Set **Root Directory** → `web`
4. Add Environment Variables:
   - `GEMINI_API_KEY`
   - `NEXTAUTH_SECRET`
   - `NEXTAUTH_URL` (your Vercel URL)
5. Deploy!

---

## 📜 Legacy Python App

The original Streamlit chatbot is preserved in [`python_legacy/`](./python_legacy/). To run it:

```bash
pip install -r python_legacy/requirements.txt
streamlit run python_legacy/ui/app.py
```

---

## 📄 License

MIT © [Uchilong](https://github.com/Uchilong)
