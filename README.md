# 🤖 Local AI Knowledge Assistant

Ask questions about your own documents — everything runs **100% on your PC**.  
No cloud, no API keys, no internet needed after setup.

---

## 🗂️ Project Structure

```
local-ai-assistant/
├── backend/                  # FastAPI Python server
│   ├── core/                 # AI pipeline modules
│   │   ├── parser.py         # File text extraction
│   │   ├── chunker.py        # Split text into chunks
│   │   ├── embeddings.py     # Convert text → vectors
│   │   ├── vectorstore.py    # ChromaDB storage & search
│   │   ├── llm.py            # Talk to Ollama
│   │   └── pipeline.py       # Connect everything together
│   ├── data/
│   │   ├── docs/             # Put your documents here
│   │   └── chroma_db/        # Vector DB (auto-created)
│   ├── main.py               # FastAPI app & routes
│   └── requirements.txt
├── frontend/                 # Next.js UI
│   ├── app/
│   │   └── page.js           # Main chat page
│   ├── components/           # React components
│   └── package.json
├── .env                      # Your config (never commit this)
└── README.md
```

---

## ⚙️ Requirements

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed on your PC
- ~1 GB RAM free

---

## 🚀 Setup — Step by Step

### Step 1 — Install Ollama & pull the model
```bash
# Download from https://ollama.com then run:
ollama pull qwen2.5:0.5b
```

### Step 2 — Set up Python backend
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3 — Configure your .env
```bash
# Copy the example and edit as needed
cp ../.env .env
```

### Step 4 — Add your documents
```bash
# Put any .pdf, .docx, .txt, .csv, .md files here:
mkdir -p data/docs
# copy your files into backend/data/docs/
```

### Step 5 — Index your documents
```bash
python -m core.pipeline index
```

### Step 6 — Start the backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 7 — Start the frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```

### Step 8 — Open in browser
```
http://localhost:3000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check server + chunk count |
| POST | `/ask` | Ask a question |
| POST | `/upload` | Upload & index a file |
| POST | `/reindex` | Rebuild the full index |
| GET | `/history` | All past Q&A |
| DELETE | `/history` | Clear all history |
| GET | `/export/word` | Download chat as Word |
| GET | `/export/excel` | Download chat as Excel |

---

## 💡 Tips

- The smaller the model (`qwen2.5:0.5b`), the faster but less detailed the answers
- Add more documents to `data/docs/` and hit `/reindex` to update the AI's knowledge
- ChromaDB is stored in `data/chroma_db/` — delete this folder to start fresh
