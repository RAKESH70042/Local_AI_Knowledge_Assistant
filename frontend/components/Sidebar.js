// components/Sidebar.js
import { useState } from 'react';

export default function Sidebar({ sessions, activeId, onNew, onSelect, onDelete, backendStatus }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside style={{
      width: collapsed ? 56 : 'var(--sidebar-width)',
      minWidth: collapsed ? 56 : 'var(--sidebar-width)',
      background: 'var(--bg-card)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      transition: 'width 0.2s ease, min-width 0.2s ease',
      overflow: 'hidden',
      zIndex: 10,
    }}>
      {/* Header */}
      <div style={{
        padding: collapsed ? '16px 12px' : '16px 16px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        gap: 8,
      }}>
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 28, height: 28,
              background: 'var(--accent)',
              borderRadius: 7,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 14,
            }}>🧠</div>
            <span style={{ fontWeight: 600, fontSize: 14 }}>AI Assistant</span>
          </div>
        )}
        <button
          className="btn btn-ghost btn-icon"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand' : 'Collapse'}
          style={{ flexShrink: 0 }}
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* New Chat Button */}
      <div style={{ padding: collapsed ? '10px 8px' : '10px 12px' }}>
        <button
          className="btn btn-primary"
          onClick={onNew}
          style={{ width: '100%', justifyContent: collapsed ? 'center' : 'flex-start' }}
          title="New Chat"
        >
          <span>✏️</span>
          {!collapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Session List */}
      {!collapsed && (
        <div style={{ flex: 1, overflowY: 'auto', padding: '4px 8px' }}>
          {sessions.length === 0 && (
            <div style={{
              padding: '24px 12px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: 13,
            }}>
              No chats yet.<br />Start a conversation!
            </div>
          )}
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => onSelect(s.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                background: activeId === s.id ? 'var(--accent-light)' : 'transparent',
                border: `1px solid ${activeId === s.id ? '#bfdbfe' : 'transparent'}`,
                marginBottom: 2,
                transition: 'all 0.12s',
                gap: 6,
              }}
              onMouseEnter={(e) => {
                if (activeId !== s.id) e.currentTarget.style.background = 'var(--bg-hover)';
              }}
              onMouseLeave={(e) => {
                if (activeId !== s.id) e.currentTarget.style.background = 'transparent';
              }}
            >
              <div style={{ flex: 1, overflow: 'hidden' }}>
                <div style={{
                  fontSize: 13,
                  fontWeight: activeId === s.id ? 500 : 400,
                  color: activeId === s.id ? 'var(--accent)' : 'var(--text-primary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  💬 {s.title || 'New Chat'}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  {s.messageCount || 0} messages
                </div>
              </div>
              <button
                className="btn btn-ghost btn-icon btn-sm"
                onClick={(e) => { e.stopPropagation(); onDelete(s.id); }}
                title="Delete"
                style={{ opacity: 0.5, fontSize: 11, padding: 4 }}
              >🗑️</button>
            </div>
          ))}
        </div>
      )}

      {/* Status Footer */}
      {!collapsed && (
        <div style={{
          padding: '10px 14px',
          borderTop: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          fontSize: 12,
          color: 'var(--text-muted)',
        }}>
          <span style={{
            width: 7, height: 7,
            borderRadius: '50%',
            background: backendStatus === 'online' ? 'var(--success)' : backendStatus === 'checking' ? 'var(--warning)' : '#dc2626',
            animation: backendStatus === 'checking' ? 'pulse 1.5s infinite' : 'none',
            flexShrink: 0,
          }} />
          Backend: {backendStatus === 'online' ? 'Connected' : backendStatus === 'checking' ? 'Checking…' : 'Offline'}
        </div>
      )}
    </aside>
  );
}
