import React from 'react';

const LoadingSpinner = ({ size = "medium" }) => {
  const sizeClasses = {
    small: "w-4 h-4 border-2",
    medium: "w-8 h-8 border-3",
    large: "w-12 h-12 border-4"
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClasses[size]} rounded-full border-t-transparent border-[var(--bg-primary)] animate-spin`}
        style={{ borderTopColor: 'transparent', borderRightColor: 'currentColor', borderBottomColor: 'currentColor', borderLeftColor: 'currentColor' }}
      ></div>
    </div>
  );
};

export default LoadingSpinner;
