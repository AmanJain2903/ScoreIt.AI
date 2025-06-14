import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser, loginUser, googleLogin, sendEmail } from '../api/auth';
import { createSession } from '../api/session';
import '../styles/Auth.css';
import { useGoogleLogin } from '@react-oauth/google';
import { createProfile, readProfile } from '../api/profile';
import { Eye, EyeOff } from 'lucide-react';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const Googlelogin = useGoogleLogin({
    onSuccess: async (credentialResponse) => {
      try {
        setError('');
        setSuccessMessage('');
        localStorage.clear();
        sessionStorage.clear();
        
        if (!credentialResponse.access_token) {
          throw new Error('No access token received from Google');
        }

        const res = await googleLogin(credentialResponse.access_token);
  
        const data = res.data;
        if (!data || !data.token) {
          throw new Error('No token received from backend');
        }

        setSuccessMessage('Login successful! Redirecting to dashboard...');
        let fetchedProfile;
        try{
          fetchedProfile = await readProfile(data.token);
        }
        catch(err){
          await createProfile(data.email);
          fetchedProfile = await readProfile(data.token);
        }
  
        if (rememberMe) {
          localStorage.setItem('token', data.token);
          localStorage.setItem('name', data.name);
          localStorage.setItem('isGoogleUser', data.is_google_user);
          localStorage.setItem('profileData', JSON.stringify(fetchedProfile.data));
          localStorage.setItem('darkMode', fetchedProfile.data.dark_mode);
          localStorage.setItem('modelPreference', fetchedProfile.data.model_preference);
          await createSession(data.token);
        }
        else {
          sessionStorage.setItem('token', data.token);
          sessionStorage.setItem('name', data.name);
          sessionStorage.setItem('isGoogleUser', data.is_google_user);
          sessionStorage.setItem('profileData', JSON.stringify(fetchedProfile.data));
          sessionStorage.setItem('darkMode', fetchedProfile.data.dark_mode);
          sessionStorage.setItem('modelPreference', fetchedProfile.data.model_preference);
        }
      } catch (err) {
        setError(err.response?.data?.error || err.message || "Google login failed");
      }
    },
    onError: (error) => {
      setError("Google login failed. Please try again.");
    },
    flow: 'implicit',
    scope: 'email profile',
  });

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

  const handleResendVerification = async () => {
    await sendEmail(formData.email);
    setError('');
    setSuccessMessage('Verification link sent to your email. Please check your inbox.');
  };

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
        localStorage.clear();
        sessionStorage.clear();
        console.log('Attempting login...');
        const response = await loginUser(formData.email, formData.password);
        console.log('Login response:', response);
        let fetchedProfile;
        if (response && response.data) {
          fetchedProfile = await readProfile(response.data.token);
          console.log('Login successful! Redirecting to dashboard...');
          setSuccessMessage('Login successful! Redirecting to dashboard...');
          // Store the token if it exists in the response
          if (response.data.token) {
            if (rememberMe) {
              localStorage.setItem('token', response.data.token);
              localStorage.setItem('name', response.data.name);
              localStorage.setItem('isGoogleUser', response.data.is_google_user);
              localStorage.setItem('profileData', JSON.stringify(fetchedProfile.data));
              localStorage.setItem('darkMode', fetchedProfile.data.dark_mode);
              localStorage.setItem('modelPreference', fetchedProfile.data.model_preference);
              await createSession(response.data.token);
            }
            else {
              sessionStorage.setItem('token', response.data.token);
              sessionStorage.setItem('name', response.data.name);
              sessionStorage.setItem('isGoogleUser', response.data.is_google_user);
              sessionStorage.setItem('profileData', JSON.stringify(fetchedProfile.data));
              sessionStorage.setItem('darkMode', fetchedProfile.data.dark_mode);
              sessionStorage.setItem('modelPreference', fetchedProfile.data.model_preference)
            }
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
          await createProfile(formData.email);
          await sendEmail(formData.email);
          console.log('Registration successful, setting success message...');
          setSuccessMessage('Registration successful! Verify your email to login...');
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
            <label htmlFor="password" style={{ display: 'flex', alignItems: 'center', gap: '0.5em' }}>
              Password
              <span
                className="toggle-password-label-icon"
                onClick={() => setShowPassword((prev) => !prev)}
                tabIndex={0}
                role="button"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center' }}
              >
                {showPassword ? <Eye size={18} color="#000000" /> : <EyeOff size={18} color="#A9A9A9" />}
              </span>
            </label>
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {isLogin && (
            <div className="remember-me-group">
              <div className="remember-me-left">
                <input
                  type="checkbox"
                  id="remember-me"
                  className="remember-me-checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label htmlFor="remember-me" className="remember-me-label">
                  Remember Me
                </label>
              </div>
              <div className="forgot-password-link">
                <Link to="/forgot-password">Forgot Password?</Link>
              </div>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}
          {successMessage && <div className="success-message">{successMessage}</div>}

          {error === 'Please verify your email to login' && isLogin && (
            <button
              type="button"
              className="resend-verification-btn"
              onClick={() => { handleResendVerification() }}
            >
              Resend Verification Link
            </button>
          )}

          <button type="submit" className="submit-button" disabled={
                isLogin
                  ? !formData.email || !formData.password
                  : !formData.name || !formData.email || !formData.password
              }>
            {isLogin ? 'Login' : 'Register'}
          </button>
          <button onClick={() => Googlelogin()} type="button" className="google-signin-button">
            <img src="/google.png" alt="Google Logo" className="google-icon" />
            Sign in with Google
          </button>
        </form>
      </div>
    </div>
  );
};

export default Auth; 