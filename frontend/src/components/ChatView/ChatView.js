import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import authService from '../../services/authService';
import { API_URL } from '../../config';
import './ChatView.css';

function ChatView() {
  const { chatId } = useParams();
  const [chat, setChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  const currentUser = authService.getUser();

  useEffect(() => {
    fetchChatAndMessages();
  }, [chatId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchChatAndMessages = async () => {
    try {
      setLoading(true);
      const token = authService.getToken();

      // Fetch chat info and messages in parallel
      const [chatRes, messagesRes] = await Promise.all([
        fetch(`${API_URL}/chats/${chatId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/chats/${chatId}/messages`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (!chatRes.ok || !messagesRes.ok) {
        throw new Error('Failed to fetch chat data');
      }

      const chatData = await chatRes.json();
      const messagesData = await messagesRes.json();

      setChat(chatData.chat);
      setMessages(messagesData.messages);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching chat:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    const content = newMessage.trim();
    if (!content || sending) return;

    try {
      setSending(true);
      const token = authService.getToken();

      const response = await fetch(`${API_URL}/chats/${chatId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      setMessages([...messages, data.message]);
      setNewMessage('');
      setError('');
    } catch (err) {
      setError(err.message);
      console.error('Error sending message:', err);
    } finally {
      setSending(false);
    }
  };

  const handleBack = () => {
    navigate('/chats');
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZone: 'America/New_York'
    });
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);

    // Get current date in EST
    const todayEST = new Date().toLocaleDateString('en-US', { timeZone: 'America/New_York' });
    const yesterdayDate = new Date();
    yesterdayDate.setDate(yesterdayDate.getDate() - 1);
    const yesterdayEST = yesterdayDate.toLocaleDateString('en-US', { timeZone: 'America/New_York' });
    const messageDateEST = date.toLocaleDateString('en-US', { timeZone: 'America/New_York' });

    if (messageDateEST === todayEST) {
      return 'Today';
    } else if (messageDateEST === yesterdayEST) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        timeZone: 'America/New_York'
      });
    }
  };

  const groupMessagesByDate = (messages) => {
    const grouped = {};
    messages.forEach(msg => {
      const dateKey = new Date(msg.created_at).toDateString();
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(msg);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div className="chat-view-container">
        <div className="loading">Loading chat...</div>
      </div>
    );
  }

  if (!chat) {
    return (
      <div className="chat-view-container">
        <div className="error-message">Chat not found</div>
      </div>
    );
  }

  const otherParticipant = chat.other_participant;
  const groupedMessages = groupMessagesByDate(messages);

  return (
    <div className="chat-view-container">
      <div className="chat-view-card">
        <div className="chat-header">
          <button onClick={handleBack} className="back-button">
            ← Back
          </button>
          <div className="chat-header-info">
            <div className="chat-avatar-small">
              {otherParticipant?.username?.charAt(0).toUpperCase() || '?'}
            </div>
            <h2>{otherParticipant?.username || 'Unknown User'}</h2>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="no-messages-state">
              <p>No messages yet. Start the conversation!</p>
            </div>
          ) : (
            Object.keys(groupedMessages).map(dateKey => (
              <div key={dateKey}>
                <div className="date-separator">
                  {formatDate(groupedMessages[dateKey][0].created_at)}
                </div>
                {groupedMessages[dateKey].map((message) => (
                  <div
                    key={message.id}
                    className={`message ${
                      message.sender_id === currentUser.id ? 'message-sent' : 'message-received'
                    }`}
                  >
                    <div className="message-content">
                      <p>{message.content}</p>
                      <span className="message-time">{formatTime(message.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="message-input-form">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="message-input"
            disabled={sending}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!newMessage.trim() || sending}
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatView;
