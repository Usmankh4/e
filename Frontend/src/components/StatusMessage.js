import React from 'react';

/**
 * Reusable component for displaying loading and error states
 * @param {Object} props - Component props
 * @param {boolean} props.isLoading - Whether content is loading
 * @param {string} props.error - Error message if any
 * @param {Function} props.onBack - Optional callback for back button
 * @param {string} props.loadingMessage - Custom loading message
 * @param {string} props.errorTitle - Custom error title
 */
export default function StatusMessage({ 
  isLoading, 
  error, 
  onBack, 
  loadingMessage = "Loading...",
  errorTitle = "Error"
}) {
  if (isLoading) {
    return <div className="loading">{loadingMessage}</div>;
  }
  
  if (error) {
    return (
      <div className="error">
        <h2>{errorTitle}</h2>
        <p>{error}</p>
        {onBack && <button onClick={onBack}>Go Back</button>}
      </div>
    );
  }
  
  return null;
}
