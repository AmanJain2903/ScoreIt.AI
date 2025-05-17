import React, { useState, useEffect, forwardRef, useImperativeHandle, useRef } from 'react';
import { getHistory, deleteOne, deleteAll } from '../api/history';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import '../styles/PastMatches.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const SCORE_ORDER = [
  'EDUCATION',
  'EXPERIENCE',
  'TECHNICAL_SKILL',
  'SOFT_SKILL',
  'TOOL',
  'CERTIFICATION',
  'DESIGNATION'
];

const SCORE_LABELS = {
  EDUCATION: 'Education',
  EXPERIENCE: 'Experience',
  TECHNICAL_SKILL: 'Technical Skill',
  SOFT_SKILL: 'Soft Skill',
  TOOL: 'Tools Used',
  CERTIFICATION: 'Certification',
  DESIGNATION: 'Designation'
};

const PastMatches = forwardRef((props, ref) => {
  const { onCountChange } = props;
  const sectionRef = useRef(null);
  const [matches, setMatches] = useState([]);
  const [expandedMatch, setExpandedMatch] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchMatches();
  }, []);

  useEffect(() => {
    if (onCountChange) {
      onCountChange(matches.length);
    }
  }, [matches, onCountChange]);

  const fetchMatches = async () => {
    try {
      const userEmail = localStorage.getItem('email');
      if (!userEmail) return;

      const response = await getHistory(userEmail);
      if (response.data && response.data.history) {
        setMatches(response.data.history);
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteMatch = async (match) => {
    try {
      console.log('Deleting match:', match);
      const userEmail = localStorage.getItem('email');
      if (!userEmail) return;

      await deleteOne(userEmail, match);
      setMatches(matches.filter(m => m._id !== match));
      if (expandedMatch === match) {
        setExpandedMatch(null);
      }
    } catch (error) {
      console.error('Error deleting match:', error);
    }
  };

  const handleClearHistory = async () => {
    try {
      const userEmail = localStorage.getItem('email');
      if (!userEmail) return;

      await deleteAll(userEmail);
      setMatches([]);
      setExpandedMatch(null);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#10B981'; // Green
    if (score >= 0.6) return '#3B82F6'; // Blue
    if (score >= 0.4) return '#F59E0B'; // Yellow
    return '#EF4444'; // Red
  };

  const getMatchDateValue = (match) => {
    // Debug log
    // eslint-disable-next-line no-console
    console.log('match.timestamp:', match.timestamp);
    if (match.timestamp) {
      // If it's a string or number, return directly
      if (typeof match.timestamp === 'string' || typeof match.timestamp === 'number') {
        return match.timestamp;
      }
      // If it's a MongoDB extended JSON object
      if (match.timestamp.$date) {
        if (typeof match.timestamp.$date === 'string' || typeof match.timestamp.$date === 'number') {
          return match.timestamp.$date;
        }
        if (match.timestamp.$date.$numberLong) {
          return Number(match.timestamp.$date.$numberLong);
        }
      }
    }
    return null;
  };

  const formatDate = (dateValue) => {
    if (!dateValue) return 'No date';
    let dateObj;
    if (typeof dateValue === 'number' || !isNaN(Number(dateValue))) {
      dateObj = new Date(Number(dateValue));
    } else {
      dateObj = new Date(dateValue);
    }
    if (isNaN(dateObj.getTime())) return 'Invalid date';
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    let hours = dateObj.getHours();
    const minutes = String(dateObj.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    const hourStr = String(hours).padStart(2, '0');
    return `${year}-${month}-${day}  ${hourStr}:${minutes} ${ampm}`;
  };

  // Radar chart options
  const getRadarOptions = (color) => ({
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `${context.label}: ${(context.parsed.r * 100).toFixed(1)}%`
        }
      }
    },
    scales: {
      r: {
        angleLines: { color: 'var(--border-color)' },
        grid: { color: 'var(--border-color)' },
        pointLabels: {
          color: 'var(--text-secondary)',
          font: { size: 13 }
        },
        min: 0,
        max: 1,
        ticks: {
          display: false
        }
      }
    }
  });

  // Helper to get string id
  const getMatchId = (match) => match._id;
  // Find the expanded match object
  const expandedMatchObj = matches.find(m => getMatchId(m) === expandedMatch);

  const sortedMatches = [...matches].sort((a, b) => {
    const aTime = getMatchDateValue(a);
    const bTime = getMatchDateValue(b);
    // Convert to numbers for comparison
    const aNum = typeof aTime === 'string' ? Date.parse(aTime) : Number(aTime);
    const bNum = typeof bTime === 'string' ? Date.parse(bTime) : Number(bTime);
    return bNum - aNum; // Descending order
  });

  useImperativeHandle(ref, () => ({
    refresh: fetchMatches,
    scrollIntoView: (options) => {
      if (sectionRef.current) sectionRef.current.scrollIntoView(options);
    }
  }));

  if (isLoading) {
    return <div className="loading-spinner"></div>;
  }

  return (
    <>
      {matches.length > 0 && (
        <div className="past-matches-container">
          <div className="past-matches-section" ref={sectionRef}>
            <div className="section-header">
              <h2>Past Matches</h2>
              <button className="clear-history-button" onClick={handleClearHistory}>
                Clear History
              </button>
            </div>
            <div className="matches-grid">
              {sortedMatches.map((match) => {
                // Prepare radar data
                const labels = SCORE_ORDER.map(key => SCORE_LABELS[key]);
                const data = SCORE_ORDER.map(label => match.match_report[label] ?? 0);
                // Use the average score for color
                const avgScore = data.reduce((a, b) => a + b, 0) / data.length;
                const color = getScoreColor(avgScore);
                return (
                  <div key={match._id} className="match-card">
                    <div className="match-header">
                      <span className="match-date">{formatDate(getMatchDateValue(match))}</span>
                    </div>
                    <div 
                      className={`score-radar clickable`}
                      onClick={() => setExpandedMatch(getMatchId(match))}
                      style={{ cursor: 'pointer' }}
                    >
                      <Radar
                        data={{
                          labels,
                          datasets: [
                            {
                              label: 'Match Scores',
                              data,
                              backgroundColor: color + '33', // semi-transparent fill
                              borderColor: color,
                              pointBackgroundColor: color,
                              pointBorderColor: color,
                              borderWidth: 2,
                              fill: true
                            }
                          ]
                        }}
                        options={getRadarOptions(color)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Render the modal only once at the root */}
            {expandedMatchObj && (
              <div className="past-match-modal-overlay" onClick={() => setExpandedMatch(null)}>
                <div className="past-match-modal" onClick={e => e.stopPropagation()}>
                  <div className="modal-header">
                    <span className="modal-date">{formatDate(getMatchDateValue(expandedMatchObj))}</span>
                    <button className="modal-close" onClick={() => setExpandedMatch(null)} title="Close">✖</button>
                  </div>
                  <div className="modal-top-section">
                    <div className="modal-resume">
                      <h3>Resume</h3>
                      <div className="text-content">{expandedMatchObj.resume_text}</div>
                    </div>
                    <div className="modal-jd">
                      <h3>Job Description</h3>
                      <div className="text-content">{expandedMatchObj.jd_text}</div>
                    </div>
                  </div>
                  <div className="modal-section">
                    <h3>Detailed Scores</h3>
                    <div className="detailed-scores">
                      {Object.entries(expandedMatchObj.match_report).map(([key, value]) => (
                        <div key={key} className="score-item">
                          <span className="score-label">{SCORE_LABELS[key] || key}</span>
                          <div className="score-bar-container">
                            <div 
                              className="score-bar"
                              style={{
                                width: `${value * 100}%`,
                                backgroundColor: getScoreColor(value)
                              }}
                            />
                          </div>
                          <span className="score-value">{(value * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button className="modal-delete" onClick={() => { handleDeleteMatch(expandedMatchObj._id && expandedMatchObj._id.$oid ? expandedMatchObj._id.$oid : expandedMatchObj._id); setExpandedMatch(null); }} title="Delete">🗑️ Delete Match</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
});

export default PastMatches; 