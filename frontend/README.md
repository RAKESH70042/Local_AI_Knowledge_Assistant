# 🧠 AI Knowledge Assistant — Frontend (Phase 6)

A clean, minimal Next.js frontend for your Local AI Knowledge Assistant backend.

## Features
- 💬 Chat interface with session history
- 📁 Document upload with text extraction (PDF, DOCX, TXT, CSV, JSON, Images)
- 📤 Export chat as DOCX, Excel (.xlsx), or CSV
- 🗂️ Multiple chat sessions (saved in localStorage)
- ✅ Backend status indicator

---

## Setup & Run

### 1. Place this folder
```
AI_2/
├── backend/          ← your FastAPI (Phase 5)
└── frontend/         ← this folder
```

### 2. Install dependencies
```cmd
cd C:\Users\rv747\AI_2\frontend
npm install
```

### 3. Start the frontend
```cmd
npm run dev
```
Open: http://localhost:3000

### 4. Make sure backend is running too
```cmd
cd C:\Users\rv747\AI_2\backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Backend API Expected

Your FastAPI backend should have:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/`      | GET    | Health check |
| `/health`| GET    | Health check |
| `/chat`  | POST   | Chat endpoint |

### `/chat` Request Body:
```json
{
  "message": "User's question",
  "history": [{"role": "user", "content": "..."}],
  "context": "Extracted file text (optional)",
  "filename": "uploaded-file.pdf (optional)"
}
```

### `/chat` Response:
```json
{
  "response": "Assistant's reply"
}
```

---

## Export Formats
- **DOCX** — Formatted Word document with colored headers
- **XLSX** — Excel spreadsheet, one row per message
- **CSV** — Plain text, comma-separated

## File Text Extraction
Supported client-side extraction:
- PDF → pdfjs-dist
- DOCX → mammoth
- TXT/CSV/MD/JSON → plain text read
- Images → note displayed (OCR requires backend)
## ⚠️ Ethical & Safe AI Usage

This assistant is built for internal knowledge retrieval only.
Please follow these guidelines when using it:

### ✅ Intended Use
- Querying internal documents and knowledge bases
- Summarizing and extracting information from uploaded files
- Assisting engineers with onboarding and documentation

### ❌ Do Not Use For
- Generating or spreading misinformation
- Processing personally identifiable information (PII)
- Making critical decisions without human review
- Sharing confidential data with external systems

### 🔒 Privacy & Data
- All data stays 100% local on your PC — nothing is sent to the cloud
- Sensitive information (emails, phone numbers, IDs) is automatically
  redacted from responses
- Do not upload files containing passwords or secret keys

### 🤖 AI Limitations
- The model may produce incorrect or incomplete answers
- Always verify important information from the original source
- Citations show which documents were used — always check them
- Smaller models (0.5b) are less accurate than larger ones

### 📋 Responsible Use
- This tool augments human decision-making, it does not replace it
- Report any unexpected or harmful outputs to your team lead