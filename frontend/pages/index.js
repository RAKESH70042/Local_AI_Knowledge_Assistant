// pages/index.js
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Sidebar from '../components/Sidebar';
import ChatMessage from '../components/ChatMessage';
import ExportMenu from '../components/ExportMenu';
import FileUpload from '../components/FileUpload';

const API = 'http://localhost:8000';
const API_TOKEN = 'my-secret-key-123';

function genId() {
  return Math.random().toString(36).slice(2, 10);
}

function timestamp() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function createSession() {
  return { id: genId(), title: 'New Chat', messages: [], createdAt: new Date().toISOString() };
}

export default function Home() {
  const [sessions, setSessions]           = useState([]);
  const [activeId, setActiveId]           = useState(null);
  const [input, setInput]                 = useState('');
  const [loading, setLoading]             = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [showUpload, setShowUpload]       = useState(false);
  const [pendingFiles, setPendingFiles]   = useState([]);

  const messagesEndRef = useRef(null);
  const textareaRef    = useRef(null);

  const activeSession = sessions.find((s) => s.id === activeId);
  const messages      = activeSession?.messages || [];

  // Init
  useEffect(() => {
    const saved = localStorage.getItem('ai_sessions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSessions(parsed);
        if (parsed.length > 0) setActiveId(parsed[0].id);
      } catch {}
    } else {
      const s = createSession();
      setSessions([s]);
      setActiveId(s.id);
    }
    checkBackend();
  }, []);

  // Save sessions
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('ai_sessions', JSON.stringify(sessions));
    }
  }, [sessions]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function checkBackend() {
    try {
      await axios.get(`${API}/health`, {
        timeout: 3000,
        headers: { 'X-API-Token': API_TOKEN },
      });
      setBackendStatus('online');
    } catch {
      setBackendStatus('offline');
    }
  }

  function updateSession(id, updater) {
    setSessions((prev) => prev.map((s) => (s.id === id ? updater(s) : s)));
  }

  function addMessage(sessionId, msg) {
    updateSession(sessionId, (s) => {
      const newMsgs = [...s.messages, msg];
      const title =
        s.title === 'New Chat' && msg.role === 'user'
          ? (msg.content || msg.fileName || 'Chat').substring(0, 36)
          : s.title;
      return { ...s, messages: newMsgs, title, messageCount: newMsgs.length };
    });
  }

  function updateLastMessage(sessionId, patch) {
    updateSession(sessionId, (s) => {
      const msgs = [...s.messages];
      msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], ...patch };
      return { ...s, messages: msgs };
    });
  }

  async function sendMessage() {
    const text = input.trim();
    if (!text && pendingFiles.length === 0) return;
    if (!activeId) return;
    if (loading) return;

    const userMsg = {
      id:            genId(),
      role:          'user',
      content:       text,
      timestamp:     timestamp(),
      fileName:      pendingFiles.length > 0 ? pendingFiles.map((f) => f.name).join(', ') : undefined,
      storedName:    pendingFiles.length > 0 ? pendingFiles.map((f) => f.storedName).join(', ') : undefined,
      extractedText: pendingFiles.length > 0 ? pendingFiles.map((f) => f.extractedText).join('\n\n---\n\n') : undefined,
    };

    addMessage(activeId, userMsg);
    setInput('');
    setPendingFiles([]);
    setShowUpload(false);
    setLoading(true);

    const loadingMsg = { id: genId(), role: 'assistant', content: '', loading: true, timestamp: timestamp() };
    addMessage(activeId, loadingMsg);

    try {
      const payload = {
        message: text || '[File uploaded]',
        history: messages.slice(-10).map((m) => ({ role: m.role, content: m.content })),
      };

      if (userMsg.extractedText) {
        payload.context  = userMsg.extractedText;
        payload.filename = userMsg.storedName || userMsg.fileName;
      }

      const response = await fetch(`${API}/stream`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Token': API_TOKEN },
        body:    JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const reader  = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText  = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullText += decoder.decode(value);
        updateLastMessage(activeId, { content: fullText, loading: false });
      }
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Could not reach backend.';
      updateLastMessage(activeId, {
        content:  ` Error: ${errMsg}\n\n_Make sure your FastAPI backend is running at ${API}_`,
        loading:  false,
      });
      setBackendStatus('offline');
    }

    setLoading(false);
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function handleFilesReady(files) {
    setPendingFiles((prev) => [...prev, ...files]);
    setShowUpload(false);
  }

  function newSession() {
    const s = createSession();
    setSessions((prev) => [s, ...prev]);
    setActiveId(s.id);
  }

  function deleteSession(id) {
    setSessions((prev) => {
      const next = prev.filter((s) => s.id !== id);
      if (activeId === id && next.length > 0) setActiveId(next[0].id);
      else if (next.length === 0) {
        const s = createSession();
        setActiveId(s.id);
        return [s];
      }
      return next;
    });
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>

      {/* Sidebar */}
      <Sidebar
        sessions={sessions.map((s) => ({ ...s, messageCount: s.messages?.length || 0 }))}
        activeId={activeId}
        onNew={newSession}
        onSelect={setActiveId}
        onDelete={deleteSession}
        backendStatus={backendStatus}
      />

      {/* Main */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>

        {/* Top Bar */}
        <header style={{
          padding:        '0 16px',
          height:         52,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'space-between',
          borderBottom:   '1px solid var(--border)',
          background:     'var(--bg-card)',
          flexShrink:     0,
          gap:            12,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0 }}>
            <span style={{
              fontSize:     14,
              fontWeight:   600,
              color:        'var(--text-primary)',
              overflow:     'hidden',
              textOverflow: 'ellipsis',
              whiteSpace:   'nowrap',
            }}>
              {activeSession?.title || 'New Chat'}
            </span>
            {messages.length > 0 && (
              <span className="badge badge-gray">{messages.length} msgs</span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
            <button
              className="btn btn-ghost btn-icon btn-sm"
              onClick={checkBackend}
              title="Check backend"
            >🔄</button>
            <ExportMenu messages={messages} sessionTitle={activeSession?.title} />
          </div>
        </header>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 2 }}>
          {messages.length === 0 && (
            <div style={{
              flex:           1,
              display:        'flex',
              flexDirection:  'column',
              alignItems:     'center',
              justifyContent: 'center',
              gap:            12,
              color:          'var(--text-muted)',
              textAlign:      'center',
            }}>
              <div style={{ fontSize: 48 }}>🧠</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: 'var(--text-primary)' }}>
                AI Knowledge Assistant
              </div>
              <div style={{ fontSize: 14, maxWidth: 360 }}>
                Ask me anything, or upload a document to extract and analyze its content.
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginTop: 4 }}>
                {['Summarize a document', 'Answer questions', 'Extract key info', 'Analyze data'].map((hint) => (
                  <button
                    key={hint}
                    className="btn btn-secondary btn-sm"
                    onClick={() => setInput(hint)}
                  >
                    {hint}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={msg.id || i} message={msg} isLast={i === messages.length - 1} />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{
          borderTop:  '1px solid var(--border)',
          background: 'var(--bg-card)',
          padding:    '12px 16px',
          flexShrink: 0,
        }}>
          {/* Pending file chips */}
          {pendingFiles.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 8 }}>
              {pendingFiles.map((f, i) => (
                <div key={i} style={{
                  display:    'inline-flex',
                  alignItems: 'center',
                  gap:        5,
                  background: 'var(--accent-light)',
                  border:     '1px solid #bfdbfe',
                  borderRadius: 20,
                  padding:    '3px 8px',
                  fontSize:   12,
                  color:      'var(--accent)',
                }}>
                  📎 {f.name}
                  <button
                    onClick={() => setPendingFiles((prev) => prev.filter((_, idx) => idx !== i))}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent)', fontSize: 13, lineHeight: 1, padding: 0 }}
                  >×</button>
                </div>
              ))}
            </div>
          )}

          {/* Inline upload drop zone */}
          {showUpload && (
            <div style={{ marginBottom: 10 }}>
              <FileUpload onFilesReady={handleFilesReady} disabled={loading} />
            </div>
          )}

          {/* Input row */}
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
            <button
              className="btn btn-ghost btn-icon"
              onClick={() => setShowUpload(!showUpload)}
              title="Attach file"
              style={{
                flexShrink:  0,
                background:  showUpload ? 'var(--accent-light)' : undefined,
                color:       showUpload ? 'var(--accent)'       : undefined,
              }}
            >📎</button>

            <textarea
              ref={textareaRef}
              className="input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                pendingFiles.length > 0
                  ? 'Ask something about this file, or press Enter to send…'
                  : 'Ask your AI assistant… (Enter to send, Shift+Enter for newline)'
              }
              disabled={loading}
              rows={1}
              style={{
                flex:      1,
                resize:    'none',
                maxHeight: 160,
                overflowY: 'auto',
                lineHeight: 1.5,
                padding:   '9px 12px',
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
              }}
            />

            <button
              className="btn btn-primary"
              onClick={sendMessage}
              disabled={loading || (!input.trim() && pendingFiles.length === 0)}
              style={{ flexShrink: 0, height: 38 }}
            >
              {loading
                ? <span style={{ display: 'inline-block', animation: 'spin 0.8s linear infinite' }}>⟳</span>
                : '↑ Send'}
            </button>
          </div>

          {/* Footer hint */}
          <div style={{
            display:        'flex',
            justifyContent: 'space-between',
            marginTop:      6,
            fontSize:       11.5,
            color:          'var(--text-muted)',
          }}>
            <span>Enter to send · Shift+Enter for newline · 📎 to attach files</span>
            <span style={{ color: backendStatus === 'online' ? 'var(--success)' : 'var(--danger)' }}>
              {backendStatus === 'online'
                ? '● Connected'
                : backendStatus === 'checking'
                ? '◌ Checking…'
                : '○ Offline'}
            </span>
          </div>
        </div>

      </div>
    </div>
  );
}