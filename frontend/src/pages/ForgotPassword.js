import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Auth.css';
import { sendResetEmail } from '../api/password';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSendResetLink = async (e) => {
    e.preventDefault();
    // Dummy function for now
    console.log('Reset password for:', email);
    setError('');
    try {
      const response = await sendResetEmail(email);
      if (response.status === 200) {
        setError('');
        setSuccess(response.data.message || response.message || 'Reset link sent to your email. Please check your inbox.');
        setTimeout(() => {
          navigate('/auth');
        }, 2000);
      } 
      else {
        setSuccess('');
        setError(response.data.error || response.message || 'Failed to send reset email. Please try again.');
      }
    } catch (error) {
      setError('Failed to send reset email. Please try again.');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-sidebar">
        <div className="logo-container">
          <img src="/logo.png" alt="ScoreIt Logo" className="logo" />
        </div>
      </div>

      <div className="auth-form-container">
        <h2>Reset Your Password</h2>
        <form className="auth-form" onSubmit={handleSendResetLink}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <button
            type="submit"
            className="submit-button"
            disabled={!email}
          >
            Send Reset Link
          </button>

          <button
            type="button"
            className="return-to-login"
            onClick={() => navigate('/auth')}
          >
            Return To Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword; 