import React from 'react';

// Pixel-grid skull — the DeathAI mark. Drawn on a 12x12 grid so it stays crisp at any size.
const SkullIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12" fill="currentColor" shapeRendering="crispEdges" className={className} aria-hidden="true">
    <path d="M3 1h6v1h1v1h1v4h-1v1H9v2H8v1H4v-1H3V8H2V7H1V3h1V2h1z M3 4v2h2V4z M7 4v2h2V4z M5 7v1h2V7z M4 9v1h1V9z M7 9v1h1V9z" fillRule="evenodd" />
  </svg>
);

export default SkullIcon;
