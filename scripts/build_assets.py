#!/usr/bin/env python3
"""Generate the profile README's radar-console SVG artwork.

Run from the repo root:  python3 scripts/build_assets.py
Needs:  pip install fonttools brotli uharfbuzz
Edit PROJECTS / STACK below, re-run, commit the regenerated assets/.

Text is converted to outlines (Chakra Petch, IBM Plex Mono and Anek Telugu,
scripts/fonts, SIL OFL) because GitHub cannot load web fonts inside a README image.
"""
import io
import math
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"

BG, PANEL, LINE = "#04121F", "#071B2C", "#14506B"
WHITE, TEXT, DIM, CYAN, AMBER, RED = "#FFFFFF", "#D5F6FF", "#7FB8CF", "#39C6EE", "#FFB020", "#FF3B5C"


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
    "h6": Face("chakra-petch-latin-600-normal.woff2"),
    "h7": Face("chakra-petch-latin-700-normal.woff2"),
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


def svg(w, h, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label, {'"': '&quot;'})}">
<style>
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes ping{{from{{transform:scale(.4);opacity:.9}}to{{transform:scale(2.6);opacity:0}}}}
.sweep{{animation:spin 7s linear infinite}}
.ping{{animation:ping 2.4s ease-out infinite}}
@media (prefers-reduced-motion:reduce){{.sweep,.ping{{animation:none}}}}
</style>
<rect width="{w}" height="{h}" rx="4" fill="{BG}"/>
{body}
</svg>
"""


def brackets(w, h, inset=14, arm=30, color=CYAN):
    """Targeting-reticle corners instead of a full box."""
    a, b, c, d = inset, w - inset, inset, h - inset
    d_attr = (f"M{a},{c + arm}V{c}H{a + arm} M{b - arm},{c}H{b}V{c + arm} "
              f"M{b},{d - arm}V{d}H{b - arm} M{a + arm},{d}H{a}V{d - arm}")
    return (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="4" fill="none" stroke="{LINE}"/>'
            f'<path d="{d_attr}" fill="none" stroke="{color}" stroke-width="2.5"/>')


# ---------------------------------------------------------------- hero

CONTACTS = [("Kavach", 38, .70, RED, "start"), ("VEGA-OS", 118, .62, CYAN, "start"),
            ("Jessy", 214, .78, CYAN, "end"), ("PATER AI", 306, .56, CYAN, "end")]


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def wedge(cx, cy, r, a0, a1):
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    return f"M{num(cx)},{num(cy)}L{num(x0)},{num(y0)}A{r},{r} 0 0 1 {num(x1)},{num(y1)}Z"


def radar(cx, cy, R):
    b = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>']
    for k in (.25, .5, .75):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{num(R * k)}" fill="none" stroke="{LINE}"/>')
    b.append(f'<path d="M{cx - R},{cy}H{cx + R}M{cx},{cy - R}V{cy + R}" stroke="{LINE}"/>')
    ticks = []
    for deg in range(0, 360, 10):
        inner = R - (14 if deg % 30 == 0 else 7)
        x0, y0 = polar(cx, cy, inner, deg)
        x1, y1 = polar(cx, cy, R, deg)
        ticks.append(f"M{num(x0)},{num(y0)}L{num(x1)},{num(y1)}")
    b.append(f'<path d="{"".join(ticks)}" stroke="{DIM}" stroke-width="1.2"/>')
    # Fading trail behind the leading edge, all rotating about the centre.
    sw = [f'<g class="sweep" style="transform-origin:{cx}px {cy}px">']
    head = 62
    for i in range(10):
        a1 = head - i * 7
        sw.append(f'<path d="{wedge(cx, cy, R, a1 - 7.3, a1)}" fill="{CYAN}" opacity="{round(.34 * (1 - i / 10) ** 1.6, 3)}"/>')
    x, y = polar(cx, cy, R, head)
    sw.append(f'<line x1="{cx}" y1="{cy}" x2="{num(x)}" y2="{num(y)}" stroke="{CYAN}" stroke-width="2.5"/></g>')
    b.append("".join(sw))
    for name, deg, k, col, anchor in CONTACTS:
        x, y = polar(cx, cy, R * k, deg)
        if col == RED:
            b.append(f'<circle class="ping" style="transform-origin:{num(x)}px {num(y)}px" cx="{num(x)}" cy="{num(y)}" r="12" fill="none" stroke="{RED}" stroke-width="2"/>')
        b.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{7 if col == RED else 5}" fill="{col}"/>')
        tx = x + 14 if anchor == "start" else x - 14
        b.append(text(name, tx, y + 6, 19, TEXT, 600, anchor=anchor))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{CYAN}"/>')
    return "\n".join(b)


def hero():
    w, h = 1200, 440
    x = 64
    greet = "నమస్తే"
    gx = x + 22 + measure("Threat console online", 20, 600) + 34
    b = [brackets(w, h),
         f'<circle cx="{x + 6}" cy="66" r="6" fill="{CYAN}"/>',
         text("Threat console online", x + 22, 73, 20, CYAN, 600),
         text(greet, gx, 74, 22, DIM, "te"),
         text(", I’m Bannu", gx + measure(greet, 22, "te"), 73, 20, DIM),
         text("PARISE ASHISH", x - 3, 172, 92, WHITE, "h7", limit=700),
         text("Cybersecurity analyst", x, 226, 38, CYAN, "h6", limit=700)]
    stats = [("Kavach", "EDR and SIEM", WHITE), ("VEGA-OS", "hardened OS", WHITE), ("CEH v14", "in progress", AMBER)]
    for i, (v, lbl, col) in enumerate(stats):
        sx = x + i * 228
        b.append(text(v, sx, 302, 38, col, "h6", limit=216))
        b.append(text(lbl, sx, 332, 20, TEXT))
    b.append(f'<circle cx="{x + 6}" cy="389" r="6" fill="{RED}"/>')
    b.append(text("Open to cybersecurity analyst roles", x + 22, 396, 23, WHITE, 600, limit=700))
    b.append(radar(958, 220, 178))
    return svg(w, h, "\n".join(b), "Threat console: Parise Ashish, cybersecurity analyst. "
               "Open to cybersecurity analyst roles. CEH v14 in progress.")


# ---------------------------------------------------------------- project panes

PROJECTS = [
    dict(slug="kavach", kind="Cybersecurity", name="Kavach Cyber", status=("demo", True),
         about="Zero-trust defence platform with EDR, SIEM correlation and DevSecOps on one core.",
         stats=[("mTLS", "agent enrolment"), ("6h", "CERT-In clock"), ("OPA", "zero-trust scoring")]),
    dict(slug="vega", kind="Secure systems", name="VEGA-OS", status=("building", True),
         about="Agent-native OS where a non-AI broker checks every action a model asks to take.",
         stats=[("VARL", "agent runtime"), ("Rust", "microkernel"), ("SELinux", "MLS policy")]),
    dict(slug="jessy", kind="Personal AI", name="Jessy", status=("building", True),
         about="Voice-first home network assistant that keeps personal data away from cloud models.",
         stats=[("Home lab", "self-hosted"), ("Voice", "with chat option"), ("Memory", "learns from use")]),
    dict(slug="pater", kind="LLM fine-tuning", name="PATER AI", status=("training", True),
         about="Telugu Catholic theological assistant, with a corpus that fixes over-refusal.",
         stats=[("72B", "Qwen2.5 base"), ("34K", "samples, 4 tiers"), ("SFT, DPO", "QLoRA r=32")]),
    dict(slug="bharatdoc", kind="Document AI", name="BharatDoc", status=("api", False),
         about="KYC extraction API on PaddleOCR with validators for Indian identity documents.",
         stats=[("PAN", "and IFSC"), ("GSTIN", "checksum check"), ("Aadhaar", "auto-masking")]),
    dict(slug="raaga", kind="Generative audio", name="Raaga.AI", status=("public", False),
         about="Composes Telugu songs on Carnatic ragas with melody, lyrics, beats and vocals.",
         stats=[("5", "layer pipeline"), ("Raga, tala", "validated theory"), ("Celery", "async render")]),
    dict(slug="formator", kind="AI companion", name="Formator AI", status=("public", False),
         about="Chat companion for seminary formators: theology, philosophy, accompaniment.",
         stats=[("Next.js", "with Groq"), ("0", "databases"), ("$0", "to run")]),
    dict(slug="ministerium", kind="Community tech", name="Ministerium", status=("platform", False),
         about="Telugu-first parish management platform for the Diocese of Khammam.",
         stats=[("Django", "with React"), ("4", "LLM providers"), ("తెలుగు", "first")]),
]


def card(p):
    w, h = 600, 290
    m = 36
    inner = w - 2 * m
    st, live = p["status"]
    col = AMBER if live else DIM
    b = [brackets(w, h, 10, 16),
         text(p["kind"], m, 56, 20, CYAN, 600),
         text(st.capitalize() if st != "api" else "API", w - m, 56, 20, col, 600, anchor="end")]
    st_w = measure(st.capitalize() if st != "api" else "API", 20, 600)
    b.append(f'<circle cx="{num(w - m - st_w - 15)}" cy="49" r="5" fill="{col}"/>')
    b.append(text(p["name"].upper(), m - 2, 118, 50, WHITE, "h7", limit=inner))
    lines = textwrap.wrap(p["about"], 43, break_on_hyphens=False)
    if len(lines) > 2:
        raise ValueError(p["slug"])
    for i, ln in enumerate(lines):
        b.append(text(ln, m, 158 + i * 28, 20, TEXT, limit=inner))
    c = inner / 3
    for i, (v, lbl) in enumerate(p["stats"]):
        x = m + i * c
        face = "te" if any("ఀ" <= ch <= "౿" for ch in v) else "h6"
        b.append(text(v, x, 242, 26, CYAN, face, limit=c - 6))
        b.append(text(lbl, x, 267, 16, DIM, limit=c))
    return svg(w, h, "\n".join(b), f'{p["name"]}: {p["about"]}')


# ---------------------------------------------------------------- toolbox

STACK = [
    ("Security", ["mTLS", "Open Policy Agent", "YARA, eBPF", "Semgrep, Bandit", "Grype", "SELinux, seccomp"]),
    ("Backend", ["Python", "FastAPI", "Django, DRF", "Celery", "SQLAlchemy 2", "Alembic"]),
    ("Models and ML", ["PyTorch", "Hugging Face", "QLoRA, PEFT", "SFT, DPO", "PaddleOCR", "OpenCV"]),
    ("Data and infra", ["PostgreSQL", "Redis", "MinIO, S3", "Docker", "Nginx", "GitHub Actions"]),
    ("Interface", ["React 19", "Next.js", "TypeScript", "Vite", "PWA", "Groq, Ollama"]),
]


def stack():
    w, h = 1200, 320
    m = 56
    col = (w - 2 * m) / len(STACK)
    b = [brackets(w, h)]
    for i, (head, items) in enumerate(STACK):
        x = m + i * col
        color = RED if head == "Security" else CYAN
        b.append(f'<rect x="{num(x)}" y="52" width="{num(col - 26)}" height="3" fill="{color}"/>')
        b.append(text(head, x, 94, 26, WHITE, "h7", limit=col - 12))
        for j, it in enumerate(items):
            b.append(text(it, x, 136 + j * 29, 18.5, TEXT, limit=col - 10))
    return svg(w, h, "\n".join(b), "Toolbox: " + "; ".join(f"{a}: {', '.join(i)}" for a, i in STACK))


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero(), encoding="utf-8")
    (OUT / "stack.svg").write_text(stack(), encoding="utf-8")
    for p in PROJECTS:
        (OUT / f"card-{p['slug']}.svg").write_text(card(p), encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT}")


if __name__ == "__main__":
    main()
