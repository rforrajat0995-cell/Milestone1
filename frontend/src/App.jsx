import React, { useState, useRef, useEffect } from 'react'
import './App.css'

// Use relative path for Vercel deployment, or localhost for local development
// Always use /api prefix - Vercel routes /api/* to api/ functions
// In development, use localhost
const getApiBaseUrl = () => {
  // Check environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // Check if we're in browser and on Vercel
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    if (hostname.includes('vercel.app') || hostname.includes('vercel.com')) {
      return '/api'
    }
  }
  
  // Default: localhost for development (port 5001 to avoid AirPlay conflict)
  return 'http://localhost:5001'
}

const API_BASE_URL = getApiBaseUrl()
const isProduction = typeof window !== 'undefined' && 
  (window.location.hostname.includes('vercel.app') || 
   window.location.hostname.includes('vercel.com'))

function App() {
  // Store messages per chat
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [backendConnected, setBackendConnected] = useState(false)
  const [backendMode, setBackendMode] = useState(null)  // Track backend mode (gemini vs fallback)
  const messagesEndRef = useRef(null)
  const requestInProgressRef = useRef(false)  // Prevent duplicate requests
  const healthCheckDoneRef = useRef(false)  // Prevent duplicate health checks

  // Check backend connection on mount (only once, even with StrictMode)
  useEffect(() => {
    if (!healthCheckDoneRef.current) {
      healthCheckDoneRef.current = true
      checkBackendConnection()
    }
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
      const healthUrl = `${API_BASE_URL}/health`
      console.log('Checking backend at:', healthUrl)
      console.log('API_BASE_URL:', API_BASE_URL)
      console.log('Hostname:', typeof window !== 'undefined' ? window.location.hostname : 'N/A')
      
      const response = await fetch(healthUrl)
      console.log('Health check response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('Health check data:', data)
      setBackendConnected(data.status === 'healthy')
      
      // Store mode information
      if (data.mode) {
        setBackendMode(data.mode)
        console.log('Backend mode:', data.mode)
      }
    } catch (error) {
      console.error('Backend connection check failed:', error)
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        API_BASE_URL: API_BASE_URL
      })
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
    // Prevent duplicate requests
    if (!inputValue.trim() || isLoading || requestInProgressRef.current) {
      console.log('Request blocked - already in progress or invalid input')
      return
    }

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    const queryText = inputValue
    setInputValue('')
    setIsLoading(true)
    requestInProgressRef.current = true  // Mark request as in progress

    // Add user message immediately
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)

    try {
      console.log('Sending query to:', `${API_BASE_URL}/query`)
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: queryText }),
      })

      console.log('Response status:', response.status, response.statusText)

      if (!response.ok) {
        let errorData
        try {
          errorData = await response.json()
        } catch (e) {
          errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
        }
        console.error('HTTP error:', errorData)
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Response data:', data)

      if (!data.success) {
        // Show the actual answer even if success is false (might contain useful error info)
        if (data.answer && data.answer.includes('Error generating answer')) {
          throw new Error(data.answer)
        }
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
      console.error('Error details:', {
        message: error.message,
        name: error.name,
        stack: error.stack,
        API_BASE_URL: API_BASE_URL
      })
      
      // Check if it's a network error
      const isNetworkError = error.message.includes('Failed to fetch') || 
                            error.message.includes('NetworkError') ||
                            error.message.includes('Network request failed') ||
                            error.name === 'TypeError'
      
      let errorContent
      if (isNetworkError) {
        errorContent = `Network Error: Cannot connect to backend at ${API_BASE_URL}. Please make sure the backend is running on http://localhost:5001 and try again.`
      } else {
        errorContent = `Error: ${error.message}`
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: errorContent,
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
      requestInProgressRef.current = false  // Reset request flag
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
        
        {/* Backend Mode Indicator */}
        {backendConnected && backendMode && (
          <div className="mode-status">
            <div className="mode-label">Mode:</div>
            <div className={`mode-badge ${backendMode.fallback_active ? 'fallback' : 'gemini'}`}>
              {backendMode.fallback_active ? '🔄 Fallback (Local)' : '✨ Gemini API'}
            </div>
            <div className="mode-details">
              Embeddings: {backendMode.embeddings === 'local (sentence-transformers)' ? 'Local' : 'Gemini'} | 
              LLM: {backendMode.llm === 'gemini-api' ? 'Gemini' : 'Fallback'}
            </div>
          </div>
        )}

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
              
              {/* Important Notice */}
              <div className="info-box">
                <strong>📌 Important:</strong> This assistant is specifically designed for <strong>Parag Parikh Mutual Funds only</strong>. 
                It does not support queries about funds from other Asset Management Companies (AMCs).
              </div>
              
              <p>Ask me anything about Parag Parikh mutual funds. I can help you find information about expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometers, and benchmarks.</p>
              
              {!backendConnected && (
                <div className="warning-box">
                  ⚠️ Backend not connected. {isProduction ? 'The API endpoint may not be available. Please check the deployment.' : 'Please make sure the backend server is running on http://localhost:5001'}
                </div>
              )}
              
              <div className="feature-cards">
                <div className="feature-card">
                  <div className="feature-icon">📊</div>
                  <h3>Fund Information</h3>
                  <p>Get detailed information about Parag Parikh mutual fund schemes only.</p>
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
                          {message.sourceUrls[0].includes('?q=') ? 'Search on Groww' : message.sourceUrls[0]}
                        </a>
                        {message.sourceUrls[0].includes('?q=') ? (
                          <div className="source-note">
                            <small>Note: Direct fund URL not available. Click to search for this fund on Groww.</small>
                          </div>
                        ) : (
                          <div className="source-note">
                            <small>Note: Source URLs are from when data was scraped. If this link doesn't work, please search for the fund on <a href="https://groww.in/mutual-funds" target="_blank" rel="noopener noreferrer">Groww</a>.</small>
                          </div>
                        )}
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
          This assistant provides factual information only for Parag Parikh Mutual Funds. 
          It does not support other AMCs and does not provide investment advice.
        </div>
      </div>
    </div>
  )
}

export default App
