import React from 'react';

const ReaperIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
    {/* This path creates a stylized, abstract reaper/scythe shape within a circle, designed to be menacing and modern. */}
    <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 3.5c-2.06 0-3.88.94-5.12 2.42l6.23 6.23c.33-.28.61-.6.84-.95l3.17-4.69C16.14 6.71 14.18 5.5 12 5.5zm-6.69 4.31c-.3.4-.55.84-.76 1.31l3.52 3.52c.79-.42 1.68-.64 2.62-.64s1.83.22 2.62.64l3.52-3.52c-.21-.47-.46-.91-.76-1.31L12 14.54l-6.69-4.73zM12 18.5c2.06 0 3.88-.94 5.12-2.42l-6.23-6.23c-.33.28-.61.6-.84.95l-3.17 4.69c1.02 1.77 3 3.01 5.12 3.01z"/>
  </svg>
);

export default ReaperIcon;
