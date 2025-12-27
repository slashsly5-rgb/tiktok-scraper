import { useState } from 'react'
import './ChatInterface.css'

const ChatInterface = () => {
  const [message, setMessage] = useState('')
  const [suggestions] = useState([
    'Why is cost of living trending up?',
    'Summarise sentiment in Miri'
  ])

  const handleSubmit = (text) => {
    if (!text || text.trim() === '') return

    console.log('User message:', text)
    // TODO: Implement actual chat functionality with API
    alert(`You asked: ${text}\n\nThis feature will connect to the AI assistant API.`)
    setMessage('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(message)
    }
  }

  return (
    <section className="chat-interface">
      <div className="chat-container">
        <div className="chat-welcome">
          <h3>Welcome, YB Dennis Ngau. How may I help you today?</h3>
        </div>

        {/* <div className="chat-input-wrapper">
          <button className="chat-add-btn" title="Add attachment">
            <i className="fas fa-plus"></i>
          </button>
          <input
            type="text"
            className="chat-input"
            placeholder="Ask BUMI"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button className="chat-voice-btn" title="Voice input">
            <i className="fas fa-microphone"></i>
          </button>
        </div> */}

        <div className="chat-suggestions">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-chip"
              onClick={() => handleSubmit(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}

export default ChatInterface
