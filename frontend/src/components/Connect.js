import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Connect.css';

function Connect() {
  const [matchingUsers, setMatchingUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMatchingUsers();
  }, []);

  const fetchMatchingUsers = async () => {
    try {
      setLoading(true);
      const token = authService.getToken();

      const response = await fetch('http://localhost:5000/api/connect/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch matching users');
      }

      const data = await response.json();
      setMatchingUsers(data.users);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching matching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleSendMessage = async (userId) => {
    try {
      const token = authService.getToken();

      const response = await fetch('http://localhost:5000/api/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ other_user_id: userId })
      });

      if (!response.ok) {
        throw new Error('Failed to create chat');
      }

      const data = await response.json();
      navigate(`/chats/${data.chat.id}`);
    } catch (err) {
      setError(err.message);
      console.error('Error creating chat:', err);
    }
  };

  if (loading) {
    return (
      <div className="connect-container">
        <div className="loading">Finding your fellow commuters...</div>
      </div>
    );
  }

  return (
    <div className="connect-container">
      <div className="connect-card">
        <div className="header">
          <button onClick={handleBack} className="back-button">
            ← Back
          </button>
          <h1>Connect with Fellow Commuters</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        {matchingUsers.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🚂</div>
            <h2>No Matching Commuters Yet</h2>
            <p>
              We couldn't find any users who share your routes at the moment.
            </p>
            <p>
              Try adding more routes to increase your chances of connecting with fellow commuters!
            </p>
            <button onClick={() => navigate('/routes')} className="add-routes-button">
              Add Routes
            </button>
          </div>
        ) : (
          <div className="users-section">
            <div className="users-header">
              <h2>Found {matchingUsers.length} Fellow Commuter{matchingUsers.length !== 1 ? 's' : ''}</h2>
              <p>These users take at least one of the same routes as you</p>
            </div>

            <div className="users-list">
              {matchingUsers.map(user => (
                <div key={user.id} className="user-card">
                  <div className="user-info">
                    <div className="user-avatar">
                      {user.username.charAt(0).toUpperCase()}
                    </div>
                    <div className="user-details">
                      <h3>{user.username}</h3>
                      <p className="shared-routes-count">
                        {user.shared_routes_count} shared route{user.shared_routes_count !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>

                  <div className="shared-routes">
                    <h4>Shared Routes:</h4>
                    <div className="routes-tags">
                      {user.shared_routes.map(route => (
                        <div
                          key={route.route_id}
                          className="route-tag"
                          style={{
                            backgroundColor: route.route_color
                              ? `#${route.route_color}`
                              : '#00ab66',
                            color: route.route_text_color
                              ? `#${route.route_text_color}`
                              : '#ffffff'
                          }}
                        >
                          <span className="route-short-name">{route.route_short_name}</span>
                          <span className="route-type-icon">
                            {route.route_type === 'train' ? '🚆' : '🚌'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="user-actions">
                    <button
                      className="message-button"
                      onClick={() => handleSendMessage(user.id)}
                    >
                      Send Message
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Connect;
