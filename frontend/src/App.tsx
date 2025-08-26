import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

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
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [tenantInfo, setTenantInfo] = useState<TenantInfo | null>(null);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchTenantInfo();
    fetchChatHistory();
  }, []);

  const fetchTenantInfo = async () => {
    try {
      const response = await axios.get("/api/tenant/info/");
      setTenantInfo(response.data.tenant);
    } catch (err) {
      console.error("Error fetching tenant info:", err);
    }
  };

  const fetchChatHistory = async () => {
    try {
      const response = await axios.get("/api/chat/history/?limit=50");
      setMessages(response.data.messages.reverse());
    } catch (err) {
      console.error("Error fetching chat history:", err);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    setIsLoading(true);
    setError("");

    const userMessage = currentMessage;
    setCurrentMessage("");

    // Add user message to chat immediately
    const tempMessage: ChatMessage = {
      id: "temp-" + Date.now(),
      prompt: userMessage,
      response: "",
      created_at: new Date().toISOString(),
      model: "",
      tokens_used: 0,
      response_time_ms: 0,
    };
    setMessages((prev: any) => [...prev, tempMessage]);

    try {
      const response = await axios.post("/api/chat/call/", {
        prompt: userMessage,
        model: "openai",
      });

      if (response.data.success) {
        // Remove temp message and add real message
        setMessages((prev: any[]) =>
          prev.filter((msg: { id: string }) => msg.id !== tempMessage.id)
        );

        const newMessage: ChatMessage = {
          id: response.data.message_id,
          prompt: response.data.prompt,
          response: response.data.response,
          created_at: new Date().toISOString(),
          model: response.data.model,
          tokens_used: 1,
          response_time_ms: response.data.response_time_ms || 0,
        };

        setMessages((prev: any) => [...prev, newMessage]);

        // Update tenant info
        if (tenantInfo) {
          setTenantInfo({
            ...tenantInfo,
            tokens_used: tenantInfo.tokens_used + 1,
            tokens_remaining: tenantInfo.tokens_remaining - 1,
          });
        }
      } else {
        throw new Error("Failed to send message");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Error sending message");
      // Remove temp message on error
      setMessages((prev: any[]) =>
        prev.filter((msg: { id: string }) => msg.id !== tempMessage.id)
      );
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className='app'>
      <div className='chat-container'>
        {/* Header */}
        <div className='chat-header'>
          <h1>💬 Multi-Tenant Chat</h1>
          {tenantInfo && (
            <div className='tenant-info'>
              <span className='tenant-name'>{tenantInfo.name}</span>
              <span className='token-info'>
                Tokens: {tenantInfo.tokens_used}/{tenantInfo.tokens_limit}
              </span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className='messages-container'>
          {messages.length === 0 && !isLoading && (
            <div className='welcome-message'>
              <h3>👋 Welcome to Multi-Tenant Chat!</h3>
              <p>Start a conversation by typing a message below.</p>
            </div>
          )}

          {messages.map(
            (message: {
              id: any;
              prompt: any;
              created_at: string;
              response: any;
              response_time_ms: number;
            }) => (
              <div
                key={message.id}
                className='message-group'
              >
                <div className='message user-message'>
                  <div className='message-content'>
                    <strong>You:</strong> {message.prompt}
                  </div>
                  <div className='message-time'>
                    {formatTime(message.created_at)}
                  </div>
                </div>

                {message.response && (
                  <div className='message ai-message'>
                    <div className='message-content'>
                      <strong>AI:</strong> {message.response}
                    </div>
                    <div className='message-meta'>
                      <span className='message-time'>
                        {formatTime(message.created_at)}
                      </span>
                      {message.response_time_ms > 0 && (
                        <span className='response-time'>
                          ({message.response_time_ms}ms)
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          )}

          {isLoading && (
            <div className='message ai-message loading'>
              <div className='message-content'>
                <div className='typing-indicator'>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error */}
        {error && <div className='error-message'>⚠️ {error}</div>}

        {/* Input */}
        <form
          onSubmit={sendMessage}
          className='message-form'
        >
          <div className='input-container'>
            <input
              type='text'
              value={currentMessage}
              onChange={(e: { target: { value: any } }) =>
                setCurrentMessage(e.target.value)
              }
              placeholder='Type your message here...'
              disabled={isLoading}
              className='message-input'
            />
            <button
              type='submit'
              disabled={isLoading || !currentMessage.trim()}
              className='send-button'
            >
              {isLoading ? "⏳" : "📤"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default App;
