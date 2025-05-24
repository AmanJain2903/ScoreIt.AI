import React from 'react';
import ScoreRow from './ScoreRow';
import '../styles/ScoreReport.css';

const ScoreReport = ({ isOpen, onClose, matchData }) => {
  if (!isOpen || !matchData) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <div className="score-report">
          <h2>Match Scores</h2>
          {typeof matchData.timeTaken === 'number' && (
            <div className="match-time">
              Time Taken: {Math.floor(matchData.timeTaken / 60000)}m {((matchData.timeTaken % 60000) / 1000).toFixed(0)}s
            </div>
          )}
          <div className="score-bars">
            <ScoreRow 
              label="Education"
              value={`${matchData.education.toFixed(1)}%`}
              percentage={matchData.education}
              color="#10b981"
            />
            <ScoreRow 
              label="Experience"
              value={`${matchData.experience.toFixed(1)}%`}
              percentage={matchData.experience}
              color="#3b82f6"
            />
            <ScoreRow 
              label="Technical Skill"
              value={`${matchData.technicalSkill.toFixed(1)}%`}
              percentage={matchData.technicalSkill}
              color="#f59e0b"
            />
            <ScoreRow 
              label="Soft Skill"
              value={`${matchData.softSkill.toFixed(1)}%`}
              percentage={matchData.softSkill}
              color="#ef4444"
            />
            <ScoreRow 
              label="Tools Used"
              value={`${matchData.tool.toFixed(1)}%`}
              percentage={matchData.tool}
              color="#8b5cf6"
            />
            <ScoreRow 
              label="Certification"
              value={`${matchData.certification.toFixed(1)}%`}
              percentage={matchData.certification}
              color="#ec4899"
            />
            <ScoreRow 
              label="Designation"
              value={`${matchData.designation.toFixed(1)}%`}
              percentage={matchData.designation}
              color="#14b8a6"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreReport; 