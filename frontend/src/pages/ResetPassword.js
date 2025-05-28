import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/ResetPassword.css';
import { jwtDecode } from 'jwt-decode';
import { resetPassword } from '../api/password';
import { deleteAllSessions } from '../api/session';


const ResetPassword = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [logoutAll, setLogoutAll] = useState(false);
  const [error, setError] = useState('Error Message');
  const [success, setSuccess] = useState('Success Message');
  const [token, setToken] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    try{
        const searchParams = new URLSearchParams(location.search);
        const resetToken = searchParams.get('token');
        if (!resetToken) {
            setError('Invalid reset token.');
        }
        else {
          setError('');
          setSuccess('');
          setToken(resetToken);
          const decoded = jwtDecode(resetToken);
          setEmail(decoded.email);
    }
    }
    catch (error) {
      setSuccess('');
      setError('Invalid reset token. Try generating a new one.');
    }
  }, [location]);


  const handleLogoutAllDevices = async() => {
    try{
      await deleteAllSessions(token);
    }
    catch(err){
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!newPassword || !confirmPassword) {
      setSuccess('');
      setError('Please fill in all fields.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setSuccess('');
      setError('Passwords do not match.');
      return;
    }
    try{
      const response = await resetPassword(token, newPassword);
      if (response.status === 200) {
        setError('');
        setSuccess(response.data.message || response.message || 'Password reset successfully!');
        if (logoutAll) {
          await handleLogoutAllDevices();
        }
        setTimeout(() => {
          navigate('/auth');
        }, 2000);
      }
      else {
        setSuccess('');
        setError(response.data.error || response.message || 'Failed to reset password.');
      }
    }
    catch (error) {
      setSuccess('');
      setError('Failed to reset password.');
    }
  };

  return (
    <div className="reset-container">
      <div className="reset-sidebar">
        <div className="logo-container">
          <img src="/logo.png" alt="ScoreIt Logo" className="logo" />
        </div>
      </div>
      <div className="reset-form-container">
        <h2>Reset Your Password</h2>
        <form className="reset-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder={email}
              disabled
            />
          </div>
          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              placeholder="Enter new password"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
              required
            />
          </div>
          <div className="reset-logout-group">
            <input
              type="checkbox"
              id="logoutAll"
              checked={logoutAll}
              onChange={e => setLogoutAll(e.target.checked)}
              className="reset-logout-checkbox"
            />
            <label htmlFor="logoutAll" className="reset-logout-label">
              Logout from all devices?
            </label>
          </div>
          {error && <div className="reset-error-message">{error}</div>}
          {success && <div className="reset-success-message">{success}</div>}
          <button
            type="submit"
            className="reset-submit-button"
            disabled={!newPassword || !confirmPassword}
          >
            Reset Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword; 