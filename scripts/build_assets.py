#!/usr/bin/env python3
"""Generate the profile README's SVG artwork (dark + light variants).

Run from the repo root:  python3 scripts/build_assets.py
Needs:  pip install fonttools brotli uharfbuzz
Edit PROJECTS / STACK below, re-run, commit the regenerated assets/.

Text is converted to outlines with Anek Telugu (scripts/fonts, SIL OFL), so the
artwork looks the same on every device. GitHub cannot load web fonts in a README.
"""
import io
from pathlib import Path
from xml.sax.saxutils import escape

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"

# Indigo ground, rice-flour white, kumkum red. Red only ever marks live signal.
THEMES = {
    "dark": dict(bg="#18225A", surface="#1F2B6B", line="#3A478C", text="#F5F1E8",
                 muted="#BCC4E4", faint="#8590C2", signal="#FF7A66"),
    "light": dict(bg="#E9ECF8", surface="#F6F7FD", line="#C6CDE6", text="#18225A",
                  muted="#465082", faint="#8089B3", signal="#C42B22"),
}


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
    400: Face("anek-telugu-latin-400-normal.woff2"),
    500: Face("anek-telugu-latin-500-normal.woff2"),
    700: Face("anek-telugu-latin-700-normal.woff2"),
    "te": Face("anek-telugu-telugu-500-normal.woff2"),
}


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def measure(s, size, weight=400):
    f = FACES[weight]
    return sum(p.x_advance for p in f.shape(s)[1]) * size / f.upem


def text(s, x, y, size, fill, weight=400, anchor="start", limit=None):
    """Return one outlined <path>, and fail loudly if the run overflows `limit`."""
    width = measure(s, size, weight)
    if limit and width > limit:
        raise ValueError(f"{s!r} is {width:.0f}px wide, limit {limit}")
    f = FACES[weight]
    k = size / f.upem
    pen_x = x - width if anchor == "end" else x
    pen = SVGPathPen(f.glyphs, ntos=num)
    infos, positions = f.shape(s)
    for info, pos in zip(infos, positions):
        gx = pen_x + pos.x_offset * k
        gy = y - pos.y_offset * k
        f.glyphs[f.order[info.codepoint]].draw(TransformPen(pen, (k, 0, 0, -k, gx, gy)))
        pen_x += pos.x_advance * k
    return f'<path d="{pen.getCommands()}" fill="{fill}"/>'


def svg(w, h, body, t, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label, {'"': '&quot;'})}">
<style>
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes land{{to{{opacity:1}}}}
.trace{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 3.2s cubic-bezier(.55,0,.25,1) .3s forwards}}
.end{{opacity:0;animation:land .4s ease-out 3.4s forwards}}
@media (prefers-reduced-motion:reduce){{.trace{{animation:none;stroke-dashoffset:0}}.end{{animation:none;opacity:1}}}}
</style>
<rect width="{w}" height="{h}" rx="8" fill="{t['bg']}"/>
{body}
</svg>
"""


# ---------------------------------------------------------------- hero

# Lattice steps walked by the red line: one continuous stroke, the way a kolam
# is drawn, and the way an attack chain moves host to host.
TRACE = [(-3, 0), (-2, 1), (-1, 0), (0, 1), (-1, 2), (0, 3), (1, 2), (2, 1), (1, 0), (2, -1),
         (1, -2), (0, -1), (-1, -2), (0, -3)]


def smooth(points):
    """Catmull-Rom through the points, as cubic Beziers."""
    pts = [points[0], *points, points[-1]]
    d = f"M{num(points[0][0])},{num(points[0][1])}"
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1:i + 3]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{num(c1[0])},{num(c1[1])} {num(c2[0])},{num(c2[1])} {num(p2[0])},{num(p2[1])}"
    return d


def kolam(cx, cy, s, t):
    points = [(cx + u * s, cy + v * s) for v in range(-3, 4) for u in range(-(3 - abs(v)), 4 - abs(v))]
    r, k = s * 0.5, 0.6
    parts = []
    for x, y in points:
        d = (f"M{num(x)},{num(y - r)} Q{num(x + r * k)},{num(y - r * k)} {num(x + r)},{num(y)} "
             f"Q{num(x + r * k)},{num(y + r * k)} {num(x)},{num(y + r)} "
             f"Q{num(x - r * k)},{num(y + r * k)} {num(x - r)},{num(y)} "
             f"Q{num(x - r * k)},{num(y - r * k)} {num(x)},{num(y - r)}Z")
        parts.append(f'<path d="{d}" fill="none" stroke="{t["line"]}" stroke-width="1.5"/>')
    for x, y in points:
        parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="3.4" fill="{t["text"]}"/>')
    path = [(cx + u * s, cy + v * s) for u, v in TRACE]
    parts.append(f'<path class="trace" pathLength="1" d="{smooth(path)}" fill="none" '
                 f'stroke="{t["signal"]}" stroke-width="3.5" stroke-linecap="round"/>')
    ex, ey = path[-1]
    parts.append(f'<g class="end"><circle cx="{num(ex)}" cy="{num(ey)}" r="6" fill="{t["signal"]}"/>'
                 f'<circle cx="{num(ex)}" cy="{num(ey)}" r="14" fill="none" stroke="{t["signal"]}" stroke-width="2"/></g>')
    sx, sy = path[0]
    parts.append(f'<circle cx="{num(sx)}" cy="{num(sy)}" r="6" fill="{t["signal"]}"/>')
    return "\n".join(parts)


def hero(t):
    w, h = 1200, 440
    x = 64
    greet = "నమస్తే"
    b = [text(greet, x, 88, 32, t["muted"], "te"),
         text(", I’m Bannu", x + measure(greet, 32, "te"), 88, 30, t["muted"], 500),
         text("Parise Ashish", x - 4, 196, 112, t["text"], 700, limit=730),
         text("Cybersecurity analyst", x, 258, 44, t["text"], 500, limit=730),
         text("I review threat detections and build the Python and", x, 314, 25, t["muted"], limit=730),
         text("AI systems that help analysts act on them.", x, 348, 25, t["muted"], limit=730),
         f'<circle cx="{x + 6}" cy="393" r="6" fill="{t["signal"]}"/>',
         text("Open to cybersecurity analyst roles. Preparing for CEH v14.", x + 24, 400, 21, t["text"], 500, limit=700)]
    b.append(kolam(986, 220, 42, t))
    return svg(w, h, "\n".join(b), t,
               "Parise Ashish (Bannu), cybersecurity analyst. Open to cybersecurity analyst roles.")


# ---------------------------------------------------------------- project cards

PROJECTS = [
    dict(slug="kavach", kind="Cybersecurity", name="Kavach Cyber", status=("Demo", True),
         lines=["Indigenous zero-trust defence platform with EDR,", "SIEM correlation and DevSecOps on one core."],
         stats=[("mTLS", "agent enrolment"), ("6h", "CERT-In clock"), ("OPA", "zero-trust scoring")]),
    dict(slug="vega", kind="Secure systems", name="VEGA-OS", status=("Building", True),
         lines=["Agent-native OS where a non-AI broker checks", "every system action a model asks to take."],
         stats=[("VARL", "agent runtime"), ("Rust", "microkernel"), ("SELinux", "MLS policy")]),
    dict(slug="jessy", kind="Personal AI", name="Jessy", status=("Building", True),
         lines=["Voice-first assistant on my home network, built", "so personal data stays away from cloud models."],
         stats=[("Home lab", "self-hosted"), ("Voice", "with chat option"), ("Memory", "learns from use")]),
    dict(slug="pater", kind="LLM fine-tuning", name="PATER AI", status=("Training", True),
         lines=["Telugu Catholic theological assistant, with a", "desensitisation corpus that fixes over-refusal."],
         stats=[("72B", "Qwen2.5 base"), ("34K", "samples in 4 tiers"), ("SFT, DPO", "QLoRA r=32")]),
    dict(slug="bharatdoc", kind="Document AI", name="BharatDoc", status=("API", False),
         lines=["KYC extraction API on PaddleOCR with production", "validators for Indian identity documents."],
         stats=[("PAN", "and IFSC"), ("GSTIN", "checksum check"), ("Aadhaar", "auto-masking")]),
    dict(slug="raaga", kind="Generative audio", name="Raaga.AI", status=("Public", False),
         lines=["Composes Telugu songs on authentic Carnatic", "ragas with melody, lyrics, beats and vocals."],
         stats=[("5", "layer pipeline"), ("Raga, tala", "validated theory"), ("Celery", "async render")]),
    dict(slug="formator", kind="AI companion", name="Formator AI", status=("Public", False),
         lines=["Chat companion for seminary formators, covering", "theology, philosophy and accompaniment."],
         stats=[("Next.js", "with Groq"), ("0", "databases"), ("$0", "to run")]),
    dict(slug="ministerium", kind="Community tech", name="Ministerium", status=("Platform", False),
         lines=["Telugu-first parish management platform for", "the Diocese of Khammam."],
         stats=[("Django", "with React"), ("4", "LLM providers"), ("తెలుగు", "first")]),
]


def card(p, t):
    w, h = 600, 300
    st, live = p["status"]
    m = 36
    inner = w - 2 * m
    st_w = measure(st, 20, 500)
    b = [f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="{t["surface"]}" stroke="{t["line"]}"/>',
         text(p["kind"], m, 54, 20, t["muted"], 500),
         f'<circle cx="{num(w - m - st_w - 15)}" cy="47" r="5" fill="{t["signal"] if live else t["faint"]}"/>',
         text(st, w - m, 54, 20, t["muted"], 500, anchor="end"),
         text(p["name"], m - 2, 124, 56, t["text"], 700, limit=inner)]
    for i, ln in enumerate(p["lines"]):
        b.append(text(ln, m, 168 + i * 31, 23, t["muted"], limit=inner))
    col = inner / 3
    for i, (v, lbl) in enumerate(p["stats"]):
        x = m + i * col
        face = "te" if any("ఀ" <= c <= "౿" for c in v) else 500
        b.append(text(v, x, 256, 27, t["text"], face, limit=col - 10))
        b.append(text(lbl, x, 281, 18, t["muted"], limit=col - 10))
    return svg(w, h, "\n".join(b), t, f'{p["name"]}: {" ".join(p["lines"])}')


# ---------------------------------------------------------------- stack

STACK = [
    ("Security", ["mTLS", "Open Policy Agent", "YARA, eBPF", "Semgrep, Bandit", "Grype", "SELinux, seccomp"]),
    ("Backend", ["Python", "FastAPI", "Django, DRF", "Celery", "SQLAlchemy 2", "Alembic"]),
    ("Models and ML", ["PyTorch", "Hugging Face", "QLoRA, PEFT", "SFT, DPO", "PaddleOCR", "OpenCV"]),
    ("Data and infra", ["PostgreSQL", "Redis", "MinIO, S3", "Docker", "Nginx", "GitHub Actions"]),
    ("Interface", ["React 19", "Next.js", "TypeScript", "Vite", "PWA", "Groq, Ollama"]),
]


def stack(t):
    w, h = 1200, 330
    m = 56
    col = (w - 2 * m) / len(STACK)
    b = [f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="none" stroke="{t["line"]}"/>']
    for i, (head, items) in enumerate(STACK):
        x = m + i * col
        b.append(text(head, x, 82, 29, t["text"], 700, limit=col - 12))
        for j, it in enumerate(items):
            b.append(text(it, x, 128 + j * 32, 21, t["muted"], limit=col - 12))
    return svg(w, h, "\n".join(b), t, "Tech stack: " + "; ".join(f"{h_}: {', '.join(i)}" for h_, i in STACK))


def main():
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"hero-{name}.svg").write_text(hero(t), encoding="utf-8")
        (OUT / f"stack-{name}.svg").write_text(stack(t), encoding="utf-8")
        for p in PROJECTS:
            (OUT / f"card-{p['slug']}-{name}.svg").write_text(card(p, t), encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT}")


if __name__ == "__main__":
    main()
