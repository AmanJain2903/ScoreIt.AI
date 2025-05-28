import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { checkSession } from './api/session';

const ProtectedRoute = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const verify = async () => {
      const token = localStorage.getItem('token');

      if (token) {
        try {
          const response = await checkSession(token);
          setIsAuthenticated(response.data.active);
        } catch (error) {
          setIsAuthenticated(false);
        }
      } else if (sessionStorage.getItem('token')) {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
      setIsLoading(false);
    };

    verify();
  }, []);

  if (isLoading) return <div>Loading...</div>; // or a spinner

  return isAuthenticated ? children : <Navigate to="/auth" />;
};

export default ProtectedRoute;