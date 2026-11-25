import React from 'react';

const BrainIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v0A2.5 2.5 0 0 1 9.5 7h-3A2.5 2.5 0 0 1 4 4.5v0A2.5 2.5 0 0 1 6.5 2h3Z"></path>
        <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v0A2.5 2.5 0 0 0 14.5 7h3A2.5 2.5 0 0 0 20 4.5v0A2.5 2.5 0 0 0 17.5 2h-3Z"></path>
        <path d="M12 18.5c-2.76 0-5-2.24-5-5 0-1.07.33-2.07.9-2.88.6-.85 1.4-1.5 2.3-2.02.9-.52 2-1.01 3.1-1.01s2.2.49 3.1 1.01c.9.52 1.7 1.17 2.3 2.02.57.8.9 1.8.9 2.88 0 2.76-2.24 5-5 5Z"></path>
        <path d="M20 10.2c.7 1.1 1 2.4 1 3.8 0 2.76-2.24 5-5 5s-5-2.24-5-5c0-1.4.3-2.7 1-3.8"></path>
        <path d="M4 10.2c-.7 1.1-1 2.4-1 3.8 0 2.76 2.24 5 5 5s5-2.24 5-5c0-1.4-.3-2.7-1-3.8"></path>
        <path d="M12 21.5V18.5"></path>
    </svg>
);

export default BrainIcon;
