import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Send,
  Sparkles,
  Trash2,
  ExternalLink,
  FileText,
  Globe,
  AlertCircle,
  ArrowUp
} from 'lucide-react';
import './App.css';
import { ChatIcon } from './components/ChatIcon';

function App() {
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('ar_advisor_chats');
    return saved ? JSON.parse(saved) : [];
  });
  const [currentChatId, setCurrentChatId] = useState(() => {
    const saved = localStorage.getItem('ar_advisor_current_chat_id');
    return saved || Date.now().toString();
  });
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const starterPrompts = [
    "How can I balance family and work?",
    "Build me a morning habit routine",
    "Tips to improve my financial health",
    "Micro-habits to boost energy levels"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Find active chat or construct an empty messages list
  const activeChat = chats.find(c => c.id === currentChatId);
  const messages = activeChat ? activeChat.messages : [];

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [currentChatId]);

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem('ar_advisor_chats', JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    localStorage.setItem('ar_advisor_current_chat_id', currentChatId);
  }, [currentChatId]);

  const getSourceLabel = (src) => {
    if (!src) return 'Source';
    if (src.startsWith('http://') || src.startsWith('https://')) {
      try {
        return new URL(src).hostname.replace('www.', '');
      } catch {
        return 'Web Link';
      }
    }
    const parts = src.split(/[\\/]/);
    return parts[parts.length - 1] || 'Local Doc';
  };

  const handleSend = async (textToSend) => {
    const queryText = textToSend || input;
    if (!queryText.trim()) return;

    if (!textToSend) setInput('');
    setError(null);

    const userMsg = { id: Date.now() + '-user', text: queryText, sender: 'user' };

    // Optimistically update chats with user message
    setChats(prevChats => {
      const updatedChats = [...prevChats];
      const chatIndex = updatedChats.findIndex(c => c.id === currentChatId);
      if (chatIndex === -1) {
        // Create new chat session
        const newChat = {
          id: currentChatId,
          title: queryText.slice(0, 30) + (queryText.length > 30 ? '...' : ''),
          messages: [userMsg]
        };
        return [newChat, ...updatedChats];
      } else {
        // Append message to existing chat session
        const chat = updatedChats[chatIndex];
        const updatedMessages = [...chat.messages, userMsg];
        // If it was empty session and didn't have title, set it
        let title = chat.title;
        if (chat.messages.length === 0) {
          title = queryText.slice(0, 30) + (queryText.length > 30 ? '...' : '');
        }
        updatedChats[chatIndex] = {
          ...chat,
          title,
          messages: updatedMessages
        };
        return updatedChats;
      }
    });

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/life-advisor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: queryText }),
      });

      if (!response.ok) throw new Error(`Server returned status ${response.status}`);

      const data = await response.json();
      const botMsg = {
        id: Date.now() + '-bot',
        text: data.final_message || "I couldn't process that.",
        sender: 'bot',
        sources: data.sources || []
      };

      setChats(prevChats => {
        return prevChats.map(c => {
          if (c.id === currentChatId) {
            return {
              ...c,
              messages: [...c.messages, botMsg]
            };
          }
          return c;
        });
      });
    } catch (err) {
      console.error("API Fetch Error:", err);
      setError("Unable to connect. Make sure the backend is running on localhost:8000.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startNewChat = () => {
    const newId = Date.now().toString();
    setCurrentChatId(newId);
    setError(null);
  };

  const deleteChat = (chatId, e) => {
    e.stopPropagation();
    const updatedChats = chats.filter(c => c.id !== chatId);
    setChats(updatedChats);
    if (currentChatId === chatId) {
      if (updatedChats.length > 0) {
        setCurrentChatId(updatedChats[0].id);
      } else {
        startNewChat();
      }
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className={`app-container ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      {/* Sidebar */}
      <aside className="app-sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <ChatIcon size={28} />
            <span className="sidebar-title">AR Advisor</span>
          </div>
          <button className="sidebar-toggle-btn" onClick={() => setIsSidebarOpen(false)} title="Collapse sidebar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
        </div>

        <button className="sidebar-new-chat-btn" onClick={startNewChat}>
          <Sparkles size={16} />
          <span>New Chat</span>
        </button>

        <div className="sidebar-history">
          <div className="history-label">Recent Chats</div>
          {chats.length === 0 ? (
            <div className="no-history">No chat history</div>
          ) : (
            <div className="history-list">
              {chats.map(chat => (
                <div
                  key={chat.id}
                  className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
                  onClick={() => setCurrentChatId(chat.id)}
                >
                  <span className="history-item-title">{chat.title}</span>
                  <button
                    className="history-delete-btn"
                    onClick={(e) => deleteChat(chat.id, e)}
                    title="Delete Chat"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>

      {/* Main Layout Area */}
      <div className="app-layout">
        {/* Header */}
        <header className="app-header">
          <div className="header-left">
            {!isSidebarOpen && (
              <button className="sidebar-toggle-btn-open" onClick={() => setIsSidebarOpen(true)} title="Expand sidebar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="3" y1="12" x2="21" y2="12"></line>
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
              </button>
            )}
            <ChatIcon size={20} className="header-icon" />
            <span className="header-title">AR Advisor</span>
            <span className="header-badge">Life Coach</span>
          </div>

        </header>

        {/* Main content area */}
        <div className="chat-area">
          {!hasMessages ? (
            /* ---- WELCOME SCREEN ---- */
            <div className="welcome-container">
              <div className="welcome-content">
                <div className="welcome-icon">
                  <ChatIcon size={48} />
                </div>
                <h1>What can I help you with?</h1>
                <p>I'm your Life Alignment Coach — ask me about time management, habits, health, relationships, or finance.</p>
                <div className="prompt-chips">
                  {starterPrompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      className="prompt-chip"
                      onClick={() => handleSend(prompt)}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* ---- MESSAGES ---- */
            <div className="messages-scroll">
              {messages.map((msg) => (
                <div key={msg.id} className={`msg-row ${msg.sender}`}>
                  <div className="msg-avatar">
                    {msg.sender === 'user' ? 'U' : <ChatIcon size={18} />}
                  </div>
                  <div className="msg-bubble">
                    {msg.sender === 'user' ? (
                      <p>{msg.text}</p>
                    ) : (
                      <>
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="sources-section">
                            <span className="sources-label">
                              {msg.sources.some(s => s.startsWith('http')) ? <Globe size={12} /> : <FileText size={12} />}
                              Sources
                            </span>
                            <div className="sources-pills">
                              {msg.sources.map((src, i) => (
                                <a
                                  key={i}
                                  href={src.startsWith('http') ? src : '#'}
                                  target={src.startsWith('http') ? "_blank" : undefined}
                                  rel={src.startsWith('http') ? "noopener noreferrer" : undefined}
                                  className="source-pill"
                                  title={src}
                                >
                                  {getSourceLabel(src)}
                                  {src.startsWith('http') && <ExternalLink size={10} />}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="msg-row bot">
                  <div className="msg-avatar">
                    <ChatIcon size={18} />
                  </div>
                  <div className="msg-bubble">
                    <div className="typing-dots">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="error-banner">
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-box">
            <input
              ref={inputRef}
              type="text"
              placeholder="Message AR Advisor..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            <button
              className="send-btn"
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
            >
              <ArrowUp size={18} />
            </button>
          </div>
          <p className="input-hint">AR uses RAG + live web search to generate grounded responses.</p>
        </div>
      </div>
    </div>
  );
}

export default App;
