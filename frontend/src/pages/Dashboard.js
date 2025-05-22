import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResume, parseJD } from '../api/parse';
import { extractResume, extractJD } from '../api/extract';
import { makeMatch } from '../api/match';
import { addHistory, deleteAll } from '../api/history';
import { deleteUser } from '../api/auth';
import ScoreReport from '../components/ScoreReport';
import PastMatches from '../components/PastMatches';
import { fetchConfig } from '../api/fetch_config';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [userName, setUserName] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jobLink, setJobLink] = useState('');
  const [resumeJSON, setResumeJSON] = useState(null);
  const [jobJSON, setJobJSON] = useState(null);
  const [matchReport, setMatchReport] = useState(null);
  const [resumeMethod, setResumeMethod] = useState('none');
  const [jobMethod, setJobMethod] = useState('none');
  const [loadingMessage, setLoadingMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showScoreReport, setShowScoreReport] = useState(false);
  const [matchTime, setMatchTime] = useState(null);
  const pastMatchesRef = useRef(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const [showProfileTooltip, setShowProfileTooltip] = useState(false);
  const [showNoMatchesPopup, setShowNoMatchesPopup] = useState(false);
  const [hasPastMatches, setHasPastMatches] = useState(null); // null = unknown, true/false = known
  const historyBtnRef = useRef(null);
  const [popupPos, setPopupPos] = useState({ top: 100, left: 100 });
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true');
  const [models, setModels] = useState({});
  const [selectedModel, setSelectedModel] = useState('1'); // Default to first model
  const [showModelDropdown, setShowModelDropdown] = useState(false);

  useEffect(() => {
    const userName = localStorage.getItem('name');
    if (userName) {
      setUserName(userName || 'User');
    }
    // Add a small delay to ensure smooth transition
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await fetchConfig();
        if (response.data) {
          setModels(response.data);
          // Set default model ID
          localStorage.setItem('modelID', '1');
        }
      } catch (error) {
        console.error('Error loading models:', error);
      }
    };
    loadModels();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('name');
    localStorage.removeItem('email');
    navigate('/auth');
  };

  const toggleProfileDropdown = () => {
    setShowProfileDropdown(!showProfileDropdown);
  };

  const handleResumeFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeMethod('file');
      setResumeFile(file);
    } else {
      alert('Please upload a PDF file');
    }
  };

  const handleResumeTextChange = (e) => {
    setResumeText(e.target.value);
    if (e.target.value.trim() !== '') {
      setResumeMethod('text');
    } else {
      setResumeMethod('none');
    }
  };

  const handleJobDescriptionChange = (e) => {
    setJobDescription(e.target.value);
    if (e.target.value.trim() !== '') {
      setJobMethod('text');
    } else {
      setJobMethod('none');
    }
  };

  const handleJobLinkChange = (e) => {
    setJobLink(e.target.value);
    if (e.target.value.trim() !== '') {
      setJobMethod('link');
    } else {
      setJobMethod('none');
    }
  };

  const handleResumeReset = () => {
    setResumeText('');
    setResumeMethod('none');
    setResumeFile(null);
    const fileInput = document.getElementById('resume-upload');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleJobReset = () => {
    setJobDescription('');
    setJobLink('');
    setJobMethod('none');
  };

  const isMatchEnabled = () => {
    return (resumeText.trim() !== '' || resumeFile) && 
           (jobDescription.trim() !== '' || jobLink.trim() !== '');
  };

  const handleMatch = async () => {
    try {
      setIsProcessing(true);
      const startTime = Date.now();
      let finalResumeText = resumeText;
      let finalJobDescription = jobDescription;
      let finalResumeJSON = null;
      let finalJobJSON = null;

      // If resume file is provided, parse it first
      if (resumeMethod === 'file' && resumeFile) {
        setLoadingMessage('Parsing Resume from PDF...');
        const formData = new FormData();
        formData.append('resume_file', resumeFile);
        
        const response = await parseResume(formData);
        if (response.data && response.data.resume_text) {
          finalResumeText = response.data.resume_text;
          setResumeText(response.data.resume_text);
        } else {
          alert('Failed to parse resume: ' + (response.data?.error || 'Unknown error'));
          setIsProcessing(false);
          setLoadingMessage('');
          return;
        }
      }

      // If job link is provided, parse it first
      if (jobMethod === 'link' && jobLink.trim() !== '') {
        setLoadingMessage('Parsing Job Description from Link...');
        const formData = new FormData();
        formData.append('jd_link', jobLink);
        
        const response = await parseJD(formData);
        if (response.data && response.data.jd_text) {
          finalJobDescription = response.data.jd_text;
          setJobDescription(finalJobDescription);
        } else {
          alert('Failed to parse job description: ' + (response.data?.error || 'Unknown error'));
          setIsProcessing(false);
          setLoadingMessage('');
          return;
        }
      }

      // Now both resume and job description should be in text format
      if (finalResumeText.trim() === '' || finalJobDescription.trim() === '') {
        alert('Please provide both resume and job description');
        setIsProcessing(false);
        setLoadingMessage('');
        return;
      }

      // Extract JSON from resume text
      setLoadingMessage('Extracting Resume Entities...');
      const resumeFormData = new FormData();
      resumeFormData.append('resume_text', finalResumeText);
      resumeFormData.append('model_id', selectedModel);
      let resumeExtractResponse;
      try {
        resumeExtractResponse = await extractResume(resumeFormData);
        if (!resumeExtractResponse.data || !resumeExtractResponse.data.resume_entites) {
          // First attempt failed, try once more
          resumeExtractResponse = await extractResume(resumeFormData);
          if (!resumeExtractResponse.data || !resumeExtractResponse.data.resume_entites) {
            throw new Error('Failed to extract resume entities');
          }
        }
        finalResumeJSON = resumeExtractResponse.data.resume_entites;
        setResumeJSON(finalResumeJSON);
      } catch (error) {
        alert('Failed to extract resume entities: ' + (error.message || 'Unknown error'));
        setIsProcessing(false);
        setLoadingMessage('');
        return;
      }

      // Extract JSON from job description text
      setLoadingMessage('Extracting Job Description Entities...');
      const jdFormData = new FormData();
      jdFormData.append('jd_text', finalJobDescription);
      jdFormData.append('model_id', selectedModel);
      
      let jdExtractResponse;
      try {
        jdExtractResponse = await extractJD(jdFormData);
        if (!jdExtractResponse.data || !jdExtractResponse.data.jd_entites) {
          // First attempt failed, try once more
          jdExtractResponse = await extractJD(jdFormData);
          if (!jdExtractResponse.data || !jdExtractResponse.data.jd_entites) {
            throw new Error('Failed to extract job description entities');
          }
        }
        finalJobJSON = jdExtractResponse.data.jd_entites;
        setJobJSON(finalJobJSON);
      } catch (error) {
        alert('Failed to extract job description entities: ' + (error.message || 'Unknown error'));
        setIsProcessing(false);
        setLoadingMessage('');
        return;
      }

      // Make the match using the extracted JSONs
      setLoadingMessage('Analyzing Match...');
      const matchResponse = await makeMatch(finalResumeJSON, finalJobJSON);
      if (!matchResponse.data || !matchResponse.data.match_report) {
        alert('Failed to generate match report: ' + (matchResponse.data?.error || 'Unknown error'));
        setIsProcessing(false);
        setLoadingMessage('');
        return;
      }

      // Calculate total time taken
      const endTime = Date.now();
      const timeTaken = endTime - startTime;
      setMatchTime(timeTaken);

      // Store the match report and show the modal
      setMatchReport(matchResponse.data.match_report);
      setShowScoreReport(true);
      
    } catch (error) {
      console.error('Error in match process:', error);
      alert('Error processing match. Please try again.');
    } finally {
      setIsProcessing(false);
      setLoadingMessage('');
    }
  };

  const resetDashboard = () => {
    setResumeText('');
    setJobDescription('');
    setResumeFile(null);
    setJobLink('');
    setResumeJSON(null);
    setJobJSON(null);
    setMatchReport(null);
    setMatchTime(null);
    setResumeMethod('none');
    setJobMethod('none');
    setLoadingMessage('');
    setIsProcessing(false);
    
    // Reset file input if it exists
    const fileInput = document.getElementById('resume-upload');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleCloseScoreReport = async () => {
    try {
      const userEmail = localStorage.getItem('email');
      if (!userEmail) {
        console.error('No user email found');
        return;
      }

      // Add to history
      await addHistory(
        userEmail,
        resumeText,
        resumeJSON,
        jobDescription,
        jobJSON,
        matchReport
      );

      // Refresh past matches
      if (pastMatchesRef.current && pastMatchesRef.current.refresh) {
        pastMatchesRef.current.refresh();
      }

      // Close the modal and reset dashboard
      setShowScoreReport(false);
      resetDashboard();
    } catch (error) {
      console.error('Error adding to history:', error);
      setShowScoreReport(false);
      resetDashboard();
    }
  };

  const handleScrollToHistory = () => {
    if (hasPastMatches === false) {
      if (historyBtnRef.current) {
        const rect = historyBtnRef.current.getBoundingClientRect();
        setPopupPos({
          top: rect.top - 48, // 48px above the button
          left: rect.left + rect.width / 2
        });
      }
      setShowNoMatchesPopup(true);
      setTimeout(() => setShowNoMatchesPopup(false), 2000);
      return;
    }
    if (pastMatchesRef.current) {
      pastMatchesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleDeleteAccountClick = () => {
    setShowDeleteModal(true);
    setDeletePassword('');
    setDeleteError('');
  };

  const handleDeleteModalClose = () => {
    setShowDeleteModal(false);
    setDeletePassword('');
    setDeleteError('');
  };

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    setDeleteError('');
    try {
      const email = localStorage.getItem('email');
      if (!email) throw new Error('No user email found');
      await deleteUser(email, deletePassword);
      await deleteAll(email);
      localStorage.removeItem('token');
      localStorage.removeItem('name');
      localStorage.removeItem('email');
      navigate('/auth');
    } catch (err) {
      // Show error from API if available
      const apiError = err?.response?.data?.error || err?.response?.data?.message || err.message || 'Failed to delete account';
      setDeleteError(apiError);
    } finally {
      setIsDeleting(false);
    }
  };

  // Listen for changes in PastMatches and update hasPastMatches
  // We'll use a callback ref to get matches count from PastMatches
  const handlePastMatchesCount = (count) => {
    setHasPastMatches(count > 0);
  };

  const handleToggleDarkMode = () => setDarkMode(dm => !dm);

  const handleModelSelect = (modelId) => {
    setSelectedModel(modelId);
    localStorage.setItem('modelID', modelId);
    setShowModelDropdown(false);
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="dashboard-container fade-in">
      {/* Sidebar */}
      <div className="dashboard-sidebar">
        <div className="sidebar-header">
          <img src="/logo.png" alt="ScoreIt Logo" className="sidebar-logo" />
        </div>
        
        <div className="sidebar-buttons">
          <button ref={historyBtnRef} className="nav-item" onClick={handleScrollToHistory}>
            <span className="nav-icon">📈</span>
            History
          </button>
          <button onClick={handleLogout} className="sidebar-logout">
            <span className="nav-icon">🚪</span>
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-main">
        {/* Top Navigation Bar */}
        <nav className="top-nav">
          <div className="welcome-message">
            Welcome to ScoreIt.AI, <span className="user-name">{userName}</span> !
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button
              className="dark-mode-toggle"
              onClick={handleToggleDarkMode}
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '1.6rem',
                cursor: 'pointer',
                color: darkMode ? '#fbbf24' : '#374151',
                marginRight: '0.5rem',
                transition: 'color 0.2s'
              }}
            >
              {darkMode ? '🌙' : '☀️'}
            </button>
            <div className="profile-section">
              <button className="profile-button" onClick={toggleProfileDropdown}>
                <span className="profile-icon">👤</span>
                <span className="profile-text">Profile</span>
              </button>
              {showProfileDropdown && (
                <div className="profile-dropdown">
                  <div style={{ position: 'relative' }}>
                    <button
                      className="dropdown-item"
                      onMouseEnter={() => setShowProfileTooltip(true)}
                      onMouseLeave={() => setShowProfileTooltip(false)}
                      onFocus={() => setShowProfileTooltip(true)}
                      onBlur={() => setShowProfileTooltip(false)}
                    >
                      <span className="dropdown-icon">👤</span>
                      My Profile
                    </button>
                    {showProfileTooltip && (
                      <div style={{
                        position: 'absolute',
                        right: '100%',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: '#18181b',
                        color: '#fff',
                        padding: '0.5rem 1rem',
                        borderRadius: 8,
                        whiteSpace: 'nowrap',
                        fontSize: '0.95rem',
                        marginRight: '0.5rem',
                        zIndex: 2002,
                        boxShadow: '0 2px 8px rgba(0,0,0,0.12)'
                      }}>
                        Feature under development
                      </div>
                    )}
                  </div>
                  <button
                    className="dropdown-item settings-parent"
                    onMouseEnter={() => setShowDeleteAccount(true)}
                    onMouseLeave={() => setShowDeleteAccount(false)}
                    onFocus={() => setShowDeleteAccount(true)}
                    onBlur={() => setShowDeleteAccount(false)}
                  >
                    <span className="dropdown-icon">⚙️</span>
                    Settings
                  </button>
                  {showDeleteAccount && (
                    <button
                      className="dropdown-item delete-account-btn"
                      onClick={handleDeleteAccountClick}
                      onMouseEnter={() => setShowDeleteAccount(true)}
                      onMouseLeave={() => setShowDeleteAccount(false)}
                    >
                      Delete Account?
                    </button>
                  )}
                  <div className="dropdown-divider"></div>
                  <button className="dropdown-item" onClick={handleLogout}>
                    <span className="dropdown-icon">🚪</span>
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="dashboard-content">
          <div className="input-sections">
            {/* Resume Section */}
            <div className="input-section resume-section">
              <h2>
                Resume
                <button onClick={handleResumeReset} className="reset-button">
                  Reset
                </button>
              </h2>
              <div className="text-input-container">
                <textarea
                  className="text-input"
                  placeholder="Paste your resume text here..."
                  value={resumeText}
                  onChange={handleResumeTextChange}
                  disabled={resumeMethod === 'file'}
                />
              </div>
              <div className="alternative-input">
                <div className="file-upload">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleResumeFileUpload}
                    id="resume-upload"
                    className="file-input"
                    disabled={resumeMethod === 'text'}
                  />
                  <label 
                    htmlFor="resume-upload" 
                    className={`file-label ${resumeMethod === 'text' ? 'disabled' : ''}`}
                  >
                    Or Upload Resume
                  </label>
                </div>
              </div>
            </div>

            {/* Job Description Section */}
            <div className="input-section job-section">
              <h2>
                Job Description
                <button onClick={handleJobReset} className="reset-button">
                  Reset
                </button>
              </h2>
              <div className="text-input-container">
                <textarea
                  className="text-input"
                  placeholder="Paste job description here..."
                  value={jobDescription}
                  onChange={handleJobDescriptionChange}
                  disabled={jobMethod === 'link'}
                />
              </div>
              <div className="alternative-input">
                <div className="link-input">
                  <input
                    type="url"
                    placeholder="Or Paste Job Link"
                    value={jobLink}
                    onChange={handleJobLinkChange}
                    className="url-input"
                    disabled={jobMethod === 'text'}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Model Selector */}
          <div className="model-selector-container">
            <div className="model-selector" onClick={() => setShowModelDropdown(!showModelDropdown)}>
              <span>
                {models[selectedModel] ? (
                  <>
                    {models[selectedModel].NAME}
                    {models[selectedModel].MODEL_TYPE === 'paid' && <span className="model-paid"> $</span>}
                  </>
                ) : (
                  'Choose Model'
                )}
              </span>
              <span className="model-selector-arrow">▼</span>
            </div>
            {showModelDropdown && (
              <div className="model-dropdown">
                {Object.entries(models).map(([id, model]) => (
                  <div
                    key={id}
                    className="model-option"
                    onClick={() => handleModelSelect(id)}
                  >
                    <span className="model-check">{selectedModel === id ? '✓' : ''}</span>
                    <span className="model-name">{model.NAME}</span>
                    {model.MODEL_TYPE === 'paid' && <span className="model-paid">$</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Make Match Button */}
          <div className="match-button-container">
            <button 
              className={`match-button ${isMatchEnabled() ? 'enabled' : 'disabled'}`}
              onClick={handleMatch}
              disabled={!isMatchEnabled() || isProcessing}
            >
              {isProcessing ? (
                <>
                  <div className="button-spinner"></div>
                  {loadingMessage}
                </>
              ) : !isMatchEnabled() ? (
                'Please provide both Resume and Job Description'
              ) : (
                'Make Match'
              )}
            </button>
          </div>

          {/* Score Report Modal */}
          {showScoreReport && matchReport && (
            <ScoreReport 
              matchReport={matchReport} 
              onClose={handleCloseScoreReport}
              matchTime={matchTime}
            />
          )}

          <PastMatches ref={pastMatchesRef} onCountChange={handlePastMatchesCount} />
          <footer className="past-matches-footer">
            <div className="footer-title">ScoreIt.AI v1.0.0</div>
            <div className="footer-author">Developed by Aman Jain</div>
            <div className="footer-email">amanjn2003@gmail.com</div>
          </footer>
        </main>
      </div>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" style={{zIndex: 3000}}>
          <div className="modal-content" style={{margin: 'auto', padding: '2rem', textAlign: 'center', width: '30vw', marginLeft: '44vw', alignItems: 'center', justifyContent: 'center', alignSelf: 'center'}}>
            <h2>Delete Account</h2>
            <p style={{marginBottom: '1rem'}}>This will permanently delete your account and all match history. This action cannot be undone.</p>
            <input
              type="password"
              placeholder="Enter your password to confirm"
              value={deletePassword}
              onChange={e => setDeletePassword(e.target.value)}
              style={{width: '100%', padding: '0.75rem', borderRadius: 8, border: '1px solid #e5e7eb', marginBottom: '1rem'}}
              disabled={isDeleting}
            />
            {deleteError && <div style={{color: '#ef4444', marginBottom: '1rem'}}>{deleteError}</div>}
            <div style={{display: 'flex', justifyContent: 'center', gap: '1rem'}}>
              <button onClick={handleDeleteModalClose} style={{padding: '0.7rem 2rem', borderRadius: 8, border: 'none', background: '#e5e7eb', color: '#374151', fontWeight: 600}} disabled={isDeleting}>Cancel</button>
              <button onClick={handleConfirmDelete} style={{padding: '0.7rem 2rem', borderRadius: 8, border: 'none', background: '#ef4444', color: '#fff', fontWeight: 600}} disabled={isDeleting || !deletePassword}>{isDeleting ? 'Deleting...' : 'Delete'}</button>
            </div>
          </div>
        </div>
      )}

      {showNoMatchesPopup && (
        <div
          className={`no-matches-popup ${showNoMatchesPopup ? 'show' : ''}`}
          style={{
            position: 'fixed',
            top: popupPos.top,
            left: popupPos.left,
            transform: 'translate(-50%, -100%)',
            background: '#18181b',
            color: '#fff',
            padding: '1rem 2rem',
            borderRadius: 10,
            fontSize: '1.1rem',
            zIndex: 4000,
            boxShadow: '0 2px 8px rgba(0,0,0,0.18)',
            pointerEvents: 'auto',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            transition: 'opacity 0.4s cubic-bezier(.4,2,.6,1), transform 0.4s cubic-bezier(.4,2,.6,1)'
          }}
          onClick={() => setShowNoMatchesPopup(false)}
        >
          You have no past matches.
        </div>
      )}
    </div>
  );
};

export default Dashboard; 