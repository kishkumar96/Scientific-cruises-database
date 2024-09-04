import React from 'react';
import './StatusLabel.css'; // Make sure to create and import a CSS file for styling

const StatusLabel = ({ statuses }) => {
  if (!statuses || statuses.length === 0) return <span className="status">N/A</span>;

  return (
    <div className="status-labels">
      {statuses.map((status, index) => (
        <span key={index} className={`status status-${status.toLowerCase().replace(/\s+/g, '-')}`}>
          {status}
        </span>
      ))}
    </div>
  );
};

export default StatusLabel;
