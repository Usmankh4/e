import React from 'react';

/**
 * Reusable pagination component
 * @param {Object} props - Component props
 * @param {number} props.currentPage - Current page number
 * @param {Function} props.onPageChange - Function to call when page changes
 * @param {boolean} props.hasNextPage - Whether there is a next page
 * @param {boolean} props.hasPreviousPage - Whether there is a previous page
 */
export default function Pagination({ 
  currentPage, 
  onPageChange, 
  hasNextPage = true, 
  hasPreviousPage = false 
}) {
  const handlePrevious = () => {
    if (!hasPreviousPage) return;
    onPageChange(currentPage - 1);
  };

  const handleNext = () => {
    if (!hasNextPage) return;
    onPageChange(currentPage + 1);
  };

  return (
    <div className="pageButton">
      {hasPreviousPage && (
        <button onClick={handlePrevious}>Previous</button>
      )}
      <button onClick={handleNext} disabled={!hasNextPage}>Next</button>
    </div>
  );
}
