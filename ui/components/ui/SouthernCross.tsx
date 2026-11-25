import React from 'react';

// The Southern Cross (Crux + epsilon), positioned as on the Australian flag.
// Used as the "AUS" signature motif — keep it small and quiet.
const STARS: { x: number; y: number; r: number }[] = [
  { x: 50, y: 88, r: 4.2 }, // Alpha Crucis
  { x: 50, y: 12, r: 3.6 }, // Gamma Crucis
  { x: 18, y: 42, r: 3.6 }, // Beta Crucis
  { x: 80, y: 36, r: 3.2 }, // Delta Crucis
  { x: 64, y: 58, r: 2.0 }, // Epsilon Crucis
];

const SouthernCross: React.FC<{ className?: string }> = ({ className = 'w-10 h-10' }) => (
  <svg viewBox="0 0 100 100" className={className} aria-hidden="true">
    <g stroke="currentColor" strokeWidth="0.6" strokeDasharray="2 3" opacity="0.35" fill="none">
      <line x1="50" y1="12" x2="50" y2="88" />
      <line x1="18" y1="42" x2="80" y2="36" />
    </g>
    {STARS.map((s, i) => (
      <path
        key={i}
        fill="currentColor"
        d={`M${s.x} ${s.y - s.r * 2}L${s.x + s.r * 0.5} ${s.y - s.r * 0.5}L${s.x + s.r * 2} ${s.y}L${s.x + s.r * 0.5} ${s.y + s.r * 0.5}L${s.x} ${s.y + s.r * 2}L${s.x - s.r * 0.5} ${s.y + s.r * 0.5}L${s.x - s.r * 2} ${s.y}L${s.x - s.r * 0.5} ${s.y - s.r * 0.5}Z`}
      />
    ))}
  </svg>
);

export default SouthernCross;
