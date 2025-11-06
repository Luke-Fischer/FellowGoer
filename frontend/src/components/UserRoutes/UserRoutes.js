import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import './UserRoutes.css';

function UserRoutes() {
  const [userRoutes, setUserRoutes] = useState([]);
  const [allRoutes, setAllRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = authService.getToken();

      // Fetch all routes and user's routes in parallel
      const [allRoutesRes, userRoutesRes] = await Promise.all([
        fetch('http://localhost:5000/api/routes', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:5000/api/user/routes', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (!allRoutesRes.ok || !userRoutesRes.ok) {
        throw new Error('Failed to fetch routes');
      }

      const allRoutesData = await allRoutesRes.json();
      const userRoutesData = await userRoutesRes.json();

      setAllRoutes(allRoutesData.routes);
      setUserRoutes(userRoutesData.routes);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching routes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRoute = async () => {
    if (!selectedRoute) {
      setError('Please select a route');
      return;
    }

    try {
      const token = authService.getToken();
      const response = await fetch('http://localhost:5000/api/user/routes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ route_id: selectedRoute })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to add route');
      }

      // Refresh user routes
      await fetchData();
      setSelectedRoute('');
      setError('');
    } catch (err) {
      setError(err.message);
      console.error('Error adding route:', err);
    }
  };

  const handleRemoveRoute = async (userRouteId) => {
    try {
      const token = authService.getToken();
      const response = await fetch(`http://localhost:5000/api/user/routes/${userRouteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove route');
      }

      // Refresh user routes
      await fetchData();
      setError('');
    } catch (err) {
      setError(err.message);
      console.error('Error removing route:', err);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  // Filter out routes that user already has
  const availableRoutes = allRoutes.filter(route =>
    !userRoutes.some(ur => ur.route_id === route.route_id)
  );

  if (loading) {
    return (
      <div className="user-routes-container">
        <div className="loading">Loading routes...</div>
      </div>
    );
  }

  return (
    <div className="user-routes-container">
      <div className="user-routes-card">
        <div className="header">
          <button onClick={handleBack} className="back-button">
            ← Back
          </button>
          <h1>My Routes</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="add-route-section">
          <h2>Add a Route</h2>
          <div className="add-route-form">
            <select
              value={selectedRoute}
              onChange={(e) => setSelectedRoute(e.target.value)}
              className="route-dropdown"
            >
              <option value="">Select a route...</option>
              {availableRoutes.map(route => (
                <option key={route.route_id} value={route.route_id}>
                  {route.route_short_name} - {route.route_long_name}
                </option>
              ))}
            </select>
            <button
              onClick={handleAddRoute}
              className="add-button"
              disabled={!selectedRoute}
            >
              Add Route
            </button>
          </div>
        </div>

        <div className="routes-list-section">
          <h2>Your Routes ({userRoutes.length})</h2>
          {userRoutes.length === 0 ? (
            <p className="empty-message">
              You haven't added any routes yet. Select a route above to get started!
            </p>
          ) : (
            <div className="routes-list">
              {userRoutes.map(userRoute => (
                <div key={userRoute.id} className="route-item">
                  <div className="route-info">
                    <div
                      className="route-color-indicator"
                      style={{
                        backgroundColor: userRoute.route?.route_color
                          ? `#${userRoute.route.route_color}`
                          : '#00ab66'
                      }}
                    ></div>
                    <div className="route-details">
                      <span className="route-short-name">
                        {userRoute.route?.route_short_name}
                      </span>
                      <span className="route-long-name">
                        {userRoute.route?.route_long_name}
                      </span>
                      <span className="route-type">
                        {userRoute.route?.route_type === 'train' ? '🚆 Train' : '🚌 Bus'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemoveRoute(userRoute.id)}
                    className="remove-button"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserRoutes;
