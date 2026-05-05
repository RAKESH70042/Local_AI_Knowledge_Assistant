// components/ExportMenu.js
import { useState, useRef, useEffect } from 'react';
import { exportToCSV, exportToExcel, exportToDocx } from '../utils/exportChat';

export default function ExportMenu({ messages, sessionTitle }) {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filename = (sessionTitle || 'chat-export')
    .replace(/[^a-z0-9]/gi, '-')
    .toLowerCase()
    .substring(0, 40);

  const doExport = async (type) => {
    setExporting(type);
    setOpen(false);
    try {
      if (type === 'csv') await exportToCSV(messages, filename);
      if (type === 'xlsx') await exportToExcel(messages, filename);
      if (type === 'docx') await exportToDocx(messages, filename);
    } catch (err) {
      alert('Export failed: ' + err.message);
    }
    setExporting(null);
  };

  const formats = [
    { id: 'docx', label: 'Word Document (.docx)', icon: '📝', desc: 'Formatted with headers' },
    { id: 'xlsx', label: 'Excel Spreadsheet (.xlsx)', icon: '📊', desc: 'Table format' },
    { id: 'csv', label: 'CSV File (.csv)', icon: '📃', desc: 'Plain text table' },
  ];

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        className="btn btn-secondary btn-sm"
        onClick={() => setOpen(!open)}
        disabled={messages.length === 0}
        title="Export chat"
      >
        {exporting ? '⏳' : '⬇️'} Export
      </button>

      {open && (
        <div
          className="fade-in"
          style={{
            position: 'absolute',
            right: 0,
            top: 'calc(100% + 6px)',
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow-lg)',
            minWidth: 220,
            zIndex: 100,
            overflow: 'hidden',
          }}
        >
          <div style={{
            padding: '8px 12px 6px',
            fontSize: 11,
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            borderBottom: '1px solid var(--border)',
          }}>
            Export as…
          </div>
          {formats.map((f) => (
            <button
              key={f.id}
              onClick={() => doExport(f.id)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
                width: '100%',
                padding: '9px 12px',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'background 0.1s',
                fontFamily: 'var(--font)',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <span style={{ fontSize: 18, lineHeight: 1 }}>{f.icon}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{f.label}</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>{f.desc}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
