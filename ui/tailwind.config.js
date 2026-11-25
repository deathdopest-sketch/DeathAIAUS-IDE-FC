/** @type {import('tailwindcss').Config} */

// DeathAI Australia design system — see DESIGN_SYSTEM.md.
// Every hue resolves to a CSS channel variable (styles/tokens.css), so themes
// swap at runtime and opacity modifiers like `bg-blood/40` still work.
const hue = (name) => {
  const tier = (t) => `rgb(var(--c-${name}-${t}) / <alpha-value>)`;
  return {
    DEFAULT: tier('base'),
    50: tier('light'), 100: tier('light'), 200: tier('light'), 300: tier('light'), 400: tier('light'),
    500: tier('base'), 600: tier('base'),
    700: tier('deep'), 800: tier('deep'), 900: tier('deep'), 950: tier('deep'),
  };
};

const blood = hue('blood');
const signal = hue('signal');
const phosphor = hue('phosphor');
const amber = hue('amber');
const ochre = hue('ochre');
const ash = hue('ash');

export default {
  content: [
    './index.html',
    './*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './services/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand names
        blood, signal, phosphor, amber, ochre, ash,
        void: 'rgb(var(--c-void) / <alpha-value>)',
        bone: 'rgb(var(--c-bone) / <alpha-value>)',
        // Legacy Tailwind hues used across older components, folded into the brand
        indigo: blood, purple: blood, violet: blood, red: blood, rose: blood, pink: blood,
        blue: signal, cyan: signal, sky: signal, teal: signal,
        green: phosphor, lime: phosphor, emerald: phosphor,
        yellow: amber, orange: ochre,
        gray: ash, slate: ash, zinc: ash, neutral: ash,
      },
      fontFamily: {
        sans: ['"Chakra Petch"', 'system-ui', 'sans-serif'],
        display: ['"Chakra Petch"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
      borderRadius: {
        none: '0', sm: '0', DEFAULT: '2px', md: '2px', lg: '3px', xl: '4px', full: '9999px',
      },
      boxShadow: {
        bleed: '0 0 0 1px rgb(var(--c-blood-base) / .6), 0 0 18px -4px rgb(var(--c-blood-base) / .55)',
        signal: '0 0 0 1px rgb(var(--c-signal-base) / .5), 0 0 18px -6px rgb(var(--c-signal-base) / .5)',
        split: '-2px 0 0 rgb(var(--c-blood-base) / .8), 2px 0 0 rgb(var(--c-signal-base) / .8)',
      },
      letterSpacing: { hud: '0.18em' },
      keyframes: {
        'fade-in-right': {
          '0%': { opacity: 0, transform: 'translateX(24px) skewX(-8deg)', filter: 'blur(2px)' },
          '30%': { opacity: 1, transform: 'translateX(-4px) skewX(4deg)' },
          '45%': { transform: 'translateX(3px) skewX(0)', clipPath: 'inset(20% 0 40% 0)' },
          '60%': { clipPath: 'inset(0 0 0 0)' },
          '100%': { opacity: 1, transform: 'translateX(0)', filter: 'none' },
        },
      },
      animation: {
        'fade-in-right': 'fade-in-right .45s steps(8, end) both',
      },
    },
  },
  plugins: [],
};
