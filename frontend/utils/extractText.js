// utils/extractText.js
// Extracts text from PDF, DOCX, TXT, and image files in the browser

export async function extractTextFromFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();

  try {
    if (ext === 'txt' || ext === 'md' || ext === 'csv') {
      return await readAsText(file);
    }

    if (ext === 'pdf') {
      return await extractFromPDF(file);
    }

    if (ext === 'docx' || ext === 'doc') {
      return await extractFromDOCX(file);
    }

    if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) {
      return `[Image file: ${file.name}]\nImage uploaded. Text extraction from images requires OCR support on the backend.`;
    }

    if (ext === 'json') {
      const text = await readAsText(file);
      try {
        const parsed = JSON.parse(text);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return text;
      }
    }

    return `[File: ${file.name}]\nFile type .${ext} — content preview not available.`;
  } catch (err) {
    console.error('Text extraction error:', err);
    return `[Could not extract text from ${file.name}: ${err.message}]`;
  }
}

function readAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

async function extractFromPDF(file) {
  const arrayBuffer = await file.arrayBuffer();
  
  // Dynamically import pdfjs to avoid SSR issues
  const pdfjsLib = await import('pdfjs-dist/build/pdf');
  pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  let fullText = '';

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const pageText = content.items.map((item) => item.str).join(' ');
    fullText += `--- Page ${i} ---\n${pageText}\n\n`;
  }

  return fullText.trim() || '[No text found in PDF]';
}

async function extractFromDOCX(file) {
  const arrayBuffer = await file.arrayBuffer();
  const mammoth = await import('mammoth');
  const result = await mammoth.extractRawText({ arrayBuffer });
  return result.value.trim() || '[No text found in DOCX]';
}
