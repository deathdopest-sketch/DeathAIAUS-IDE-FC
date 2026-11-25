import React, { useEffect, useMemo, useRef, useState } from 'react';

// Haunt effects — web twins of components/death_theme.py in the Tkinter IDE.
// Everything here goes still under prefers-reduced-motion.

const reducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/* -------------------------------------------------------------------------- */
/* Text corruption                                                            */
/* -------------------------------------------------------------------------- */
const ZALGO = Array.from({ length: 0x36f - 0x300 }, (_, i) => String.fromCharCode(0x300 + i));
const SWAP: Record<string, string> = { A: 'Λ', E: 'Ξ', O: 'Ø', I: '|', T: '†', H: '#', S: '$', D: 'Ð', a: 'α', e: 'є', o: 'ø', i: 'ι', t: '†', s: '§' };
const BLOCKS = '▓▒░█▚▞';
const pick = <T,>(xs: ArrayLike<T>) => xs[Math.floor(Math.random() * xs.length)];

export function corrupt(text: string, intensity = 0.25): string {
  let out = '';
  for (const ch of text) {
    const r = Math.random();
    if (ch.trim() && r < intensity * 0.35) out += pick(BLOCKS);
    else if (SWAP[ch] && r < intensity * 0.8) out += SWAP[ch];
    else out += ch;
    if (ch.trim() && Math.random() < intensity * 0.5) out += pick(ZALGO);
  }
  return out;
}

/** Text that occasionally corrupts itself for a few frames, then recovers. */
export const CorruptText: React.FC<{ text: string; every?: [number, number]; intensity?: number; className?: string }> = ({
  text, every = [3000, 8000], intensity = 0.4, className,
}) => {
  const [shown, setShown] = useState(text);
  useEffect(() => {
    setShown(text);
    if (reducedMotion()) return;
    let t: number;
    const schedule = () => {
      t = window.setTimeout(() => {
        let n = 2 + Math.floor(Math.random() * 3);
        const burst = () => {
          if (n-- > 0) { setShown(corrupt(text, intensity)); t = window.setTimeout(burst, 55); }
          else { setShown(text); schedule(); }
        };
        burst();
      }, every[0] + Math.random() * (every[1] - every[0]));
    };
    schedule();
    return () => window.clearTimeout(t);
  }, [text, intensity, every[0], every[1]]);
  return <span className={className} aria-label={text}>{shown}</span>;
};

/* -------------------------------------------------------------------------- */
/* Whispers                                                                   */
/* -------------------------------------------------------------------------- */
export const WHISPERS = [
  'it is still compiling you',
  'something else is in this repo',
  'do not look behind the cursor',
  'the last developer never logged out',
  'your code remembers what you deleted',
  'we are not alone in this process',
  'pid 666 has always been running',
  'it knows which tests you skipped',
  'something answered on port 7777',
  'the build can hear you',
];

/** Returns a whisper string for ~2.6s every 45–120s, otherwise null. */
export function useWhisper(every: [number, number] = [45000, 120000], hold = 2600): string | null {
  const [w, setW] = useState<string | null>(null);
  useEffect(() => {
    if (reducedMotion()) return;
    let t: number;
    const schedule = () => {
      t = window.setTimeout(() => {
        setW(pick(WHISPERS));
        t = window.setTimeout(() => { setW(null); schedule(); }, hold);
      }, every[0] + Math.random() * (every[1] - every[0]));
    };
    schedule();
    return () => window.clearTimeout(t);
  }, []);
  return w;
}

/* -------------------------------------------------------------------------- */
/* Blood drips                                                                */
/* -------------------------------------------------------------------------- */
interface Drip { x: number; w: number; len: number; dur: number; delay: number; falls: boolean; fallDelay: number }

/**
 * Blood seeping down from the top edge of the nearest positioned parent.
 * `maxLen` caps drip length in px; use small values for toolbars.
 */
export const BloodDrips: React.FC<{ count?: number; maxLen?: number; className?: string; seed?: number }> = ({
  count = 18, maxLen = 220, className = '',
}) => {
  const drips = useMemo<Drip[]>(() => Array.from({ length: count }, () => ({
    x: 2 + Math.random() * 96,
    w: [2, 3, 3, 4, 5][Math.floor(Math.random() * 5)],
    len: 6 + Math.random() * maxLen,
    dur: 6 + Math.random() * 18,
    delay: Math.random() * 2,
    falls: Math.random() < 0.35,
    fallDelay: 4 + Math.random() * 10,
  })), [count, maxLen]);

  // Ragged pool along the top edge
  const pool = useMemo(() => {
    let d = 'M0 0 ';
    for (let x = 0; x <= 100; x += 2 + Math.random() * 4) d += `L${x.toFixed(1)} ${(1 + Math.random() * 5).toFixed(1)} `;
    return d + 'L100 0 Z';
  }, []);

  return (
    <div className={`pointer-events-none absolute inset-x-0 top-0 overflow-visible ${className}`} aria-hidden="true">
      <svg className="absolute inset-x-0 top-0 w-full h-2" viewBox="0 0 100 6" preserveAspectRatio="none">
        <path d={pool} fill="rgb(var(--c-blood-deep))" />
      </svg>
      {drips.map((d, i) => (
        <div key={i} className="absolute top-0" style={{ left: `${d.x}%` }}>
          <div
            className="origin-top rounded-b-full"
            style={{
              width: d.w, height: d.len,
              background: 'linear-gradient(rgb(var(--c-blood-deep)), rgb(var(--c-blood-base)) 70%, rgb(var(--c-blood-light) / .9))',
              animation: `drip-grow ${d.dur}s cubic-bezier(.6,.05,.4,1) ${d.delay}s both`,
            }}
          />
          {d.falls && (
            <div
              className="absolute rounded-full"
              style={{
                top: d.len - d.w, left: -d.w * 0.25, width: d.w * 1.5, height: d.w * 2,
                background: 'rgb(var(--c-blood-base))',
                animation: `drop-fall 3.2s ease-in ${d.dur + d.fallDelay}s infinite`,
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* The watching eye                                                           */
/* -------------------------------------------------------------------------- */
export const WatchingEye: React.FC<{ size?: number; className?: string }> = ({ size = 96, className = '' }) => {
  const ref = useRef<SVGSVGElement>(null);
  const [look, setLook] = useState({ x: 0, y: 0 });
  const [lid, setLid] = useState(0); // 0 open … 1 shut
  const veins = useMemo(() => Array.from({ length: 6 }, () => {
    const a = Math.random() * Math.PI * 2;
    const x1 = 50 + Math.cos(a) * 46, y1 = 50 + Math.sin(a) * 25;
    const x2 = 50 + Math.cos(a) * 22, y2 = 50 + Math.sin(a) * 12;
    return `M${x1} ${y1} Q${(x1 + x2) / 2 + (Math.random() * 8 - 4)} ${(y1 + y2) / 2} ${x2} ${y2}`;
  }), []);

  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      const r = ref.current?.getBoundingClientRect();
      if (!r) return;
      const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
      const dist = Math.hypot(dx, dy) || 1, k = Math.min(1, dist / 400);
      setLook({ x: (dx / dist) * 20 * k, y: (dy / dist) * 9 * k });
    };
    window.addEventListener('pointermove', onMove);
    if (reducedMotion()) return () => window.removeEventListener('pointermove', onMove);
    let t: number;
    const blink = () => {
      const seq = [0.35, 0.75, 1, 0.75, 0.35, 0];
      seq.forEach((v, i) => window.setTimeout(() => setLid(v), i * 35));
      t = window.setTimeout(blink, 2500 + Math.random() * 6500);
    };
    t = window.setTimeout(blink, 2000);
    return () => { window.removeEventListener('pointermove', onMove); window.clearTimeout(t); };
  }, []);

  const cx = 50 + look.x, cy = 50 + look.y;
  return (
    <svg ref={ref} viewBox="0 0 100 100" width={size} height={size} className={className} aria-hidden="true">
      <defs>
        <clipPath id="eye-shape"><path d="M4 50 Q50 14 96 50 Q50 86 4 50 Z" /></clipPath>
        <radialGradient id="eye-white" cx="50%" cy="50%" r="60%">
          <stop offset="55%" stopColor="#cbbfae" />
          <stop offset="100%" stopColor="#7a5a52" />
        </radialGradient>
      </defs>
      <g clipPath="url(#eye-shape)">
        <rect width="100" height="100" fill="url(#eye-white)" />
        {veins.map((d, i) => <path key={i} d={d} stroke="rgb(var(--c-blood-base))" strokeWidth="0.8" fill="none" />)}
        <circle cx={cx} cy={cy} r="17" fill="rgb(var(--c-blood-base))" stroke="rgb(var(--c-blood-deep))" strokeWidth="3" />
        <ellipse cx={cx} cy={cy} rx="5" ry="12" fill="rgb(var(--c-void))" />
        <circle cx={cx + 5} cy={cy - 6} r="2" fill="#fff" opacity=".6" />
        <rect x="0" y="0" width="100" height={14 + lid * 72} fill="var(--bg-primary)" />
      </g>
      <path d="M4 50 Q50 14 96 50 Q50 86 4 50 Z" fill="none" stroke="rgb(var(--c-blood-deep))" strokeWidth="2" />
    </svg>
  );
};

/* -------------------------------------------------------------------------- */
/* Typewriter boot log                                                        */
/* -------------------------------------------------------------------------- */
export const BOOT_LOG = [
  '> mounting /dev/soul ........ ok',
  '> scanning for survivors .... 0 found',
  '> loading thanatos-22b ...... resident',
  '> telemetry ................. severed',
  '> last session closed ....... never',
  '> something is typing ....... not you',
];

export const TypeLog: React.FC<{ lines?: string[]; className?: string }> = ({ lines = BOOT_LOG, className = '' }) => {
  const [done, setDone] = useState<string[]>(reducedMotion() ? lines : []);
  const [current, setCurrent] = useState('');

  useEffect(() => {
    if (reducedMotion()) return;
    let cancelled = false;
    let t: number;
    const typeLine = (li: number, n: number) => {
      if (cancelled || li >= lines.length) return;
      const line = lines[li];
      setCurrent(line.slice(0, n));
      if (n < line.length) {
        // hesitate on the dots, like something is thinking
        const delay = line[n - 1] === '.' ? 45 + Math.random() * 95 : 18 + Math.random() * 42;
        t = window.setTimeout(() => typeLine(li, n + 1), delay);
      } else {
        t = window.setTimeout(() => { setDone(d => [...d, line]); setCurrent(''); typeLine(li + 1, 0); }, 500 + Math.random() * 900);
      }
    };
    t = window.setTimeout(() => typeLine(0, 0), 900);
    return () => { cancelled = true; window.clearTimeout(t); };
  }, [lines]);

  const all = [...done, ...(done.length < lines.length ? [current] : [])];
  return (
    <div className={`font-mono text-xs leading-7 ${className}`} aria-hidden="true">
      {all.map((l, i) => (
        <div key={i} className={i === lines.length - 1 ? 'text-blood-light' : 'text-[var(--text-muted)]'}>
          {l}{i === all.length - 1 && <span className="text-blood-light animate-[blink_1s_steps(1)_infinite]">█</span>}
        </div>
      ))}
    </div>
  );
};
