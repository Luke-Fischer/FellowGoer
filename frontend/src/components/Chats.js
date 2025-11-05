import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';
import './Chats.css';

function Chats() {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchChats();
  }, [location.key]);

  const fetchChats = async () => {
    try {
      setLoading(true);
      const token = authService.getToken();

      const response = await fetch('http://localhost:5000/api/chats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch chats');
      }

      const data = await response.json();
      setChats(data.chats);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching chats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleChatClick = (chatId) => {
    navigate(`/chats/${chatId}`);
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="chats-container">
        <div className="loading">Loading chats...</div>
      </div>
    );
  }

  return (
    <div className="chats-container">
      <div className="chats-card">
        <div className="header">
          <button onClick={handleBack} className="back-button">
            ← Back
          </button>
          <h1>My Chats</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        {chats.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h2>No Chats Yet</h2>
            <p>
              Start a conversation with fellow commuters by visiting the Connect page!
            </p>
            <button onClick={() => navigate('/connect')} className="connect-button">
              Find Commuters
            </button>
          </div>
        ) : (
          <div className="chats-list">
            {chats.map(chat => (
              <div
                key={chat.id}
                className="chat-item"
                onClick={() => handleChatClick(chat.id)}
              >
                <div className="chat-avatar">
                  {chat.other_participant?.username?.charAt(0).toUpperCase() || '?'}
                </div>
                <div className="chat-info">
                  <div className="chat-header-row">
                    <h3 className="chat-username">
                      {chat.other_participant?.username || 'Unknown User'}
                    </h3>
                    {chat.last_message && (
                      <span className="chat-time">
                        {formatTime(chat.last_message.created_at)}
                      </span>
                    )}
                  </div>
                  <p className="chat-last-message">
                    {chat.last_message ? (
                      <>
                        {chat.last_message.sender_id === authService.getUser().id && (
                          <span className="you-label">You: </span>
                        )}
                        {chat.last_message.content}
                      </>
                    ) : (
                      <span className="no-messages">No messages yet</span>
                    )}
                  </p>
                </div>
                {chat.unread_count > 0 && (
                  <div className="unread-badge">{chat.unread_count}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Chats;
