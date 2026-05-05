"""
parser.py
---------
Reads and cleans documents from the data/docs folder.
Supports: .md, .txt, .pdf, .docx, .csv
"""

import os
import re
import json
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
import os

DOCS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "data",
        "docs"
    )
)


# ── Optional imports ──────────────────────────────────────────────────────────

try:
    import pdfplumber
    PDFPLUMBER_OK = True
except ImportError:
    PDFPLUMBER_OK = False

try:
    import fitz
    PYMUPDF_OK = True
except ImportError:
    PYMUPDF_OK = False

try:
    import docx2txt
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False


# ── Text Cleaning ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', text)
    return text.strip()


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return clean_text(f.read())


def parse_pdf(filepath: str) -> str:
    if PDFPLUMBER_OK:
        try:
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return clean_text(text)
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e} — trying PyMuPDF")

    if PYMUPDF_OK:
        doc = fitz.open(filepath)
        text = "\n".join(page.get_text() for page in doc)
        return clean_text(text)

    raise ImportError("No PDF parser available. Run: pip install pdfplumber pymupdf")


def parse_docx(filepath: str) -> str:
    if not DOCX_OK:
        raise ImportError("Run: pip install docx2txt")
    return clean_text(docx2txt.process(filepath))


def parse_csv(filepath: str) -> str:
    if not PANDAS_OK:
        raise ImportError("Run: pip install pandas")
    df = pd.read_csv(filepath).fillna("")
    lines = []
    for _, row in df.iterrows():
        parts = [f"{col}: {val}" for col, val in row.items() if str(val).strip()]
        if parts:
            lines.append(", ".join(parts))
    return clean_text("\n".join(lines))
def parse_odt(filepath: str) -> str:
    try:
        from odf import teletype
        from odf.opendocument import load
        doc = load(filepath)
        alltext = teletype.extractText(doc.text)
        return clean_text(alltext)
    except ImportError:
        raise ImportError("Run: pip install odfpy")

# ── Router ────────────────────────────────────────────────────────────────────

PARSERS = {
    ".md":   parse_txt,
    ".txt":  parse_txt,
    ".pdf":  parse_pdf,
    ".docx": parse_docx,
    ".csv":  parse_csv,
    ".odt":  parse_odt,  
}

SUPPORTED_EXTENSIONS = set(PARSERS.keys())


def parse_file(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in PARSERS:
        raise ValueError(f"Unsupported file type: '{ext}'")
    return PARSERS[ext](filepath)



def load_metadata(filepath: str) -> dict:
    base = os.path.splitext(filepath)[0]
    meta_path = base + ".meta.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metadata: {e}")
    return {}


def load_all_documents(docs_dir: str = DOCS_DIR) -> list[dict]:
    if not os.path.exists(docs_dir):
        logger.error(f"DOCS_DIR does not exist: {docs_dir}")
        return []

    documents = []

    for fname in sorted(os.listdir(docs_dir)):
        print("Parser reading from:", docs_dir)
        print("Files seen:", os.listdir(docs_dir))
        ext = os.path.splitext(fname)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS or fname.startswith("."):
            continue

        filepath = os.path.join(docs_dir, fname)

        try:
            text = parse_file(filepath)
            if not text.strip():
                logger.warning(f"  ⚠ Empty: {fname} — skipping")
                continue

            meta = load_metadata(filepath)
            documents.append({
                "filepath": filepath,
                "filename": fname,
                "text":     text,
                "metadata": meta,
            })
            logger.info(f"  ✓ Parsed: {fname}  ({len(text):,} chars)")

        except Exception as e:
            logger.error(f"  ✗ Failed: {fname} → {e}")

    return documents


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nScanning: {DOCS_DIR}\n")
    docs = load_all_documents()

    if not docs:
        print("No documents found. Add files to:", DOCS_DIR)
    else:
        print(f"\nTotal loaded: {len(docs)} document(s)\n")
        for doc in docs:
            print(f"  {doc['filename']}  —  {len(doc['text']):,} chars")
        print(f"\nPreview ({docs[0]['filename']}):")
        print(docs[0]["text"][:400])

        