import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { 
      sender: 'bot', 
      text: 'Hello! I\'m Brew Master AI. Ask me anything about beer brewing, and I\'ll help you with expert knowledge from our brewing database.',
      timestamp: new Date(),
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewConversation = () => {
    setMessages([
      { 
        sender: 'bot', 
        text: 'Hello! I\'m Brew Master AI. Ask me anything about beer brewing, and I\'ll help you with expert knowledge from our brewing database.',
        timestamp: new Date(),
        sources: []
      }
    ]);
    setError(null);
    setShowExportMenu(false);
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
      console.log('Copied to clipboard');
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const copyResponse = (message) => {
    const textToCopy = `${message.text}\n\nSources: ${message.sources?.map(s => `${s.source_file} (${(s.score * 100).toFixed(1)}% match)`).join(', ') || 'None'}`;
    copyToClipboard(textToCopy);
  };

  const exportConversation = () => {
    const conversationText = messages.map(msg => {
      const timestamp = new Date(msg.timestamp).toLocaleString();
      const sources = msg.sources?.map(s => `${s.source_file} (${(s.score * 100).toFixed(1)}% match)`).join(', ') || 'None';
      
      return `${msg.sender === 'user' ? 'You' : 'Brew Master AI'} (${timestamp}):\n${msg.text}${msg.sources?.length ? `\nSources: ${sources}` : ''}\n`;
    }).join('\n---\n\n');

    const blob = new Blob([conversationText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `brew-master-ai-conversation-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const shareConversation = async () => {
    const conversationText = messages.map(msg => {
      const sources = msg.sources?.map(s => `${s.source_file} (${(s.score * 100).toFixed(1)}% match)`).join(', ') || 'None';
      return `${msg.sender === 'user' ? 'You' : 'Brew Master AI'}: ${msg.text}${msg.sources?.length ? `\nSources: ${sources}` : ''}`;
    }).join('\n\n');

    const shareText = `🍺 Brew Master AI Conversation\n\n${conversationText}\n\n---\nShared from Brew Master AI`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Brew Master AI Conversation',
          text: shareText,
          url: window.location.href
        });
      } catch (err) {
        console.log('Share cancelled or failed');
      }
    } else {
      // Fallback to copying to clipboard
      copyToClipboard(shareText);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const updatedMessages = [...messages, { 
      sender: 'user', 
      text: userMessage, 
      timestamp: new Date() 
    }];
    setMessages(updatedMessages);

    try {
      // Prepare conversation context for RAG
      const conversationContext = updatedMessages
        .filter(msg => msg.sender === 'user')
        .map(msg => msg.text)
        .join('\n');

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          conversation_context: conversationContext,
          top_k: 3
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Add bot response
      const finalMessages = [...updatedMessages, { 
        sender: 'bot', 
        text: data.answer, 
        timestamp: new Date(),
        sources: data.sources || [],
        confidence_score: data.confidence_score || 0,
        response_quality: data.response_quality || 'Unknown'
      }];
      
      setMessages(finalMessages);

    } catch (err) {
      console.error('Error:', err);
      setError('Sorry, I encountered an error. Please try again.');
      const errorMessages = [...updatedMessages, { 
        sender: 'bot', 
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      }];
      setMessages(errorMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <div className="header-content">
            <h1>🍺 Brew Master AI</h1>
            <p>Your expert beer brewing assistant</p>
          </div>
          <div className="header-actions">
            <div className="export-menu-container">
              <button 
                className="export-btn"
                onClick={() => setShowExportMenu(!showExportMenu)}
                title="Export & Share"
              >
                📤
              </button>
              {showExportMenu && (
                <div className="export-menu">
                  <button onClick={exportConversation} className="export-option">
                    📄 Export as Text
                  </button>
                  <button onClick={shareConversation} className="export-option">
                    🔗 Share Conversation
                  </button>
                </div>
              )}
            </div>
            <button 
              className="new-chat-btn"
              onClick={startNewConversation}
              title="Start new conversation"
            >
              ➕ New Chat
            </button>
          </div>
        </header>

        <div className="messages-container">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender}`}>
              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                {msg.sender === 'bot' && msg.confidence_score !== undefined && (
                  <div className="confidence-indicator">
                    <span className={`confidence-badge ${msg.response_quality?.toLowerCase()}`}>
                      {msg.response_quality} ({(msg.confidence_score * 100).toFixed(0)}%)
                    </span>
                  </div>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <div className="sources-title">Sources:</div>
                    {msg.sources.map((source, idx) => (
                      <div key={idx} className="source-item">
                        <span className="source-file">{source.source_file}</span>
                        <span className="source-score">({(source.score * 100).toFixed(1)}% match)</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="message-actions">
                  <div className="message-time">{formatTime(msg.timestamp)}</div>
                  {msg.sender === 'bot' && !msg.isError && (
                    <button 
                      className="copy-btn"
                      onClick={() => copyResponse(msg)}
                      title="Copy response"
                    >
                      📋
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot">
              <div className="message-content">
                <div className="loading-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              className="message-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about beer brewing techniques, ingredients, recipes..."
              disabled={isLoading}
              rows={1}
            />
            <button 
              className="send-button"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          <div className="input-hint">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
