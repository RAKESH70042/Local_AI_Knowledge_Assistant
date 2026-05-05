// components/ChatMessage.js
import { useState } from 'react';

export default function ChatMessage({ message, isLast }) {
  const [showExtracted, setShowExtracted] = useState(false);
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        margin: '8px 0',
      }}>
        <span style={{
          fontSize: 12,
          color: 'var(--text-muted)',
          background: 'var(--bg-hover)',
          padding: '3px 10px',
          borderRadius: 20,
          border: '1px solid var(--border)',
        }}>
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div
      className={isLast ? 'fade-in' : ''}
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 10,
        padding: '4px 0',
        alignItems: 'flex-start',
      }}
    >
      {/* Avatar */}
      <div style={{
        width: 32,
        height: 32,
        borderRadius: 8,
        background: isUser ? 'var(--accent)' : '#f1f0ec',
        border: isUser ? 'none' : '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 15,
        flexShrink: 0,
        marginTop: 2,
      }}>
        {isUser ? '🧑' : '🤖'}
      </div>

      {/* Bubble */}
      <div style={{ maxWidth: '72%', minWidth: 60 }}>
        {/* File attachment badge */}
        {message.fileName && (
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5,
            background: 'var(--bg-hover)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            padding: '4px 9px',
            fontSize: 12,
            color: 'var(--text-secondary)',
            marginBottom: 5,
          }}>
            <span>{getFileIcon(message.fileName)}</span>
            <span>{message.fileName}</span>
            {message.extractedText && (
              <button
                onClick={() => setShowExtracted(!showExtracted)}
                style={{
                  marginLeft: 4,
                  background: 'var(--accent-light)',
                  color: 'var(--accent)',
                  border: 'none',
                  borderRadius: 4,
                  padding: '1px 6px',
                  fontSize: 11,
                  cursor: 'pointer',
                  fontFamily: 'var(--font)',
                }}
              >
                {showExtracted ? 'Hide text' : 'Show extracted text'}
              </button>
            )}
          </div>
        )}

        {/* Extracted text preview */}
        {showExtracted && message.extractedText && (
          <div style={{
            background: '#fafaf8',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 12px',
            fontSize: 12,
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-secondary)',
            maxHeight: 200,
            overflowY: 'auto',
            marginBottom: 6,
            whiteSpace: 'pre-wrap',
            lineHeight: 1.5,
          }}>
            {message.extractedText.substring(0, 1500)}
            {message.extractedText.length > 1500 && (
              <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                {'\n\n'}… ({message.extractedText.length - 1500} more chars)
              </span>
            )}
          </div>
        )}

        {/* Message bubble */}
        <div style={{
          background: isUser ? 'var(--accent)' : 'var(--bg-card)',
          color: isUser ? 'white' : 'var(--text-primary)',
          border: isUser ? 'none' : '1px solid var(--border)',
          borderRadius: isUser
            ? '14px 14px 4px 14px'
            : '14px 14px 14px 4px',
          padding: '10px 14px',
          fontSize: 14,
          lineHeight: 1.65,
          boxShadow: 'var(--shadow-sm)',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {message.loading ? (
            <span style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
              <span style={{ animation: 'blink 1s infinite 0s', fontSize: 18 }}>•</span>
              <span style={{ animation: 'blink 1s infinite 0.2s', fontSize: 18 }}>•</span>
              <span style={{ animation: 'blink 1s infinite 0.4s', fontSize: 18 }}>•</span>
            </span>
          ) : (
            <>
  {message.content}

  {!isUser && message.sources?.length > 0 && (
    <details style={{
      marginTop: 10,
      borderTop: '1px solid var(--border)',
      paddingTop: 8
    }}>
      <summary style={{
        cursor:'pointer',
        fontSize:12,
        fontWeight:600
      }}>
        Sources ({message.sources.length})
      </summary>

      <ul style={{
        marginTop:8,
        paddingLeft:18,
        fontSize:12
      }}>
        {message.sources.map((src,i)=>(
          <li key={i}>{src}</li>
        ))}
      </ul>
    </details>
  )}
</>
          )}
        </div>

        {/* Timestamp */}
        {message.timestamp && (
          <div style={{
            fontSize: 11,
            color: 'var(--text-muted)',
            marginTop: 3,
            textAlign: isUser ? 'right' : 'left',
          }}>
            {message.timestamp}
          </div>
        )}
      </div>
    </div>
  );
}

function getFileIcon(filename) {
  const ext = filename?.split('.').pop()?.toLowerCase();
  const icons = {
    pdf: '📄', docx: '📝', doc: '📝', txt: '📃',
    csv: '📊', xlsx: '📊', xls: '📊',
    png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️',
    json: '🔧', md: '📋',
  };
  return icons[ext] || '📎';
}
