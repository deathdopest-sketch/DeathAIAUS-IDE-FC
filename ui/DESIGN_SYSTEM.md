# DeathAI Australia — UI Design System

Haunted-terminal aesthetic for the DeathAIAUS IDE: red-black void, aged-bone text, arterial red,
a sickly cyan glitch fringe, CRT scanlines and a closing vignette. Things move when you're not
looking. Australian signature via an ochre accent and the Southern Cross.

**One system, two UIs.** The web UI reads `ui/styles/tokens.css`; the Tkinter IDE reads
`components/death_theme.py`. They carry the same values — change both together.

## What was there before (extracted)

| Area | Before | Problem |
|---|---|---|
| Colour | ~30 CSS vars × 4 themes in `index.html` | Components ignored them and hardcoded `indigo/blue/purple/cyan/lime/gray-600`, so 6+ competing accents. `--accent-warning-text: #yellow-300` was invalid. |
| Theme switch | `App.tsx` set `className` | CSS keyed on `data-theme`, so switching themes did nothing. |
| Tailwind | `content` missed `components/**` | Most arbitrary classes were never generated (6 KB CSS). |
| Type | System sans + Courier New | No hierarchy, no brand voice. |
| Shape/space | `rounded-md/lg`, ad hoc padding | No scale. |

## Files

- `styles/tokens.css` — all tokens and themes (`deathai` default, plus `dark`, `light`, `gothic`, `cyberpunk`)
- `index.css` — base, `dx-*` component classes, glitch effects, keyframes
- `tailwind.config.js` — brand hues and the legacy Tailwind hues remapped to tokens
- `components/ui/GlitchText.tsx`, `components/ui/SouthernCross.tsx`, `components/icons/SkullIcon.tsx`

## Tokens

### Colour — raw channels (`--c-<hue>-<tier>`, tiers `light | base | deep`)

| Hue | Light / Base / Deep | Role | Tk name |
|---|---|---|---|
| `blood` | `#ff2440` / `#a3001b` / `#3a0009` | Primary fills (base), text and hover (light), wells (deep) | `BLOOD_LIGHT`, `BLOOD`, `BLOOD_DEEP` |
| `signal` | `#8de8ee` / `#3ec7d1` / `#0d3a3e` | Sickly cyan: info, links, RGB-split partner | `SIGNAL*` |
| `phosphor` | `#b9e581` / `#8fc94a` / `#1f300f` | "Bile": success, terminal output | `BILE*` |
| `amber` | — / `#d99a1e` / — | Warnings, pending | `AMBER` |
| `ochre` | — / `#9c4a24` / — | **AUS accent**, sparingly | `OCHRE` |
| `void` / `bone` | `#030203` / `#d9d0c1` | Background / aged-bone text | `VOID` / `TEXT` |

Surfaces are red-tinted blacks, never neutral grey: `#070405 → #0b0607 → #110a0b → #1c1012`.
Borders are dried blood: `#2b1619`, `#1a0d0f`.

**Contrast rule:** text uses `blood-light`, never `blood` (base red on black is ~2.5:1).

In Tailwind: `bg-blood`, `text-signal-light`, `border-blood/50`, `bg-blood-deep/40`.
Legacy hues map automatically (`indigo/purple/red → blood`, `blue/cyan → signal`,
`green/lime → phosphor`, `yellow → amber`, `gray → ash`), so older components stay on-brand.

### Semantic

`--bg-primary | secondary | tertiary | hover | elevated`, `--text-primary | secondary | muted`,
`--border-primary | secondary`, `--accent-*`, `--terminal-bg | text`. Components should use these
and not raw hex values.

### Type

| Token | Font | Use |
|---|---|---|
| `--font-ui` / `font-display` | Chakra Petch 400–700 | UI text, headings (UPPERCASE, `tracking-wide`) |
| `--font-code` / `font-mono` | JetBrains Mono 400/600 | Code, labels, buttons, terminal |

Scale: 10px HUD label · 11–12px buttons/tree · 13px code · 14px body · 18–24px dialog titles · 30–36px hero.
Fonts ship via `@fontsource` (offline-safe for pywebview).

### Shape & spacing

- Spacing scale: 4, 8, 12, 16, 24, 32, 40, 48px (`--space-*` / `T.S1…T.S12`, DPI-scaled in Tk).
- Fixed heights: toolbar 56, pane header 40, status bar 30 (`--bar-h`, `--header-h`, `--status-h` / `T.BAR_H`…).
- Default pane split 18 / 52 / 30 with 6px gutters. Pane content gets 20–24px side padding; chat messages 28px apart.
- Radius ≈ 0–3px. Corners are **cut** (clip-path) rather than rounded: `--cut: 10px` on panels, 8px on buttons, 18px on dialogs.
- Gutters glow blood-red on drag.

## Components (`dx-` prefix)

| Class | Purpose |
|---|---|
| `dx-btn` | Ghost button, mono uppercase, cut corners; hover = red edge + RGB-split jitter |
| `dx-btn-primary` / `-success` / `-danger` | Variants |
| `dx-btn-icon`, `dx-btn-lg` | Sizes |
| `dx-input` | Field with blood left-edge, cyan focus glow |
| `dx-label` | 10px tracked uppercase HUD label |
| `dx-tag` | Bracketed outline tag, e.g. `[AUS]` |
| `dx-pane-header` | 32px strip at the top of every pane; first label gets a red `//` |
| `dx-panel` | Tertiary surface with a cut corner |
| `dx-backdrop` + `dx-dialog` | Modal; dialog enters with a glitch-in animation |
| `dx-dot` | Pulsing status dot (uses `currentColor`) |
| `dx-caret` | Blinking red block cursor |

## Glitch effects (use with restraint)

| Effect | How | Where |
|---|---|---|
| Slice glitch | `<GlitchText text="…" />` or `.glitch[data-text]` | Hero wordmark (always), toolbar logo (`mode="hover"`) |
| Tear | `.dx-tear` — horizontal tear about every 7s | Logo, loader only |
| RGB split | `.dx-split`, button hover | Emphasis words |
| Scanlines + grain | `body::before/::after`, set via `--scanline-opacity`, `--noise-opacity` | Global |
| Glitch-in | `.dx-dialog`, `animate-fade-in-right` (toasts) | Entrances |

### Haunt effects (`components/ui/haunt.tsx` · `death_theme.Haunt` and friends)

| Effect | Web | Tk | Where |
|---|---|---|---|
| Blood drips seeping from an edge | `<BloodDrips/>` | `BloodDrips(canvas)` | Welcome screen; short drips under the toolbar (web) |
| Eye that follows the cursor and blinks | `<WatchingEye/>` | `WatchingEye(canvas, …)` | Welcome screen only |
| Typewriter boot log ("scanning for survivors … 0 found") | `<TypeLog/>` | `TypeLog(canvas, …)` | Welcome screen |
| Text corruption bursts (zalgo, block glyphs) | `<CorruptText/>`, `corrupt()` | `Haunt.glitch_label`, `corrupt()` | Logo, one headline |
| Status-bar whispers, ~every 45–120s | `useWhisper()` | `Haunt.whispers(label)` | Status bar |
| Heartbeat line (~52bpm) | `.dx-heartbeat` | `Haunt.heartbeat(parent)` | Under the toolbar |
| Fluorescent flicker | `.dx-flicker` | `Haunt.flicker(widget, …)` | Status chips |
| Window-title corruption | — | `Haunt.title(base)` | Tk window title |
| Vignette + slow "breathing" | `body::before` | — | Global |

Switch it all off: `prefers-reduced-motion` (web) or `DEATHAI_CALM=1` (Tk).

**Rules:** at most one *always-on* glitch per screen. Haunting goes in chrome (logo, status bar,
welcome screen), never inside the editor, chat content or error messages. Never glitch body copy or code.
All motion is disabled under `prefers-reduced-motion`.

## Tkinter specifics

- Call `T.apply(root)` right after creating a Tk root. It resolves fonts (Bahnschrift / Cascadia Mono
  on Windows), styles every ttk widget on the `clam` theme, sets `option_add` defaults for classic tk
  widgets, and scales spacing to the display DPI. Importing the module makes the process DPI-aware,
  so text is crisp instead of bitmap-stretched.
- Build with `T.button(parent, text, cmd, variant='ghost'|'primary'|'danger'|'success', size='sm'|'md'|'lg')`,
  `T.pane_header(parent, title)`, `T.hud(parent, text)` and `T.style_text(text_widget)`.
- `scripts/apply_death_palette.py` migrated ~1,700 hardcoded colours and fonts across `components/`
  to tokens. Re-run it after adding old-style code; it's idempotent.

## Voice

Terse, dry, morbid, never cute. Funeral vocabulary for actions ("Choose your grave",
"Exhume existing project", "Raise it", "Recently buried"). Status labels shout in mono caps (`REAPGATE // ONLINE`,
`[ERR]`). Empty states lean into the theme ("Select a file to raise it from the dead",
"Speak, mortal."), but error text stays plain and useful.
