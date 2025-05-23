import React from 'react';
import '../styles/ScoreRow.css';

const ScoreRow = ({ label, value, percentage, color }) => {
  return (
    <div className="score-row">
      <div className="score-bar-container">
        <div 
          className="score-bar" 
          style={{ 
            width: `${percentage}%`,
            backgroundColor: color || '#10b981'
          }}
        />
        <div className="score-text">
          <span className="score-label">{label}</span>
          <span className="score-value">{value}</span>
        </div>
      </div>
    </div>
  );
};

export default ScoreRow; 