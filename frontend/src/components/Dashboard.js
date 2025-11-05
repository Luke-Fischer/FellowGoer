import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const currentUser = authService.getUser();
    setUser(currentUser);
  }, []);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const handleChats = () => {
    // TODO: Implement chats functionality
    console.log('Chats clicked');
  };

  const handleConnect = () => {
    // TODO: Implement connect functionality
    console.log('Connect clicked');
  };

  const handleAddRoute = () => {
    navigate('/routes');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <div className="logo-container">
          <svg className="app-logo" viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
            {/* Train */}
            <rect x="40" y="20" width="120" height="60" rx="12" fill="#00ab66" />
            <rect x="45" y="25" width="110" height="40" fill="white" />
            <circle cx="70" cy="75" r="8" fill="#333" />
            <circle cx="130" cy="75" r="8" fill="#333" />
            {/* Train windows */}
            <rect x="52" y="30" width="22" height="16" fill="#00ab66" />
            <rect x="78" y="30" width="22" height="16" fill="#00ab66" />
            <rect x="104" y="30" width="22" height="16" fill="#00ab66" />
            <rect x="130" y="30" width="22" height="16" fill="#00ab66" />
            <rect x="52" y="48" width="22" height="16" fill="#00ab66" />
            <rect x="78" y="48" width="22" height="16" fill="#00ab66" />
            <rect x="104" y="48" width="22" height="16" fill="#00ab66" />
            <rect x="130" y="48" width="22" height="16" fill="#00ab66" />
            {/* Train top */}
            <rect x="40" y="20" width="120" height="12" rx="6" fill="#008f55" />
          </svg>
          <h1>FellowGOer</h1>
        </div>

        <h2>Welcome {user?.username}!</h2>

        <div className="description">
          <p>Select the routes you take the most to connect with your fellow commuters!</p>
          <p>Find travel buddies, share experiences, and make your daily commute more enjoyable.</p>
        </div>

        <div className="action-labels">
          <div onClick={handleAddRoute} className="action-label add-route-label">
            <span className="label-icon">➕</span>
            <span className="label-text">Add Route</span>
          </div>
          <div onClick={handleChats} className="action-label chats-label">
            <span className="label-icon">💬</span>
            <span className="label-text">Chats</span>
          </div>
          <div onClick={handleConnect} className="action-label connect-label">
            <span className="label-icon">🤝</span>
            <span className="label-text">Connect</span>
          </div>
        </div>

        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
