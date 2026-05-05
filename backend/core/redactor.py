"""
redactor.py
-----------
Redacts sensitive information like emails, phone numbers, and IDs
from text before storing or returning it.
"""

import re

# ── Patterns ──────────────────────────────────────────────────────────────────

PATTERNS = {
    "email":   (r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "[EMAIL]"),
    "phone":   (r'(\+?\d[\d\s\-().]{7,}\d)',                          "[PHONE]"),
    "aadhaar": (r'\b\d{4}\s?\d{4}\s?\d{4}\b',                        "[ID]"),
    "pan":     (r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',                        "[PAN]"),
}


# ── Core Redact Function ───────────────────────────────────────────────────────

def redact(text: str) -> str:
    """
    Redact sensitive information from text.
    
    Args:
        text: Input text string.
    
    Returns:
        Redacted text with sensitive info replaced by placeholders.
    """
    if not text:
        return text

    for name, (pattern, placeholder) in PATTERNS.items():
        text = re.sub(pattern, placeholder, text)

    return text


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    Contact John at john.doe@company.com or call +91 98765 43210.
    His Aadhaar is 1234 5678 9012 and PAN is ABCDE1234F.
    """
    print("Original:")
    print(sample)
    print("Redacted:")
    print(redact(sample))