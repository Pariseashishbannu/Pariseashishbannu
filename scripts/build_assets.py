#!/usr/bin/env python3
"""Generate the profile README's terminal-style SVG artwork.

Run from the repo root:  python3 scripts/build_assets.py
Needs:  pip install fonttools brotli uharfbuzz
Edit PROJECTS / STACK below, re-run, commit the regenerated assets/.

Text is converted to outlines (IBM Plex Mono and Anek Telugu, scripts/fonts,
SIL OFL) because GitHub cannot load web fonts inside a README image.
"""
import io
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"

BG, BAR, LINE = "#0A0F0C", "#121B16", "#23402F"
TEXT, DIM, GREEN, SHADOW, RED = "#DDF7E5", "#7FB596", "#3DFF8B", "#2FA866", "#FF4D5E"
PROMPT = "bannu@vega:~$ "


class Face:
    def __init__(self, name):
        font = TTFont(ROOT / "fonts" / name)
        font.flavor = None
        buf = io.BytesIO()
        font.save(buf)
        self.glyphs = font.getGlyphSet()
        self.order = font.getGlyphOrder()
        self.upem = font["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(buf.getvalue()))

    def shape(self, s):
        b = hb.Buffer()
        b.add_str(s)
        b.guess_segment_properties()
        hb.shape(self.hb, b)
        if any(i.codepoint == 0 for i in b.glyph_infos):
            raise ValueError(f"missing glyph in {s!r}")
        return b.glyph_infos, b.glyph_positions


FACES = {
    400: Face("ibm-plex-mono-latin-400-normal.woff2"),
    600: Face("ibm-plex-mono-latin-600-normal.woff2"),
    700: Face("ibm-plex-mono-latin-700-normal.woff2"),
    "te": Face("anek-telugu-telugu-500-normal.woff2"),
}


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def measure(s, size, weight=400):
    f = FACES[weight]
    return sum(p.x_advance for p in f.shape(s)[1]) * size / f.upem


def text(s, x, y, size, fill, weight=400, anchor="start", limit=None):
    width = measure(s, size, weight)
    if limit and width > limit:
        raise ValueError(f"{s!r} is {width:.0f}px wide, limit {limit}")
    f = FACES[weight]
    k = size / f.upem
    pen_x = x - width if anchor == "end" else x
    pen = SVGPathPen(f.glyphs, ntos=num)
    infos, positions = f.shape(s)
    for info, pos in zip(infos, positions):
        tf = (k, 0, 0, -k, pen_x + pos.x_offset * k, y - pos.y_offset * k)
        f.glyphs[f.order[info.codepoint]].draw(TransformPen(pen, tf))
        pen_x += pos.x_advance * k
    return f'<path d="{pen.getCommands()}" fill="{fill}"/>'


def show(body, delay):
    return f'<g class="s" style="animation-delay:{delay:.2f}s">{body}</g>'


def typed(s, x, y, size, fill, start, step=0.07):
    """One group per character, so the command appears to be typed."""
    adv = size * 0.6
    return "".join(show(text(c, x + i * adv, y, size, fill), start + i * step)
                   for i, c in enumerate(s) if c != " ")


def svg(w, h, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label, {'"': '&quot;'})}">
<style>
@keyframes on{{to{{opacity:1}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.s{{opacity:0;animation:on 0s linear forwards}}
.trace{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.6s cubic-bezier(.55,0,.25,1) 1s forwards}}
.cur{{animation:blink 1.1s steps(1) infinite}}
@media (prefers-reduced-motion:reduce){{.s{{animation:none;opacity:1}}.trace{{animation:none;stroke-dashoffset:0}}.cur{{animation:none}}}}
</style>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="6" fill="{BG}" stroke="{LINE}"/>
{body}
</svg>
"""


def titlebar(w, left, right=None, right_fill=DIM):
    b = [f'<path d="M1,44 V7 a6,6 0 0 1 6,-6 H{w - 7} a6,6 0 0 1 6,6 V44Z" fill="{BAR}"/>',
         f'<line x1="1" y1="44.5" x2="{w - 1}" y2="44.5" stroke="{LINE}"/>',
         text(left, 28, 29, 18, DIM)]
    if right:
        b.append(text(right, w - 28, 29, 18, right_fill, anchor="end"))
    return b


# ---------------------------------------------------------------- hero

BANNER = """\
██████╗  █████╗ ███╗   ██╗███╗   ██╗██╗   ██╗
██╔══██╗██╔══██╗████╗  ██║████╗  ██║██║   ██║
██████╔╝███████║██╔██╗ ██║██╔██╗ ██║██║   ██║
██╔══██╗██╔══██║██║╚██╗██║██║╚██╗██║██║   ██║
██████╔╝██║  ██║██║ ╚████║██║ ╚████║╚██████╔╝
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝ ╚═════╝ """


def banner(x, y, cw, ch):
    """Draw ANSI-shadow art as geometry, so it needs no box-drawing font."""
    blocks, lines = [], []
    dx, dy = cw * 0.2, ch * 0.16
    for r, row in enumerate(BANNER.split("\n")):
        for c, g in enumerate(row):
            x0, y0 = x + c * cw, y + r * ch
            x1, y1, cx, cy = x0 + cw, y0 + ch, x0 + cw / 2, y0 + ch / 2
            if g == "█":
                blocks.append(f"M{num(x0)},{num(y0)}h{num(cw + .4)}v{num(ch + .4)}h{num(-cw - .4)}z")
            elif g == "═":
                lines += [[(x0, cy - dy), (x1, cy - dy)], [(x0, cy + dy), (x1, cy + dy)]]
            elif g == "║":
                lines += [[(cx - dx, y0), (cx - dx, y1)], [(cx + dx, y0), (cx + dx, y1)]]
            elif g == "╗":
                lines += [[(x0, cy - dy), (cx + dx, cy - dy), (cx + dx, y1)], [(x0, cy + dy), (cx - dx, cy + dy), (cx - dx, y1)]]
            elif g == "╔":
                lines += [[(x1, cy - dy), (cx - dx, cy - dy), (cx - dx, y1)], [(x1, cy + dy), (cx + dx, cy + dy), (cx + dx, y1)]]
            elif g == "╝":
                lines += [[(x0, cy + dy), (cx + dx, cy + dy), (cx + dx, y0)], [(x0, cy - dy), (cx - dx, cy - dy), (cx - dx, y0)]]
            elif g == "╚":
                lines += [[(x1, cy + dy), (cx - dx, cy + dy), (cx - dx, y0)], [(x1, cy - dy), (cx + dx, cy - dy), (cx + dx, y0)]]
    shade = " ".join("M" + " L".join(f"{num(a)},{num(b)}" for a, b in seg) for seg in lines)
    return (f'<path d="{"".join(blocks)}" fill="{GREEN}" shape-rendering="crispEdges"/>'
            f'<path d="{shade}" fill="none" stroke="{SHADOW}" stroke-width="1.5"/>')


TRACE = [(-3, 0), (-2, 1), (-1, 0), (0, 1), (-1, 2), (0, 3), (1, 2), (2, 1), (1, 0), (2, -1),
         (1, -2), (0, -1), (-1, -2), (0, -3)]


def smooth(points):
    pts = [points[0], *points, points[-1]]
    d = f"M{num(points[0][0])},{num(points[0][1])}"
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1:i + 3]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{num(c1[0])},{num(c1[1])} {num(c2[0])},{num(c2[1])} {num(p2[0])},{num(p2[1])}"
    return d


def attack_map(cx, cy, s):
    """A kolam lattice read as a network: dots are hosts, red is the attack path."""
    points = [(cx + u * s, cy + v * s) for v in range(-3, 4) for u in range(-(3 - abs(v)), 4 - abs(v))]
    r, k = s * 0.5, 0.6
    parts = []
    for x, y in points:
        d = (f"M{num(x)},{num(y - r)} Q{num(x + r * k)},{num(y - r * k)} {num(x + r)},{num(y)} "
             f"Q{num(x + r * k)},{num(y + r * k)} {num(x)},{num(y + r)} "
             f"Q{num(x - r * k)},{num(y + r * k)} {num(x - r)},{num(y)} "
             f"Q{num(x - r * k)},{num(y - r * k)} {num(x)},{num(y - r)}Z")
        parts.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    for x, y in points:
        parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="3.2" fill="{GREEN}"/>')
    path = [(cx + u * s, cy + v * s) for u, v in TRACE]
    parts.append(f'<path class="trace" pathLength="1" d="{smooth(path)}" fill="none" stroke="{RED}" '
                 f'stroke-width="3" stroke-linecap="round"/>')
    sx, sy = path[0]
    ex, ey = path[-1]
    parts.append(f'<circle cx="{num(sx)}" cy="{num(sy)}" r="6" fill="{RED}"/>')
    parts.append(show(f'<circle cx="{num(ex)}" cy="{num(ey)}" r="6" fill="{RED}"/>'
                      f'<circle cx="{num(ex)}" cy="{num(ey)}" r="14" fill="none" stroke="{RED}" stroke-width="2"/>', 3.6))
    return "\n".join(parts)


def prompt_line(cmd, y, start):
    x, size = 32, 23
    return (show(text(PROMPT, x, y, size, GREEN, 600), max(start - .3, 0))
            + typed(cmd, x + len(PROMPT) * size * .6, y, size, TEXT, start))


def hero():
    w, h = 1200, 530
    x, size = 32, 23
    adv = size * .6
    b = titlebar(w, "bannu@vega: ~")
    b.append(text("నమస్తే", w - 28, 30, 21, DIM, "te", anchor="end"))
    b.append(prompt_line("whoami", 88, .35))
    b.append(show(banner(x, 108, 15.5, 25), .95))
    b.append(show(text("Parise Ashish, cybersecurity analyst", x, 298, 29, TEXT, 600), 1.15))
    b.append(prompt_line("cat status.log", 354, 1.5))
    log = [("[+] ", GREEN, "Open to cybersecurity analyst roles", 2.65),
           ("[*] ", DIM, "Preparing for CEH v14", 2.85),
           ("[>] ", RED, "Reviewing threat detections and building the AI behind them", 3.05)]
    for i, (tag, col, msg, d) in enumerate(log):
        y = 392 + i * 33
        b.append(show(text(tag, x, y, size, col, 600) + text(msg, x + 4 * adv, y, size, TEXT, limit=1090), d))
    y = 504
    b.append(show(text(PROMPT, x, y, size, GREEN, 600)
                  + f'<rect class="cur" x="{num(x + len(PROMPT) * adv + 2)}" y="{y - 19}" width="13" height="24" fill="{GREEN}"/>', 3.35))
    b.append(attack_map(980, 208, 38))
    return svg(w, h, "\n".join(b), "Terminal: Parise Ashish (Bannu), cybersecurity analyst. "
               "Open to cybersecurity analyst roles. Preparing for CEH v14.")


# ---------------------------------------------------------------- project panes

PROJECTS = [
    dict(slug="kavach", name="Kavach Cyber", status=("demo", True),
         about="Zero-trust defence platform with EDR, SIEM correlation and DevSecOps on one core.",
         stats=[("mTLS", "agent enrolment"), ("6h", "CERT-In clock"), ("OPA", "zero-trust scoring")]),
    dict(slug="vega", name="VEGA-OS", status=("building", True),
         about="Agent-native OS where a non-AI broker checks every action a model asks to take.",
         stats=[("VARL", "agent runtime"), ("Rust", "microkernel"), ("SELinux", "MLS policy")]),
    dict(slug="jessy", name="Jessy", status=("building", True),
         about="Voice-first home network assistant that keeps personal data away from cloud models.",
         stats=[("Home lab", "self-hosted"), ("Voice", "with chat option"), ("Memory", "learns from use")]),
    dict(slug="pater", name="PATER AI", status=("training", True),
         about="Telugu Catholic theological assistant, with a corpus that fixes over-refusal.",
         stats=[("72B", "Qwen2.5 base"), ("34K", "samples, 4 tiers"), ("SFT, DPO", "QLoRA r=32")]),
    dict(slug="bharatdoc", name="BharatDoc", status=("api", False),
         about="KYC extraction API on PaddleOCR with validators for Indian identity documents.",
         stats=[("PAN", "and IFSC"), ("GSTIN", "checksum check"), ("Aadhaar", "auto-masking")]),
    dict(slug="raaga", name="Raaga.AI", status=("public", False),
         about="Composes Telugu songs on Carnatic ragas with melody, lyrics, beats and vocals.",
         stats=[("5", "layer pipeline"), ("Raga, tala", "validated theory"), ("Celery", "async render")]),
    dict(slug="formator", name="Formator AI", status=("public", False),
         about="Chat companion for seminary formators: theology, philosophy, accompaniment.",
         stats=[("Next.js", "with Groq"), ("0", "databases"), ("$0", "to run")]),
    dict(slug="ministerium", name="Ministerium", status=("platform", False),
         about="Telugu-first parish management platform for the Diocese of Khammam.",
         stats=[("Django", "with React"), ("4", "LLM providers"), ("తెలుగు", "first")]),
]


def card(p):
    w, h = 600, 290
    m = 28
    inner = w - 2 * m
    st, live = p["status"]
    b = titlebar(w, f"~/projects/{p['slug']}", f"[{st}]", GREEN if live else DIM)
    b.append(text(p["name"], m - 1, 102, 44, GREEN, 700, limit=inner))
    lines = textwrap.wrap(p["about"], 43, break_on_hyphens=False)
    if len(lines) > 2:
        raise ValueError(p["slug"])
    for i, ln in enumerate(lines):
        b.append(text(ln, m, 144 + i * 29, 21, TEXT, limit=inner))
    col = inner / 3
    for i, (v, lbl) in enumerate(p["stats"]):
        x = m + i * col
        face = "te" if any("ఀ" <= c <= "౿" for c in v) else 600
        b.append(text(v, x, 232, 24, GREEN, face, limit=col - 6))
        b.append(text(lbl, x, 260, 16, DIM, limit=col))
    return svg(w, h, "\n".join(b), f'{p["name"]}: {p["about"]}')


# ---------------------------------------------------------------- toolbox

STACK = [
    ("security/", ["mTLS", "Open Policy Agent", "YARA, eBPF", "Semgrep, Bandit", "Grype", "SELinux, seccomp"]),
    ("backend/", ["Python", "FastAPI", "Django, DRF", "Celery", "SQLAlchemy 2", "Alembic"]),
    ("models/", ["PyTorch", "Hugging Face", "QLoRA, PEFT", "SFT, DPO", "PaddleOCR", "OpenCV"]),
    ("infra/", ["PostgreSQL", "Redis", "MinIO, S3", "Docker", "Nginx", "GitHub Actions"]),
    ("ui/", ["React 19", "Next.js", "TypeScript", "Vite", "PWA", "Groq, Ollama"]),
]


def stack():
    w, h = 1200, 372
    m = 32
    col = (w - 2 * m) / len(STACK)
    b = titlebar(w, "bannu@vega: ~/toolbox")
    b.append(text(PROMPT, m, 86, 20, GREEN, 600))
    b.append(text("ls -R", m + len(PROMPT) * 12, 86, 20, TEXT))
    for i, (head, items) in enumerate(STACK):
        x = m + i * col
        b.append(text(head, x, 134, 23, GREEN, 700, limit=col - 8))
        for j, it in enumerate(items):
            b.append(text("- " + it, x, 172 + j * 31, 18, TEXT, limit=col - 6))
    return svg(w, h, "\n".join(b), "Toolbox: " + "; ".join(f"{a} {', '.join(i)}" for a, i in STACK))


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero(), encoding="utf-8")
    (OUT / "stack.svg").write_text(stack(), encoding="utf-8")
    for p in PROJECTS:
        (OUT / f"card-{p['slug']}.svg").write_text(card(p), encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT}")


if __name__ == "__main__":
    main()
