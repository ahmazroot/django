
import React, { useState, useEffect } from 'react';
import './App.css';

interface ChatMessage {
  id: string;
  prompt: string;
  response: string;
  created_at: string;
  model: string;
  tokens_used: number;
  response_time_ms: number;
}

interface TenantInfo {
  id: string;
  name: string;
  domain: string;
  tokens_used: number;
  tokens_limit: number;
  tokens_remaining: number;
  system_parameter: string;
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [tenantInfo, setTenantInfo] = useState<TenantInfo | null>(null);
  const [model, setModel] = useState('gpt-3.5-turbo');
  const [seed, setSeed] = useState('');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3000';

  useEffect(() => {
    loadTenantInfo();
    loadChatHistory();
  }, []);

  const loadTenantInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tenant/info/`);
      if (response.ok) {
        const data = await response.json();
        setTenantInfo(data.tenant);
      }
    } catch (error) {
      console.error('Error loading tenant info:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/chat/history/?limit=20`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/chat/call/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          model,
          seed: seed || undefined
        })
      });

      if (response.ok) {
        const data = await response.json();
        const newMessage: ChatMessage = {
          id: data.message_id,
          prompt: data.prompt,
          response: data.response,
          created_at: new Date().toISOString(),
          model: data.model,
          tokens_used: 1,
          response_time_ms: data.response_time_ms
        };
        
        setMessages(prev => [newMessage, ...prev]);
        setPrompt('');
        
        // Update tenant info with new token count
        if (tenantInfo) {
          setTenantInfo({
            ...tenantInfo,
            tokens_remaining: data.tokens_remaining,
            tokens_used: tenantInfo.tokens_used + 1
          });
        }
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.error} - ${errorData.message}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="App">
      <header className="chat-header">
        <h1>Multi-Tenant Chat Interface</h1>
        {tenantInfo && (
          <div className="tenant-info">
            <div className="tenant-name">{tenantInfo.name}</div>
            <div className="token-usage">
              Tokens: {tenantInfo.tokens_used}/{tenantInfo.tokens_limit} 
              ({tenantInfo.tokens_remaining} remaining)
            </div>
          </div>
        )}
      </header>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="no-messages">No messages yet. Start a conversation!</div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="message-pair">
                <div className="message user-message">
                  <div className="message-content">{message.prompt}</div>
                  <div className="message-meta">You</div>
                </div>
                <div className="message ai-message">
                  <div className="message-content">{message.response}</div>
                  <div className="message-meta">
                    AI ({message.model}) • {message.response_time_ms}ms
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="chat-input-section">
          <div className="model-settings">
            <select 
              value={model} 
              onChange={(e) => setModel(e.target.value)}
              className="model-select"
            >
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
              <option value="claude-3">Claude-3</option>
            </select>
            <input
              type="text"
              placeholder="Seed (optional)"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              className="seed-input"
            />
          </div>
          
          <div className="chat-input">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              rows={3}
              disabled={loading}
              className="message-input"
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !prompt.trim()}
              className="send-button"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
