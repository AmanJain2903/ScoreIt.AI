import React, { useEffect, useRef } from 'react';
import '../styles/ScoreReport.css';

const ScoreReport = ({ matchReport, onClose, matchTime }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    // Add animation class after component mounts
    if (modalRef.current) {
      modalRef.current.classList.add('show');
    }
  }, []);

  const formatTime = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}m ${seconds}s`;
  };

  const getScoreColor = (score) => {
    // Define color stops for the gradient
    const colorStops = [
      { threshold: 0, color: '#ef4444' },    // Red
      { threshold: 0.2, color: '#f97316' },  // Orange
      { threshold: 0.4, color: '#f59e0b' },  // Yellow
      { threshold: 0.6, color: '#84cc16' },  // Light Green
      { threshold: 0.8, color: '#10b981' },  // Green
      { threshold: 1, color: '#059669' }     // Dark Green
    ];

    // Find the appropriate color based on the score
    for (let i = 0; i < colorStops.length - 1; i++) {
      const currentStop = colorStops[i];
      const nextStop = colorStops[i + 1];
      
      if (score >= currentStop.threshold && score <= nextStop.threshold) {
        // Calculate the position between the two color stops
        const position = (score - currentStop.threshold) / 
                        (nextStop.threshold - currentStop.threshold);
        
        // Interpolate between the two colors
        return interpolateColor(currentStop.color, nextStop.color, position);
      }
    }
    
    return colorStops[colorStops.length - 1].color;
  };

  // Helper function to interpolate between two colors
  const interpolateColor = (color1, color2, factor) => {
    const hex1 = color1.replace('#', '');
    const hex2 = color2.replace('#', '');
    
    const r1 = parseInt(hex1.substring(0, 2), 16);
    const g1 = parseInt(hex1.substring(2, 4), 16);
    const b1 = parseInt(hex1.substring(4, 6), 16);
    
    const r2 = parseInt(hex2.substring(0, 2), 16);
    const g2 = parseInt(hex2.substring(2, 4), 16);
    const b2 = parseInt(hex2.substring(4, 6), 16);
    
    const r = Math.round(r1 + (r2 - r1) * factor);
    const g = Math.round(g1 + (g2 - g1) * factor);
    const b = Math.round(b1 + (b2 - b1) * factor);
    
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  };

  const formatScore = (score) => {
    return `${Math.round(score * 100)}%`;
  };

  const formatLabel = (label) => {
    if (label === 'TOOL') return 'Tools Used';
    return label
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  // Define the order of keys
  const orderedKeys = [
    'EDUCATION',
    'EXPERIENCE',
    'TECHNICAL_SKILL',
    'SOFT_SKILL',
    'TOOL',
    'DESIGNATION',
    'CERTIFICATION'
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" ref={modalRef} onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <div className="score-report">
          <h2>Match Report</h2>
          {matchTime && (
            <div className="match-time">
              Time taken: {formatTime(matchTime)}
            </div>
          )}
          <div className="score-bars">
            {orderedKeys.map((key) => (
              <div key={key} className="score-item">
                <div className="score-label">{formatLabel(key)}</div>
                <div className="score-bar-container">
                  <div 
                    className="score-bar" 
                    style={{ 
                      width: `${matchReport[key] * 100}%`,
                      backgroundColor: getScoreColor(matchReport[key])
                    }}
                  />
                </div>
                <div className="score-value">{formatScore(matchReport[key])}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreReport; 