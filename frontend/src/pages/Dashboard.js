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
import Footer from '../components/Footer';
import { updateUser } from '../api/auth';
import { useGoogleLogin } from '@react-oauth/google';
import { deleteAllSessions, deleteSession , logoutAllSessions} from '../api/session';


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
  const [showNoMatchesPopup, setShowNoMatchesPopup] = useState(false);
  const [hasPastMatches, setHasPastMatches] = useState(null); // null = unknown, true/false = known
  const historyBtnRef = useRef(null);
  const [popupPos, setPopupPos] = useState({ top: 100, left: 100 });
  const [darkMode, setDarkMode] =  useState(localStorage.getItem('darkMode') === 'true' || sessionStorage.getItem('darkMode') === 'true');
  const isGoogleUser = localStorage.getItem('isGoogleUser') === 'true' || sessionStorage.getItem('isGoogleUser') === 'true';
  const [models, setModels] = useState({});
  const [selectedModel, setSelectedModel] = useState('1'); // Default to first model
  const [showModelDropdown, setShowModelDropdown] = useState(false);

  useEffect(() => {
    const userName = localStorage.getItem('name') || sessionStorage.getItem('name');
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
    }
    else {
      document.body.classList.remove('dark-mode');
    };
  }, [darkMode]);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await fetchConfig();
        if (response.data) {
          setModels(response.data);
          // Set default model ID
          localStorage.setItem('modelID', '1') || sessionStorage.setItem('modelID', '1');
        }
      } catch (error) {
        console.error('Error loading models:', error);
      }
    };
    loadModels();
  }, []);

  const deleteGoogleUser = useGoogleLogin({
    onSuccess: async (credentialResponse) => {
      try {
        const accessToken = credentialResponse.access_token;
        const email = localStorage.getItem('email') || sessionStorage.getItem('email'); 
  
        if (!accessToken || !email) {
          throw new Error('Missing access token or email');
        }
  
        await deleteUser(email, accessToken);
        await deleteAll(email);
        try{
          await deleteAllSessions(email);
        }
        catch(err){
        }
  
        // Clear local storage
        localStorage.clear();
        sessionStorage.clear();
        navigate('/auth');
  
      } catch (err) {
        alert(err.message || 'Failed to delete user');
      }
    },
    onError: () => {
      alert('Google re-authentication failed. Cannot delete user.');
    },
    flow: 'implicit',
    scope: 'email profile',
  });

  const handleLogout = async() => {
    const email = localStorage.getItem('email') || sessionStorage.getItem('email');
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    try{
      await deleteSession(email, token);
    }
    catch(err){
    }
    localStorage.clear();
    sessionStorage.clear();
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
      const userEmail = localStorage.getItem('email') || sessionStorage.getItem('email');
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

  const handleDeleteAccountClick = async() => {
    if (isGoogleUser) {
      deleteGoogleUser();
    }
    else{
      setShowDeleteModal(true);
      setDeletePassword('');
      setDeleteError('');
    }
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
      const email = localStorage.getItem('email') || sessionStorage.getItem('email');
      if (!email) throw new Error('No user email found');
      await deleteUser(email, deletePassword);
      await deleteAll(email);
      localStorage.clear();
      sessionStorage.clear();
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

  const handleToggleDarkMode = async() => {
    const isLocal = localStorage.getItem('darkMode') !== null;
    const isSession = sessionStorage.getItem('darkMode') !== null;
    let currentMode;
    if (isLocal){
      currentMode = localStorage.getItem('darkMode')==='true';
      localStorage.setItem('darkMode', (!currentMode).toString());
      setDarkMode(localStorage.getItem('darkMode')==='true');
    }
    else if (isSession){
      currentMode = sessionStorage.getItem('darkMode')==='true';
      sessionStorage.setItem('darkMode', (!currentMode).toString());
      setDarkMode(sessionStorage.getItem('darkMode')==='true');
    }
    else{
      currentMode = true;
      localStorage.setItem('darkMode', 'true');
      sessionStorage.setItem('darkMode', 'true');
      setDarkMode(localStorage.getItem('darkMode')==='true' || sessionStorage.getItem('darkMode')==='true');
    }
    const email = localStorage.getItem('email') || sessionStorage.getItem('email');
    if (!email) throw new Error('No user email found');
    try{
      await updateUser(email);
    }
    catch(err){
    }
  }

  const handleModelSelect = (modelId) => {
    setSelectedModel(modelId);
    localStorage.setItem('modelID', modelId) || sessionStorage.setItem('modelID', modelId);
    setShowModelDropdown(false);
  };

  const handleLogoutAllDevices = async() => {
    const email = localStorage.getItem('email') || sessionStorage.getItem('email');
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    try{
      await logoutAllSessions(email, token);
    }
    catch(err){
    }
    localStorage.clear();
    sessionStorage.clear();
    navigate('/auth');
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
            <img src="/history.png" alt="History" className="nav-icon" style={{ width: '1.3em', height: '1.3em' }} />
            History
          </button>
          <button onClick={handleLogout} className="sidebar-logout">
            <img src="/logout.png" alt="Logout" className="nav-icon" style={{ width: '1.3em', height: '1.3em' }} />
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
                  {showDeleteAccount && 
                  (
                    <>
                      <button
                        className="dropdown-item logout-all-btn"
                        onClick={handleLogoutAllDevices}
                        onMouseEnter={() => setShowDeleteAccount(true)}
                        onMouseLeave={() => setShowDeleteAccount(false)}
                      >
                        Log Out From All Devices?
                      </button>
                      <button
                        className="dropdown-item delete-account-btn"
                        onClick={handleDeleteAccountClick}
                        onMouseEnter={() => setShowDeleteAccount(true)}
                        onMouseLeave={() => setShowDeleteAccount(false)}
                      >
                        Delete Account?
                      </button>
                    </>
                  )
                  }
                  <div className="dropdown-divider"></div>
                  <button className="dropdown-item logout-btn" onClick={handleLogout}>
                    <img src="/logout.png" alt="Logout" className="dropdown-icon" style={{ width: '1.3em', height: '1.3em' }} />
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
              <div className="section-heading-flex">
                <h2>Resume</h2>
                <button onClick={handleResumeReset} className="reset-button">Reset</button>
              </div>
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
              <div className="section-heading-flex">
                <h2>Job Description</h2>
                <button onClick={handleJobReset} className="reset-button">Reset</button>
              </div>
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
              isOpen={showScoreReport}
              onClose={handleCloseScoreReport}
              matchData={{
                timestamp: Date.now(),
                totalScore: 100,
                battingScore: matchReport.EDUCATION * 100,
                bowlingScore: matchReport.EXPERIENCE * 100,
                fieldingScore: matchReport.TECHNICAL_SKILL * 100,
                education: matchReport.EDUCATION * 100,
                experience: matchReport.EXPERIENCE * 100,
                technicalSkill: matchReport.TECHNICAL_SKILL * 100,
                softSkill: matchReport.SOFT_SKILL * 100,
                tool: matchReport.TOOL * 100,
                certification: matchReport.CERTIFICATION * 100,
                designation: matchReport.DESIGNATION * 100,
                timeTaken: matchTime
              }}
            />
          )}
          <PastMatches ref={pastMatchesRef} onCountChange={handlePastMatchesCount} />
        </main>
        <Footer />
      </div>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="dashboard-delete-modal">
            <h2>Delete Account</h2>
            <p>This will permanently delete your account and all match history. This action cannot be undone.</p>
            <input
              type="password"
              placeholder="Enter your password to confirm"
              value={deletePassword}
              onChange={e => setDeletePassword(e.target.value)}
              disabled={isDeleting}
            />
            {deleteError && <div className="delete-error">{deleteError}</div>}
            <div className="delete-modal-actions">
              <button onClick={handleDeleteModalClose} className="delete-cancel-btn" disabled={isDeleting}>Cancel</button>
              <button onClick={handleConfirmDelete} className="delete-confirm-btn" disabled={isDeleting || !deletePassword}>{isDeleting ? 'Deleting...' : 'Delete'}</button>
            </div>
          </div>
        </div>
      )}

      {showNoMatchesPopup && (
        <div
          className={`no-matches-popup-custom ${showNoMatchesPopup ? 'show' : ''}`}
          style={{
            top: popupPos.top,
            left: popupPos.left
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