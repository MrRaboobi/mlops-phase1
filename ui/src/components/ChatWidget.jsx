import { useState } from 'react'
import axios from 'axios'
import './ChatWidget.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ChatWidget({ initialDiagnosis, patientAge, patientSex }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `I've analyzed your ECG results showing ${initialDiagnosis}. How can I help you understand this better? You can ask me questions like:

• "What lifestyle changes should I make?"
• "What does this condition mean?"
• "What should I do next?"`
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: input,
        diagnosis: initialDiagnosis,
        age: patientAge,
        sex: patientSex,
        conversation_history: messages.slice(-4) // Last 4 messages for context
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}. Please try again.`
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-widget">
      <h2>💬 Ask Questions About Your Results</h2>
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className="message-content">
              {msg.content.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about your ECG results..."
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="chat-send-button"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatWidget
