import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser, loginUser } from '../api/auth';
import '../styles/Auth.css';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  // Effect to handle automatic redirection after successful registration/login
  useEffect(() => {
    if (successMessage) {
      console.log('Success message set, starting timer...');
      const timer = setTimeout(() => {
        console.log('Timer completed, performing action...');
        if (isLogin) {
          console.log('Navigating to dashboard...');
          navigate('/dashboard', { replace: true });
        } else {
          setIsLogin(true);
          setSuccessMessage('');
        }
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [successMessage, isLogin, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    try {
      if (isLogin) {
        console.log('Attempting login...');
        const response = await loginUser(formData.email, formData.password);
        console.log('Login response:', response);
        
        if (response && response.data) {
          console.log('Login successful, setting success message...');
          setSuccessMessage('Login successful! Redirecting to dashboard...');
          // Store the token if it exists in the response
          if (response.data.token) {
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('name', response.data.name);
            localStorage.setItem('email', response.data.email);
          }
          // Clear form data after successful login
          setFormData({
            name: '',
            email: '',
            password: ''
          });
        }
      } else {
        console.log('Attempting registration...');
        const response = await registerUser(formData.name, formData.email, formData.password);
        console.log('Registration response:', response);
        
        if (response && response.data) {
          console.log('Registration successful, setting success message...');
          setSuccessMessage('Registration successful! Redirecting to login...');
          // Clear form data after successful registration
          setFormData({
            name: '',
            email: '',
            password: ''
          });
        }
      }
    } catch (err) {
      console.error('Error during registration/login:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'An error occurred';
      setError(errorMessage);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-sidebar">
        <div className="logo-container">
          <img src="/logo.png" alt="ScoreIt Logo" className="logo" />
        </div>
        <button 
          className="switch-auth-mode"
          onClick={() => setIsLogin(!isLogin)}
        >
          {isLogin ? 'Need an account? Register' : 'Already have an account? Login'}
        </button>
      </div>

      <div className="auth-form-container">
        <h2>{isLogin ? 'Welcome Back!' : 'Create Account'}</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Enter your name"
              />
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          {successMessage && <div className="success-message">{successMessage}</div>}

          <button type="submit" className="submit-button">
            {isLogin ? 'Login' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Auth; 