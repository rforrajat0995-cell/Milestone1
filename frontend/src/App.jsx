import React, { useState, useRef, useEffect } from 'react'
import './App.css'

// Use relative path for Vercel deployment, or localhost for local development
// Always use /api in production (Vercel), localhost in development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.MODE === 'production' ? '/api' : 'http://localhost:5000')
const isProduction = import.meta.env.MODE === 'production'

function App() {
  // Store messages per chat
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [backendConnected, setBackendConnected] = useState(false)
  const messagesEndRef = useRef(null)

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection()
  }, [])

  // Load messages when active chat changes
  useEffect(() => {
    if (activeChatId) {
      const chat = chats.find(c => c.id === activeChatId)
      if (chat && chat.messages) {
        setMessages(chat.messages)
      } else {
        setMessages([])
      }
    } else {
      setMessages([])
    }
  }, [activeChatId, chats])

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      const data = await response.json()
      setBackendConnected(data.status === 'healthy')
    } catch (error) {
      console.error('Backend connection check failed:', error)
      setBackendConnected(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    const queryText = inputValue
    setInputValue('')
    setIsLoading(true)

    // Add user message immediately
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: queryText }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.error || 'Query failed')
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.answer || 'Sorry, I could not process your query.',
        sourceUrls: data.source_urls || [],
        timestamp: new Date()
      }

      const updatedMessages = [...newMessages, assistantMessage]
      setMessages(updatedMessages)

      // Update or create chat
      if (activeChatId) {
        // Update existing chat
        setChats(prev => prev.map(chat => 
          chat.id === activeChatId 
            ? { ...chat, messages: updatedMessages, preview: queryText }
            : chat
        ))
      } else {
        // Create new chat
        const newChat = {
          id: Date.now(),
          title: queryText.substring(0, 30) + (queryText.length > 30 ? '...' : ''),
          preview: queryText,
          messages: updatedMessages,
          timestamp: new Date()
        }
        setChats(prev => [newChat, ...prev])
        setActiveChatId(newChat.id)
      }
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Error: ${error.message}. ${isProduction ? 'Please check if the API is available.' : 'Please make sure the backend is running on http://localhost:5000 and try again.'}`,
        timestamp: new Date()
      }
      const updatedMessages = [...newMessages, errorMessage]
      setMessages(updatedMessages)
      
      if (activeChatId) {
        setChats(prev => prev.map(chat => 
          chat.id === activeChatId 
            ? { ...chat, messages: updatedMessages }
            : chat
        ))
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const startNewChat = () => {
    setActiveChatId(null)
    setMessages([])
    setInputValue('')
  }

  const handleChatClick = (chatId) => {
    setActiveChatId(chatId)
    setInputValue('')
  }

  return (
    <div className="app">
      {/* Left Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo">MF</div>
          <h2>My Chats</h2>
        </div>

        {/* Backend Connection Status */}
        <div className={`connection-status ${backendConnected ? 'connected' : 'disconnected'}`}>
          <div className="status-dot"></div>
          <span>{backendConnected ? 'Backend Connected' : 'Backend Disconnected'}</span>
        </div>

        {/* Chats Section */}
        <div className="chats-section">
          <div className="section-header">
            <h3>Chats</h3>
          </div>
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${activeChatId === chat.id ? 'active' : ''}`}
              onClick={() => handleChatClick(chat.id)}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="2" width="12" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                <path d="M5 6h6M5 9h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              <div className="chat-item-content">
                <div className="chat-title">{chat.title}</div>
                <div className="chat-preview">{chat.preview}</div>
              </div>
            </div>
          ))}
        </div>

        <button className="new-chat-button" onClick={startNewChat}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 3v14M3 10h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          New chat
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="main-content">
        <div className="chat-header">
          <div className="model-tag">RAG Assistant</div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <h1>How can I help you today?</h1>
              <p>Ask me anything about Parag Parikh mutual funds. I can help you find information about expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometers, and benchmarks.</p>
              
              {!backendConnected && (
                <div className="warning-box">
                  ⚠️ Backend not connected. {isProduction ? 'The API endpoint may not be available. Please check the deployment.' : 'Please make sure the backend server is running on http://localhost:5000'}
                </div>
              )}
              
              <div className="feature-cards">
                <div className="feature-card">
                  <div className="feature-icon">📊</div>
                  <h3>Fund Information</h3>
                  <p>Get detailed information about any Parag Parikh mutual fund scheme.</p>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">🔍</div>
                  <h3>Quick Queries</h3>
                  <p>Ask questions in natural language and get instant factual answers.</p>
                </div>
                <div className="feature-card">
                  <div className="feature-icon">🔗</div>
                  <h3>Source Links</h3>
                  <p>Every answer includes source URLs from official Groww pages.</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map(message => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-content">
                    {message.content}
                    {message.sourceUrls && message.sourceUrls.length > 0 && (
                      <div className="source-links">
                        <strong>Source:</strong>{' '}
                        <a href={message.sourceUrls[0]} target="_blank" rel="noopener noreferrer">
                          {message.sourceUrls[0]}
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <div className="logo-small">MF</div>
            <input
              type="text"
              className="chat-input"
              placeholder="Type your prompt here..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              className="send-button"
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M18 2L9 11M18 2l-7 9M18 2H2l6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <div className="footer-disclaimer">
          This assistant provides factual information only. It does not provide investment advice.
        </div>
      </div>
    </div>
  )
}

export default App
