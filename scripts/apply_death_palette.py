"""
One-shot migration: rewrite hardcoded colours and fonts in the Tkinter IDE onto the
DeathAI design system (components/death_theme.py).

- Known hex values map to named tokens (T.BG, T.BLOOD, ...).
- Unknown hex values are classified by lightness/hue and mapped to the nearest role.
- 'Arial' / 'Segoe UI' font families -> T.UI, 'Consolas' / 'Courier' -> T.MONO.
- Adds `from components import death_theme as T` where needed.

Usage:  python scripts/apply_death_palette.py [--dry-run]
"""
import colorsys
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [ROOT / 'deathaius_ide_fc.py'] + sorted((ROOT / 'components').glob('*.py'))
SKIP = {'themes.py', 'death_theme.py', '__init__.py', 'simple_theme_selector.py'}

EXACT = {
    '#1e1e1e': 'BG', '#252525': 'BG2', '#252526': 'BG2', '#2d2d2d': 'BG3', '#2b2b2b': 'BG2',
    '#3d3d3d': 'HOVER', '#3c3c3c': 'HOVER', '#333333': 'BORDER2', '#444444': 'BORDER',
    '#0d0d0d': 'VOID', '#1a1a1a': 'VOID', '#000000': 'VOID', '#0c0c0c': 'VOID',
    '#ffffff': 'TEXT', '#d4d4d4': 'TEXT', '#cccccc': 'TEXT', '#e0e0e0': 'TEXT',
    '#888888': 'TEXT2', '#858585': 'TEXT2', '#999999': 'TEXT2', '#aaaaaa': 'TEXT2',
    '#666666': 'MUTED', '#555555': 'MUTED',
    '#00ff00': 'BILE', '#69ff69': 'BILE_LIGHT', '#00aa00': 'BLOOD', '#4caf50': 'BILE',
    '#1f4a1f': 'BILE_DEEP', '#4a1f1f': 'BLOOD_DEEP',
    '#0066cc': 'HOVER', '#264f78': 'BLOOD', '#6366f1': 'BLOOD', '#9900ff': 'HOVER',
    '#00aaff': 'SIGNAL', '#6495ed': 'SIGNAL',
    '#ff0000': 'BLOOD_LIGHT', '#cc0000': 'BLOOD', '#ff6666': 'BLOOD_LIGHT', '#ff6b6b': 'BLOOD_LIGHT',
    '#f44336': 'BLOOD_LIGHT',
    '#ff9900': 'AMBER', '#ff9800': 'AMBER', '#ffaa00': 'AMBER',
    # VS Code syntax colours -> creepy syntax
    '#569cd6': "SYNTAX['keyword']", '#ce9178': "SYNTAX['string']", '#6a9955': "SYNTAX['comment']",
    '#dcdcaa': "SYNTAX['function']", '#b5cea8': "SYNTAX['number']", '#4ec9b0': "SYNTAX['class']",
    '#c586c0': "SYNTAX['decorator']",
}
NAMED = {'white': 'TEXT', 'black': 'VOID', 'red': 'BLOOD_LIGHT', 'green': 'BILE',
         'gray': 'TEXT2', 'grey': 'TEXT2', 'yellow': 'AMBER', 'orange': 'AMBER', 'blue': 'SIGNAL'}
COLOR_KW = r'(?:bg|fg|background|foreground|insertbackground|selectbackground|selectforeground|' \
           r'activebackground|activeforeground|selectcolor|highlightbackground|highlightcolor|' \
           r'fill|outline|troughcolor|disabledforeground)'


def classify(hexv):
    """Map an arbitrary colour to a token by lightness and hue."""
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < 0.18:  # greys
        if l < 0.08: return 'VOID'
        if l < 0.14: return 'BG'
        if l < 0.19: return 'BG3'
        if l < 0.30: return 'HOVER'
        if l < 0.45: return 'MUTED'
        if l < 0.65: return 'TEXT2'
        return 'TEXT'
    deg = h * 360
    deep = l < 0.3
    if deg < 20 or deg >= 330: return 'BLOOD_DEEP' if deep else ('BLOOD_LIGHT' if l > 0.55 else 'BLOOD')
    if deg < 60: return 'AMBER' if not deep else 'BLOOD_DEEP'
    if deg < 160: return 'BILE_DEEP' if deep else ('BILE_LIGHT' if l > 0.6 else 'BILE')
    if deg < 260: return 'SIGNAL_DEEP' if deep else ('SIGNAL_LIGHT' if l > 0.6 else 'SIGNAL')
    return 'BLOOD_DEEP' if deep else 'BLOOD'  # purples/magentas -> blood


def token_for(value):
    v = value.lower()
    if v.startswith('#') and len(v) == 7:
        return EXACT.get(v) or classify(v)
    if v.startswith('#') and len(v) == 4:
        return token_for('#' + ''.join(c * 2 for c in v[1:]))
    return NAMED.get(v)


def migrate(src):
    n = 0

    def sub_hex(m):
        nonlocal n
        tok = token_for(m.group(2))
        if not tok:
            return m.group(0)
        n += 1
        return f'T.{tok}'

    # Any quoted hex literal anywhere (dict values, tag_configure, etc.)
    src = re.sub(r'''(['"])(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})\1''', sub_hex, src)

    # Named colours only when used as a colour keyword argument
    def sub_named(m):
        nonlocal n
        tok = NAMED.get(m.group(3).lower())
        if not tok:
            return m.group(0)
        n += 1
        return f'{m.group(1)}=T.{tok}'
    src = re.sub(rf'''\b({COLOR_KW})\s*=\s*(['"])(white|black|red|green|gr[ae]y|yellow|orange|blue)\2''', sub_named, src)

    # Font families inside tuples
    src, k1 = re.subn(r'''\(\s*['"](?:Arial|Segoe UI|Helvetica)['"]\s*,''', '(T.UI,', src)
    src, k2 = re.subn(r'''\(\s*['"](?:Consolas|Courier New|Courier)['"]\s*,''', '(T.MONO,', src)
    n += k1 + k2

    if n and 'death_theme as T' not in src:
        # insert after the last top-level import in the header block
        lines = src.split('\n')
        idx = 0
        for i, line in enumerate(lines[:120]):
            if line.startswith(('import ', 'from ')):
                idx = i
        lines.insert(idx + 1, 'from components import death_theme as T')
        src = '\n'.join(lines)
    return src, n


def main():
    dry = '--dry-run' in sys.argv
    total = 0
    for p in TARGETS:
        if p.name in SKIP:
            continue
        src = p.read_text(encoding='utf-8')
        new, n = migrate(src)
        if n:
            total += n
            print(f'{n:4d}  {p.relative_to(ROOT)}')
            if not dry:
                p.write_text(new, encoding='utf-8', newline='\n')
    print(f'{total} replacements{" (dry run)" if dry else ""}')


if __name__ == '__main__':
    main()
