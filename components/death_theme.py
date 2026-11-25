"""
DeathAI Australia design system for the Tkinter IDE.

Mirrors ui/styles/tokens.css so the desktop IDE and the web UI share one look:
red-black void, aged-bone text, arterial red, a sickly cyan glitch fringe, and an
ochre "AUS" accent. Also hosts the "haunt" effects (text corruption, flicker,
heartbeat, whispers, blood drips, the watching eye).

Usage:
    from components import death_theme as T
    T.apply(root)                       # once, right after creating the Tk root
    tk.Label(parent, font=(T.UI, 11), bg=T.BG, fg=T.TEXT)
    T.button(parent, "Run", cmd, variant="primary")

Set DEATHAI_CALM=1 to switch off every animated effect.
"""
import math
import os
import random
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# ---------------------------------------------------------------------------
# Palette — keep in sync with ui/styles/tokens.css
# ---------------------------------------------------------------------------
VOID = '#030203'
BG = '#070405'           # editor, inputs
BG2 = '#0b0607'          # side panels
BG3 = '#110a0b'          # toolbars, headers
HOVER = '#1c1012'
ELEVATED = '#0e0809'     # dialogs
BORDER = '#2b1619'       # dried blood
BORDER2 = '#1a0d0f'

TEXT = '#d9d0c1'         # aged bone
TEXT2 = '#8c8078'
MUTED = '#544a46'

BLOOD = '#a3001b'        # arterial — primary fills
BLOOD_LIGHT = '#ff2440'  # fresh — text, glitch fringe, hover
BLOOD_DEEP = '#3a0009'   # clotted — tints, wells

SIGNAL = '#3ec7d1'       # sickly cyan — RGB-split partner, info, links
SIGNAL_LIGHT = '#8de8ee'
SIGNAL_DEEP = '#0d3a3e'

BILE = '#8fc94a'         # success / terminal — a bit too green to be healthy
BILE_LIGHT = '#b9e581'
BILE_DEEP = '#1f300f'

AMBER = '#d99a1e'        # warnings, pending
OCHRE = '#9c4a24'        # "AUS" accent — outback earth, use sparingly

SYNTAX = {
    'keyword': BLOOD_LIGHT,
    'string': '#c98a5a',
    'comment': '#5f5550',
    'function': SIGNAL_LIGHT,
    'number': AMBER,
    'class': '#d9b3a0',
    'decorator': '#b06a8a',
}

# ---------------------------------------------------------------------------
# Spacing & type
# ---------------------------------------------------------------------------
S1, S2, S3, S4, S6, S8, S12 = 4, 8, 12, 16, 24, 32, 48
BAR_H = 56        # main toolbar
HEADER_H = 40     # pane headers
STATUS_H = 30     # status bar

# Resolved in apply(); safe defaults until then.
UI = 'Segoe UI'
DISPLAY = 'Segoe UI'
MONO = 'Consolas'

CALM = os.environ.get('DEATHAI_CALM') == '1'
SCALE = 1.0

_root = None


def _enable_hidpi():
    """Render crisply on scaled Windows displays instead of bitmap-stretching.
    Must run before the first Tk window exists, so it runs at import time."""
    if os.name != 'nt':
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


_enable_hidpi()


def px(n):
    """Scale a 96-dpi pixel measurement to the current display."""
    return int(round(n * SCALE))


def _pick(families, *candidates):
    for c in candidates:
        if c in families:
            return c
    return candidates[-1]


def apply(root):
    """Resolve fonts, set Tk option defaults and style every ttk widget."""
    global UI, DISPLAY, MONO, _root, SCALE, S1, S2, S3, S4, S6, S8, S12, BAR_H, HEADER_H, STATUS_H
    _root = root
    SCALE = max(1.0, root.winfo_fpixels('1i') / 96.0)
    S1, S2, S3, S4, S6, S8, S12 = (px(v) for v in (4, 8, 12, 16, 24, 32, 48))
    BAR_H, HEADER_H, STATUS_H = px(56), px(40), px(30)
    fams = set(tkfont.families(root))
    UI = _pick(fams, 'Bahnschrift', 'Segoe UI', 'DejaVu Sans', 'Helvetica')
    DISPLAY = _pick(fams, 'Bahnschrift SemiBold Condensed', 'Bahnschrift Condensed', 'Bahnschrift', UI)
    MONO = _pick(fams, 'Cascadia Mono', 'JetBrains Mono', 'Consolas', 'DejaVu Sans Mono', 'Courier')

    root.configure(bg=BG)

    # Classic tk widgets inherit these unless they set their own colours.
    for pattern, value in {
        '*Background': BG2, '*Foreground': TEXT,
        '*activeBackground': HOVER, '*activeForeground': TEXT,
        '*selectBackground': BLOOD, '*selectForeground': TEXT,
        '*insertBackground': BLOOD_LIGHT, '*highlightBackground': BORDER2,
        '*highlightColor': BLOOD, '*troughColor': BG,
        '*Text.Background': BG, '*Entry.Background': BG,
        '*Listbox.Background': BG, '*Text.relief': 'flat', '*Entry.relief': 'flat',
        '*Button.relief': 'flat', '*Button.borderWidth': 0, '*Button.cursor': 'hand2',
        '*Menu.background': ELEVATED, '*Menu.foreground': TEXT,
        '*Menu.activeBackground': BLOOD, '*Menu.activeForeground': TEXT,
        '*Menu.relief': 'flat', '*Menu.borderWidth': 1,
        '*Font': (UI, 10),
        '*TCombobox*Listbox.background': ELEVATED, '*TCombobox*Listbox.foreground': TEXT,
        '*TCombobox*Listbox.selectBackground': BLOOD, '*TCombobox*Listbox.font': (MONO, 10),
    }.items():
        root.option_add(pattern, value)

    st = ttk.Style(root)
    st.theme_use('clam')
    st.configure('.', background=BG2, foreground=TEXT, fieldbackground=BG,
                 bordercolor=BORDER, lightcolor=BG3, darkcolor=BG3,
                 troughcolor=BG, focuscolor=BLOOD, selectbackground=BLOOD,
                 selectforeground=TEXT, insertcolor=BLOOD_LIGHT, font=(UI, 10))
    st.configure('TFrame', background=BG2)
    st.configure('Bar.TFrame', background=BG3)
    st.configure('TLabel', background=BG2, foreground=TEXT)
    st.configure('Muted.TLabel', foreground=TEXT2)
    st.configure('Hud.TLabel', foreground=MUTED, font=(MONO, 8))

    st.configure('TButton', background=BG3, foreground=TEXT, bordercolor=BORDER,
                 lightcolor=BG3, darkcolor=BG3, padding=(S4, S2), font=(MONO, 9), relief='flat')
    st.map('TButton',
           background=[('pressed', BLOOD_DEEP), ('active', HOVER)],
           foreground=[('active', BLOOD_LIGHT), ('disabled', MUTED)],
           bordercolor=[('active', BLOOD), ('focus', BLOOD)])
    st.configure('Primary.TButton', background=BLOOD, foreground=TEXT, bordercolor=BLOOD)
    st.map('Primary.TButton', background=[('active', BLOOD_LIGHT)], foreground=[('active', VOID)])

    st.configure('TEntry', fieldbackground=BG, foreground=TEXT, bordercolor=BORDER,
                 lightcolor=BORDER2, darkcolor=BORDER2, padding=S2, insertcolor=BLOOD_LIGHT)
    st.map('TEntry', bordercolor=[('focus', BLOOD)])
    st.configure('TCombobox', fieldbackground=BG, background=BG3, foreground=TEXT,
                 arrowcolor=BLOOD_LIGHT, bordercolor=BORDER, lightcolor=BORDER2,
                 darkcolor=BORDER2, padding=S1 + 2)
    st.map('TCombobox', fieldbackground=[('readonly', BG)], foreground=[('readonly', TEXT)],
           bordercolor=[('focus', BLOOD)], selectbackground=[('readonly', BG)],
           selectforeground=[('readonly', TEXT)])
    st.configure('TCheckbutton', background=BG2, foreground=TEXT2, indicatorcolor=BG,
                 indicatorbackground=BG)
    st.map('TCheckbutton', indicatorcolor=[('selected', BLOOD)], foreground=[('active', TEXT)],
           background=[('active', BG2)])
    st.configure('TRadiobutton', background=BG2, foreground=TEXT2, indicatorcolor=BG)
    st.map('TRadiobutton', indicatorcolor=[('selected', BLOOD)], background=[('active', BG2)])

    st.configure('Treeview', background=BG2, fieldbackground=BG2, foreground=TEXT2,
                 bordercolor=BG2, rowheight=px(28), font=(MONO, 9), indent=16)
    st.map('Treeview', background=[('selected', BLOOD_DEEP)], foreground=[('selected', TEXT)])
    st.configure('Treeview.Heading', background=BG3, foreground=MUTED, font=(MONO, 8), relief='flat')

    st.configure('TNotebook', background=BG3, bordercolor=BORDER2, tabmargins=(0, 0, 0, 0))
    st.configure('TNotebook.Tab', background=BG3, foreground=MUTED, bordercolor=BORDER2,
                 lightcolor=BG3, padding=(S4, S2), font=(MONO, 9))
    st.map('TNotebook.Tab', background=[('selected', BG)], foreground=[('selected', TEXT)],
           lightcolor=[('selected', BLOOD)])

    st.configure('TPanedwindow', background=BORDER2)
    st.configure('Sash', sashthickness=px(6), gripcount=0, background=BORDER2)
    st.configure('Vertical.TScrollbar', background=BG3, troughcolor=BG, bordercolor=BG,
                 arrowcolor=MUTED, lightcolor=BG3, darkcolor=BG3, gripcount=0, arrowsize=10)
    st.configure('Horizontal.TScrollbar', background=BG3, troughcolor=BG, bordercolor=BG,
                 arrowcolor=MUTED, lightcolor=BG3, darkcolor=BG3, gripcount=0, arrowsize=10)
    st.map('Vertical.TScrollbar', background=[('active', BLOOD)])
    st.map('Horizontal.TScrollbar', background=[('active', BLOOD)])
    st.configure('TProgressbar', background=BLOOD, troughcolor=BG, bordercolor=BORDER2,
                 lightcolor=BLOOD_LIGHT, darkcolor=BLOOD_DEEP)
    st.configure('TSeparator', background=BORDER)
    st.configure('TLabelframe', background=BG2, bordercolor=BORDER)
    st.configure('TLabelframe.Label', background=BG2, foreground=MUTED, font=(MONO, 8))
    return st


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------
_VARIANTS = {
    #           bg      fg          hover bg     hover fg
    'ghost':   (BG3,   TEXT2,      HOVER,       TEXT),
    'primary': (BLOOD, TEXT,       BLOOD_LIGHT, VOID),
    'danger':  (BG3,   BLOOD_LIGHT, BLOOD_DEEP, TEXT),
    'success': (BG3,   BILE,       BILE_DEEP,   BILE_LIGHT),
}


def button(parent, text, command=None, variant='ghost', size='md', **kw):
    """Flat button with a 1px border, hover colour shift and a brief glitch on hover."""
    bg, fg, hbg, hfg = _VARIANTS[variant]
    pad = {'sm': (S3, S1 + 2), 'md': (S4, S2), 'lg': (S6, S3)}[size]
    wrap = tk.Frame(parent, bg=BLOOD if variant == 'primary' else BORDER, padx=1, pady=1)
    b = tk.Label(wrap, text=text.upper(), bg=bg, fg=fg, font=(MONO, 9 if size != 'lg' else 10, 'bold'),
                 padx=pad[0], pady=pad[1], cursor='hand2', **kw)
    b.pack(fill=tk.BOTH, expand=True)
    label = text.upper()

    def enter(_):
        b.config(bg=hbg, fg=hfg)
        wrap.config(bg=BLOOD_LIGHT if variant != 'success' else BILE)
        if not CALM:
            b.config(text=corrupt(label, 0.35))
            b.after(90, lambda: b.config(text=label))

    def leave(_):
        b.config(bg=bg, fg=fg, text=label)
        wrap.config(bg=BLOOD if variant == 'primary' else BORDER)

    b.bind('<Enter>', enter)
    b.bind('<Leave>', leave)
    if command:
        b.bind('<Button-1>', lambda e: command())
    wrap.label = b
    return wrap


def pane_header(parent, title, right=None, bg=BG3):
    """40px header strip: red '//' + tracked caps title, optional right-hand text."""
    h = tk.Frame(parent, bg=bg, height=HEADER_H)
    h.pack(fill=tk.X)
    h.pack_propagate(False)
    tk.Label(h, text='//', bg=bg, fg=BLOOD_LIGHT, font=(MONO, 9, 'bold')).pack(side=tk.LEFT, padx=(S4, S1))
    tk.Label(h, text=spaced(title), bg=bg, fg=TEXT2, font=(MONO, 8, 'bold')).pack(side=tk.LEFT)
    if right is not None:
        lbl = tk.Label(h, text=right, bg=bg, fg=MUTED, font=(MONO, 8))
        lbl.pack(side=tk.RIGHT, padx=S4)
        h.right = lbl
    tk.Frame(parent, bg=BORDER2, height=1).pack(fill=tk.X)
    return h


def hud(parent, text, fg=MUTED, bg=BG3, **kw):
    return tk.Label(parent, text=spaced(text), bg=bg, fg=fg, font=(MONO, 8), **kw)


def spaced(text):
    """Fake letter-spacing for HUD labels (Tk has no tracking)."""
    return ' '.join(text.upper())


def style_text(widget, mono=True, size=10):
    """Apply editor-grade styling to a tk.Text / ScrolledText."""
    widget.config(bg=BG, fg=TEXT, insertbackground=BLOOD_LIGHT, insertwidth=2,
                  selectbackground=BLOOD, selectforeground=TEXT, relief=tk.FLAT, bd=0,
                  highlightthickness=0, padx=S4, pady=S3, spacing1=2, spacing3=2,
                  font=(MONO if mono else UI, size))
    # ScrolledText ships a native tk.Scrollbar that Windows renders white — swap in ttk.
    vbar = getattr(widget, 'vbar', None)
    if isinstance(vbar, tk.Scrollbar):
        vbar.pack_forget()
        new = ttk.Scrollbar(vbar.master, orient=tk.VERTICAL, command=widget.yview)
        new.pack(side=tk.RIGHT, fill=tk.Y)
        widget.config(yscrollcommand=new.set)
        widget.vbar = new


# ---------------------------------------------------------------------------
# Haunt effects
# ---------------------------------------------------------------------------
_ZALGO = [chr(c) for c in range(0x0300, 0x036F)]
_SWAP = {'A': 'Λ', 'E': 'Ξ', 'O': 'Ø', 'I': '|', 'T': '†', 'H': '#', 'S': '$', 'D': 'Ð',
         'a': 'α', 'e': 'є', 'o': 'ø', 'i': 'ι', 't': '†', 's': '§'}
_BLOCKS = '▓▒░█▚▞'


def corrupt(text, intensity=0.25):
    out = []
    for ch in text:
        r = random.random()
        if ch.strip() and r < intensity * 0.35:
            out.append(random.choice(_BLOCKS))
        elif ch in _SWAP and r < intensity * 0.8:
            out.append(_SWAP[ch])
        else:
            out.append(ch)
        if ch.strip() and random.random() < intensity * 0.5:
            out.append(random.choice(_ZALGO))
    return ''.join(out)


class Haunt:
    """Low-frequency creepy behaviours bound to a Tk root. All no-ops when CALM."""

    WHISPERS = [
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
    ]

    def __init__(self, root):
        self.root = root

    # -- Text corruption --------------------------------------------------
    def glitch_label(self, label, base_text=None, every=(2500, 7000), intensity=0.4):
        if CALM:
            return
        base = base_text or label.cget('text')

        def tick():
            if not label.winfo_exists():
                return
            frames = random.randint(2, 4)

            def burst(n):
                if not label.winfo_exists():
                    return
                if n:
                    label.config(text=corrupt(base, intensity))
                    label.after(55, burst, n - 1)
                else:
                    label.config(text=base)
            burst(frames)
            label.after(random.randint(*every), tick)
        label.after(random.randint(*every), tick)

    # -- Failing fluorescent ---------------------------------------------
    def flicker(self, widget, on, off, attr='fg', every=(3000, 9000)):
        if CALM:
            return

        def tick():
            if not widget.winfo_exists():
                return
            seq = [off, on, off, off, on] if random.random() < 0.4 else [off, on]

            def step(i):
                if i < len(seq) and widget.winfo_exists():
                    widget.config(**{attr: seq[i]})
                    widget.after(random.randint(30, 90), step, i + 1)
            step(0)
            widget.after(random.randint(*every), tick)
        widget.after(random.randint(*every), tick)

    # -- Heartbeat line ---------------------------------------------------
    def heartbeat(self, parent, height=2):
        """A thin line under the toolbar that pulses lub-dub, about 52 bpm."""
        c = tk.Canvas(parent, height=height, bg=BLOOD_DEEP, highlightthickness=0, bd=0)
        c.pack(fill=tk.X)
        if CALM:
            return c
        pattern = [(BLOOD_LIGHT, 70), (BLOOD, 90), (BLOOD_LIGHT, 60), (BLOOD_DEEP, 930)]

        def beat(i=0):
            if not c.winfo_exists():
                return
            color, ms = pattern[i % len(pattern)]
            c.config(bg=color)
            c.after(ms, beat, i + 1)
        beat()
        return c

    # -- Status bar whispers --------------------------------------------
    def whispers(self, label, every=(45000, 120000), hold=2600):
        """Occasionally replace a status label's text with a whisper, then restore it."""
        if CALM:
            return

        def tick():
            if not label.winfo_exists():
                return
            original, fg = label.cget('text'), label.cget('fg')
            msg = random.choice(self.WHISPERS)
            label.config(text=corrupt(msg, 0.15), fg=BLOOD_LIGHT)
            label.after(160, lambda: label.winfo_exists() and label.config(text=msg))

            def restore():
                if label.winfo_exists() and label.cget('text') == msg:
                    label.config(text=original, fg=fg)
            label.after(hold, restore)
            label.after(random.randint(*every), tick)
        label.after(random.randint(*every), tick)

    # -- Window title ------------------------------------------------------
    def title(self, base, every=(20000, 60000)):
        self.root.title(base)
        if CALM:
            return

        def tick():
            try:
                self.root.title(corrupt(base, 0.5))
                self.root.after(180, lambda: self.root.title(base))
                self.root.after(random.randint(*every), tick)
            except tk.TclError:
                pass
        self.root.after(random.randint(*every), tick)


# ---------------------------------------------------------------------------
# Canvas scenes
# ---------------------------------------------------------------------------
class BloodDrips:
    """Blood that slowly seeps down from the top edge of a canvas."""

    def __init__(self, canvas, count=14):
        self.c = canvas
        self.drips = []
        self.count = count
        if not CALM:
            canvas.after(300, self._spawn_all)

    def _spawn_all(self):
        w = max(self.c.winfo_width(), 200)
        # ragged pool along the top
        pts = [0, 0]
        x = 0
        while x < w:
            pts += [x, random.randint(2, 9)]
            x += random.randint(14, 40)
        pts += [w, 4, w, 0]
        self.c.create_polygon(pts, fill=BLOOD_DEEP, outline='', tags='blood')
        for _ in range(self.count):
            self._spawn(w)
        self._tick()

    def _spawn(self, w):
        x = random.randint(8, w - 8)
        width = random.choice([2, 3, 3, 4, 5])
        d = {
            'x': x, 'len': random.randint(4, 12), 'max': random.randint(30, 220),
            'speed': random.uniform(0.15, 0.9), 'w': width,
            'line': self.c.create_line(x, 0, x, 6, fill=BLOOD, width=width, capstyle=tk.ROUND, tags='blood'),
            'bead': self.c.create_oval(x - width, 6 - width, x + width, 6 + width, fill=BLOOD, outline='', tags='blood'),
        }
        self.drips.append(d)

    def _tick(self):
        if not self.c.winfo_exists():
            return
        for d in self.drips:
            if d['len'] < d['max']:
                # hesitate, then lurch — blood doesn't run at constant speed
                d['len'] += d['speed'] * (3 if random.random() < 0.04 else 1)
            x, y, w = d['x'], d['len'], d['w']
            self.c.coords(d['line'], x, 0, x, y)
            r = w * 0.9 + 1
            self.c.coords(d['bead'], x - r, y - r, x + r, y + r * 1.3)
        self.c.tag_raise('fg')
        self.c.after(40, self._tick)


class WatchingEye:
    """An eye that follows the mouse and blinks at irregular intervals."""

    def __init__(self, canvas, cx, cy, r=34):
        self.c, self.cx, self.cy, self.r = canvas, cx, cy, r
        self.white = canvas.create_oval(cx - r, cy - r * 0.55, cx + r, cy + r * 0.55,
                                        fill='#cbbfae', outline=BLOOD_DEEP, width=2, tags='fg')
        for _ in range(5):  # bloodshot veins
            a = random.uniform(0, math.tau)
            x1, y1 = cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.5
            x2, y2 = cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.25
            canvas.create_line(x1, y1, (x1 + x2) / 2 + random.uniform(-4, 4), (y1 + y2) / 2, x2, y2,
                               fill=BLOOD, width=1, smooth=True, tags=('fg', 'vein'))
        self.iris = canvas.create_oval(0, 0, 0, 0, fill=BLOOD, outline=BLOOD_DEEP, width=2, tags='fg')
        self.pupil = canvas.create_oval(0, 0, 0, 0, fill=VOID, outline='', tags='fg')
        self.lid = canvas.create_rectangle(cx - r - 2, cy - r, cx + r + 2, cy - r, fill=canvas.cget('bg'),
                                           outline='', tags='fg', state='hidden')
        self._look(cx, cy)
        canvas.bind('<Motion>', lambda e: self._look(e.x, e.y), add='+')
        if not CALM:
            canvas.after(random.randint(2000, 5000), self._blink)

    def _look(self, mx, my):
        dx, dy = mx - self.cx, my - self.cy
        dist = math.hypot(dx, dy) or 1
        k = min(1, dist / 300)
        ox = dx / dist * self.r * 0.45 * k
        oy = dy / dist * self.r * 0.2 * k
        ir, pr = self.r * 0.42, self.r * 0.18
        x, y = self.cx + ox, self.cy + oy
        self.c.coords(self.iris, x - ir, y - ir, x + ir, y + ir)
        self.c.coords(self.pupil, x - pr, y - pr * 1.6, x + pr, y + pr * 1.6)  # slit-ish pupil

    def _blink(self):
        if not self.c.winfo_exists():
            return
        cx, cy, r = self.cx, self.cy, self.r
        steps = [0.3, 0.65, 1.0, 0.65, 0.3, 0.0]

        def step(i):
            if not self.c.winfo_exists():
                return
            if i < len(steps):
                h = steps[i] * r * 1.2
                self.c.itemconfig(self.lid, state='normal')
                self.c.coords(self.lid, cx - r - 2, cy - r, cx + r + 2, cy - r * 0.55 + h)
                self.c.after(35, step, i + 1)
            else:
                self.c.itemconfig(self.lid, state='hidden')
        step(0)
        self.c.after(random.randint(2500, 9000), self._blink)


class TypeLog:
    """A slow typewriter log on a canvas. Lines appear one character at a time."""

    LINES = [
        '> mounting /dev/soul ........ ok',
        '> scanning for survivors .... 0 found',
        '> loading thanatos-22b ...... resident',
        '> telemetry ................. severed',
        '> last session closed ....... never',
        '> something is typing ....... not you',
    ]

    def __init__(self, canvas, x, y, line_gap, lines=None, color=None):
        self.c, self.x, self.y, self.gap = canvas, x, y, line_gap
        self.lines = lines or self.LINES
        self.color = color or MUTED
        self.items = []
        if CALM:
            for i, line in enumerate(self.lines):
                canvas.create_text(x, y + i * line_gap, anchor='nw', text=line, fill=self.color,
                                   font=(MONO, 9), tags='fg')
            return
        self.caret = canvas.create_text(x, y, anchor='nw', text='█', fill=BLOOD_LIGHT,
                                        font=(MONO, 9), tags='fg')
        canvas.after(900, self._line, 0)
        self._blink()

    def _blink(self):
        if not self.c.winfo_exists():
            return
        state = self.c.itemcget(self.caret, 'state')
        self.c.itemconfig(self.caret, state='hidden' if state != 'hidden' else 'normal')
        self.c.after(530, self._blink)

    def _line(self, i):
        if i >= len(self.lines) or not self.c.winfo_exists():
            return
        line = self.lines[i]
        last = i == len(self.lines) - 1
        item = self.c.create_text(self.x, self.y + i * self.gap, anchor='nw', text='',
                                  fill=BLOOD_LIGHT if last else self.color, font=(MONO, 9), tags='fg')

        def type_char(n):
            if not self.c.winfo_exists():
                return
            self.c.itemconfig(item, text=line[:n])
            bbox = self.c.bbox(item)
            self.c.coords(self.caret, bbox[2] + 2 if bbox and n else self.x, self.y + i * self.gap)
            if n < len(line):
                # hesitate on the dots, like something is thinking
                delay = random.randint(45, 140) if line[n - 1:n] == '.' else random.randint(18, 60)
                self.c.after(delay, type_char, n + 1)
            else:
                self.c.after(random.randint(500, 1400), self._line, i + 1)
        type_char(0)


def scanlines(canvas, step=3):
    """Static horizontal scanlines over a canvas (drawn once, kept on top)."""
    w, h = canvas.winfo_width(), canvas.winfo_height()
    for y in range(0, h, step):
        canvas.create_line(0, y, w, y, fill=VOID, stipple='gray25', tags='scan')
    canvas.tag_raise('scan')


def glitch_text(canvas, x, y, text, size=40, anchor='nw', tag='title'):
    """Draw text three times (cyan, red, bone) and jitter the colour layers."""
    f = (DISPLAY, size, 'bold')
    a = canvas.create_text(x - 2, y, text=text, fill=SIGNAL, font=f, anchor=anchor, tags=('fg', tag))
    b = canvas.create_text(x + 2, y, text=text, fill=BLOOD_LIGHT, font=f, anchor=anchor, tags=('fg', tag))
    m = canvas.create_text(x, y, text=text, fill=TEXT, font=f, anchor=anchor, tags=('fg', tag))
    if CALM:
        return m

    def tick():
        if not canvas.winfo_exists():
            return
        if random.random() < 0.18:
            canvas.coords(a, x - random.randint(3, 9), y + random.randint(-2, 2))
            canvas.coords(b, x + random.randint(3, 9), y + random.randint(-2, 2))
            canvas.itemconfig(m, text=corrupt(text, 0.3))
        else:
            canvas.coords(a, x - 2, y)
            canvas.coords(b, x + 2, y)
            canvas.itemconfig(m, text=text)
        canvas.after(random.choice([60, 90, 140, 400]), tick)
    tick()
    return m


def southern_cross(canvas, x, y, scale=1.0, color=OCHRE):
    """Crux as on the Australian flag. Quiet signature, bottom corner only."""
    stars = [(0, 38, 5), (0, -38, 4.4), (-30, -8, 4.4), (28, -14, 4), (14, 8, 2.4)]
    for sx, sy, r in stars:
        cx, cy, r = x + sx * scale, y + sy * scale, r * scale
        pts = []
        for i in range(14):
            ang = -math.pi / 2 + i * math.pi / 7
            rad = r * 2 if i % 2 == 0 else r * 0.8
            pts += [cx + math.cos(ang) * rad, cy + math.sin(ang) * rad]
        canvas.create_polygon(pts, fill=color, outline='', tags='fg')
