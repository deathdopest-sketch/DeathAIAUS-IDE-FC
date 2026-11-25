// Fix: Implemented the SitemapIcon component.
import React from 'react';

const SitemapIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect width="18" height="7" x="3" y="3" rx="1"/>
        <rect width="7" height="7" x="3" y="14" rx="1"/>
        <rect width="7" height="7" x="14" y="14" rx="1"/>
        <path d="M6 14v-1a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1"/>
        <path d="M12 10V7"/>
    </svg>
);

export default SitemapIcon;
