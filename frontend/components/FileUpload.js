// components/FileUpload.js
import { useState, useRef } from 'react';

const API = 'http://localhost:8000';

export default function FileUpload({ onFilesReady, disabled }) {
  const [dragging,    setDragging]    = useState(false);
  const [processing,  setProcessing]  = useState(false);
  const inputRef = useRef(null);

  const ACCEPTED = '.pdf,.doc,.docx,.txt,.csv,.json,.md,.png,.jpg,.jpeg,.xlsx,.xls';

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return;
    setProcessing(true);
    const results = [];

    for (const file of Array.from(files)) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${API}/upload`, {
          method: 'POST',
          body:   formData,
        });

        if (!res.ok) throw new Error(`Upload failed: ${res.status}`);

        const data = await res.json();

        results.push({
          name:          file.name,
          storedName:    data.filename,                        // stamped name e.g. "20260504_Fennex.pdf"
          size:          file.size,
          extractedText: data.extracted_text || '',           // ← real text from backend
          indexed:       true,
        });

      } catch (err) {
        results.push({
          name:          file.name,
          size:          file.size,
          extractedText: '',
          error:         err.message,
        });
      }
    }

    setProcessing(false);
    onFilesReady(results);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !disabled && !processing && inputRef.current?.click()}
        style={{
          border:       `2px dashed ${dragging ? 'var(--accent)' : 'var(--border)'}`,
          borderRadius: 'var(--radius)',
          padding:      '20px 16px',
          textAlign:    'center',
          cursor:       disabled || processing ? 'not-allowed' : 'pointer',
          background:   dragging ? 'var(--accent-light)' : 'var(--bg)',
          transition:   'all 0.15s',
          opacity:      disabled ? 0.6 : 1,
        }}
      >
        <div style={{ fontSize: 28, marginBottom: 6 }}>
          {processing ? '⏳' : dragging ? '📂' : '📁'}
        </div>
        <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 3 }}>
          {processing ? 'Uploading and indexing…' : dragging ? 'Drop to attach' : 'Upload a file'}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          PDF, DOCX, TXT, CSV, JSON, Images
        </div>
        {!processing && (
          <div style={{
            display:      'inline-block',
            marginTop:    8,
            padding:      '4px 10px',
            background:   'var(--bg-card)',
            border:       '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            fontSize:     12,
            color:        'var(--text-secondary)',
          }}>
            Browse files
          </div>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPTED}
        style={{ display: 'none' }}
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}