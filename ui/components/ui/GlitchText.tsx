import React from 'react';

interface GlitchTextProps {
  text: string;
  as?: 'span' | 'h1' | 'h2' | 'h3';
  /** 'always' keeps slicing; 'hover' only glitches on hover */
  mode?: 'always' | 'hover';
  className?: string;
}

const GlitchText: React.FC<GlitchTextProps> = ({ text, as: Tag = 'span', mode = 'always', className = '' }) => (
  <Tag className={`glitch ${mode === 'hover' ? 'glitch-hover' : ''} ${className}`} data-text={text}>
    {text}
  </Tag>
);

export default GlitchText;
