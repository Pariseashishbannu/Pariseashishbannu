#!/usr/bin/env python3
"""Generate the profile README's SVG artwork (dark + light variants).

Run from the repo root:  python3 scripts/build_assets.py
Edit PROJECTS / STACK below, re-run, commit the regenerated assets/.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0C0B0A", surface="#151311", line="#2B2723", text="#F2ECE3",
                 muted="#948B7F", faint="#5E574E", accent="#E9A13B", accent2="#7FB2A6"),
    "light": dict(bg="#FBF8F2", surface="#F4EFE6", line="#E3DACB", text="#1C1813",
                  muted="#6B6358", faint="#A69C8D", accent="#B5690F", accent2="#3F7F72"),
}

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Noto Serif','DejaVu Serif',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
TELUGU = "'Noto Sans Telugu','Nirmala UI','Telugu Sangam MN','Gautami',sans-serif"


def e(s):
    return escape(s)


def svg(w, h, body, t, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}">
<style>
.serif{{font-family:{SERIF}}} .sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}} .te{{font-family:{TELUGU}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.k{{fill:none;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.6s cubic-bezier(.6,0,.2,1) forwards}}
.r{{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards}}
.cur{{animation:blink 1.1s steps(1) infinite}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{.k,.r{{animation:none;opacity:1;stroke-dashoffset:0}}.cur,.pulse{{animation:none}}}}
</style>
<rect width="{w}" height="{h}" rx="18" fill="{t['bg']}"/>
{body}
</svg>
"""


# ---------------------------------------------------------------- hero

def kolam(cx, cy, s, t):
    """Pulli kolam: a diamond lattice of dots, each wrapped in a soft rhombus."""
    rows = [1, 3, 5, 7, 5, 3, 1]
    dots = []
    for i, n in enumerate(rows):
        y = cy + (i - 3) * s
        for j in range(n):
            dots.append((cx + (j - (n - 1) / 2) * s, y))
    r, k = s * 0.5, 0.6
    parts = []
    order = sorted(dots, key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy)))
    for idx, (x, y) in enumerate(order):
        d = (f"M{x:.1f},{y - r:.1f} Q{x + r * k:.1f},{y - r * k:.1f} {x + r:.1f},{y:.1f} "
             f"Q{x + r * k:.1f},{y + r * k:.1f} {x:.1f},{y + r:.1f} "
             f"Q{x - r * k:.1f},{y + r * k:.1f} {x - r:.1f},{y:.1f} "
             f"Q{x - r * k:.1f},{y - r * k:.1f} {x:.1f},{y - r:.1f}Z")
        parts.append(f'<path class="k" pathLength="1" d="{d}" stroke="{t["accent"]}" '
                     f'stroke-width="1.6" style="animation-delay:{0.25 + idx * 0.035:.2f}s"/>')
    R = s * 4.15
    outer = (f"M{cx},{cy - R} Q{cx + R * .55},{cy - R * .55} {cx + R},{cy} "
             f"Q{cx + R * .55},{cy + R * .55} {cx},{cy + R} "
             f"Q{cx - R * .55},{cy + R * .55} {cx - R},{cy} "
             f"Q{cx - R * .55},{cy - R * .55} {cx},{cy - R}Z")
    parts.append(f'<path class="k" pathLength="1" d="{outer}" stroke="{t["faint"]}" '
                 f'stroke-width="1" style="animation-delay:1.9s;animation-duration:2.4s"/>')
    for x, y in dots:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{t["text"]}"/>')
    return "\n".join(parts)


def hero(t):
    w, h = 1200, 440
    b = []
    # hairline frame + grid ticks
    b.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{t["line"]}"/>')
    b.append(f'<line x1="56" y1="78" x2="{w - 56}" y2="78" stroke="{t["line"]}"/>')
    b.append(f'<line x1="56" y1="{h - 78}" x2="{w - 56}" y2="{h - 78}" stroke="{t["line"]}"/>')
    # top bar
    b.append(f'<g class="r mono" font-size="13" letter-spacing="1.5" style="animation-delay:.05s">'
             f'<circle class="pulse" cx="62" cy="48" r="4" fill="{t["accent2"]}"/>'
             f'<text x="76" y="52" fill="{t["muted"]}">AVAILABLE FOR CONTRACT WORK</text>'
             f'<text x="{w - 56}" y="52" text-anchor="end" fill="{t["muted"]}">17.3850° N · 78.4867° E — HYDERABAD / BHADRACHALAM</text></g>')
    # greeting
    b.append(f'<g class="r" style="animation-delay:.15s">'
             f'<text x="56" y="138" class="te" font-size="26" fill="{t["accent"]}">నమస్తే</text>'
             f'<text x="150" y="137" class="mono" font-size="14" fill="{t["faint"]}">/ namaste — I’m Bannu</text></g>')
    # name
    b.append(f'<text class="r serif" x="52" y="226" font-size="88" fill="{t["text"]}" letter-spacing="-1.5" '
             f'style="animation-delay:.25s">Parise Ashish<tspan fill="{t["accent"]}">.</tspan></text>')
    # role
    b.append(f'<g class="r sans" font-size="21" fill="{t["muted"]}" style="animation-delay:.4s">'
             f'<text x="56" y="272">Python backend &amp; AI engineer. I fine-tune language models,</text>'
             f'<text x="56" y="302">build document intelligence, and ship security platforms —</text>'
             f'<text x="56" y="332"><tspan fill="{t["text"]}">sovereign, culturally-intelligent software for India.</tspan></text></g>')
    # bottom ticker
    b.append(f'<g class="r mono" font-size="14" style="animation-delay:.6s">'
             f'<circle class="pulse" cx="60" cy="{h - 45}" r="4" fill="{t["accent"]}"/>'
             f'<text x="74" y="{h - 40}" fill="{t["faint"]}">NOW<tspan dx="12" fill="{t["text"]}">Training PATER AI on Qwen2.5-72B</tspan></text>'
             f'<text x="{w - 56}" y="{h - 40}" text-anchor="end" fill="{t["text"]}">MSc Computer Science · Sapienza, Rome 2027</text>'
             f'<text x="{w - 440}" y="{h - 40}" text-anchor="end" fill="{t["faint"]}">NEXT</text></g>')
    b.append(kolam(966, 222, 30, t))
    return svg(w, h, "\n".join(b), t, "Parise Ashish (Bannu) — Python backend and AI engineer")


# ---------------------------------------------------------------- project cards

PROJECTS = [
    dict(slug="pater", no="01", kind="LLM FINE-TUNING", name="PATER AI", status=("training", True),
         lines=["Telugu Catholic theological assistant, with a", "desensitisation corpus that fixes over-refusal."],
         stats=[("72B", "Qwen2.5 base"), ("34K", "samples · 4 tiers"), ("SFT→DPO", "QLoRA r=32")]),
    dict(slug="kavach", no="02", kind="CYBERSECURITY", name="Kavach Cyber", status=("mvp", True),
         lines=["Indigenous zero-trust defence platform: EDR,", "SIEM correlation and DevSecOps on one core."],
         stats=[("mTLS", "agent enrolment"), ("6h", "CERT-In clock"), ("OPA", "zero-trust scoring")]),
    dict(slug="raaga", no="03", kind="GENERATIVE AUDIO", name="Raaga.AI", status=("public", False),
         lines=["Composes Telugu songs on authentic Carnatic", "ragas — melody, lyrics, beats and vocals."],
         stats=[("5", "layer pipeline"), ("raga·tala", "validated theory"), ("Celery", "async render")]),
    dict(slug="bharatdoc", no="04", kind="DOCUMENT AI", name="BharatDoc", status=("api", False),
         lines=["KYC extraction API on PaddleOCR with production", "validators for Indian identity documents."],
         stats=[("PAN", "+ IFSC"), ("GSTIN", "Verhoeff check"), ("Aadhaar", "auto-masking")]),
    dict(slug="ministerium", no="05", kind="COMMUNITY TECH", name="Ministerium", status=("platform", False),
         lines=["Telugu-first parish management platform for", "the Diocese of Khammam."],
         stats=[("Django", "+ React"), ("4", "LLM providers"), ("తెలుగు", "first")]),
    dict(slug="formator", no="06", kind="AI COMPANION", name="Formator AI", status=("public", False),
         lines=["Chat companion for seminary formators —", "theology, philosophy, accompaniment."],
         stats=[("Next.js", "+ Groq"), ("0", "databases"), ("$0", "to run")]),
]


def card(p, t):
    w, h = 600, 300
    st, live = p["status"]
    b = [f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="{t["surface"]}" stroke="{t["line"]}"/>',
         f'<rect x="0" y="40" width="3" height="28" fill="{t["accent"]}"/>',
         f'<text x="32" y="60" class="mono" font-size="13" letter-spacing="1.6" fill="{t["muted"]}">'
         f'<tspan fill="{t["accent"]}">{p["no"]}</tspan>  ·  {p["kind"]}</text>']
    pill_w = 22 + len(st) * 8.4 + 16
    px = w - 32 - pill_w
    b.append(f'<rect x="{px:.1f}" y="40" width="{pill_w:.1f}" height="28" rx="14" fill="none" stroke="{t["line"]}"/>')
    pulse = 'class="pulse" ' if live else ""
    b.append(f'<circle {pulse}cx="{px + 15:.1f}" cy="54" r="3.5" '
             f'fill="{t["accent2"] if live else t["faint"]}"/>')
    b.append(f'<text x="{px + 26:.1f}" y="58.5" class="mono" font-size="12.5" letter-spacing="1.2" fill="{t["muted"]}">{st.upper()}</text>')
    b.append(f'<text x="30" y="122" class="serif" font-size="42" letter-spacing="-.5" fill="{t["text"]}">{e(p["name"])}</text>')
    for i, ln in enumerate(p["lines"]):
        b.append(f'<text x="32" y="{158 + i * 25}" class="sans" font-size="17" fill="{t["muted"]}">{e(ln)}</text>')
    b.append(f'<line x1="32" y1="212" x2="{w - 32}" y2="212" stroke="{t["line"]}"/>')
    col = (w - 64) / 3
    for i, (v, lbl) in enumerate(p["stats"]):
        x = 32 + i * col
        if i:
            b.append(f'<line x1="{x - 14:.1f}" y1="230" x2="{x - 14:.1f}" y2="272" stroke="{t["line"]}"/>')
        cls = "te" if any("ఀ" <= c <= "౿" for c in v) else "mono"
        b.append(f'<text x="{x:.1f}" y="250" class="{cls}" font-size="21" font-weight="600" fill="{t["accent"]}">{e(v)}</text>')
        b.append(f'<text x="{x:.1f}" y="272" class="sans" font-size="13" fill="{t["muted"]}">{e(lbl)}</text>')
    return svg(w, h, "\n".join(b), t, f'{p["name"]} — {" ".join(p["lines"])}')


# ---------------------------------------------------------------- stack

STACK = [
    ("Models & ML", ["PyTorch", "Hugging Face", "QLoRA · PEFT", "SFT · DPO", "PaddleOCR", "OpenCV"]),
    ("Backend", ["Python", "FastAPI", "Django · DRF", "Celery", "SQLAlchemy 2", "Alembic"]),
    ("Data & Infra", ["PostgreSQL", "Redis", "MinIO · S3", "Docker", "Nginx", "GitHub Actions"]),
    ("Security", ["mTLS", "Open Policy Agent", "YARA · eBPF", "Semgrep · Bandit", "Grype", "Linux"]),
    ("Interface", ["React 19", "Next.js", "TypeScript", "Vite", "PWA", "Groq · Ollama"]),
]


def stack(t):
    w, h = 1200, 330
    b = [f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{t["line"]}"/>']
    col = (w - 112) / len(STACK)
    for i, (head, items) in enumerate(STACK):
        x = 56 + i * col
        if i:
            b.append(f'<line x1="{x - 20:.1f}" y1="48" x2="{x - 20:.1f}" y2="{h - 48}" stroke="{t["line"]}"/>')
        b.append(f'<g class="r" style="animation-delay:{0.08 * i:.2f}s">'
                 f'<text x="{x:.1f}" y="66" class="mono" font-size="12.5" letter-spacing="1.6" fill="{t["accent"]}">'
                 f'{i + 1:02d}</text>'
                 f'<text x="{x:.1f}" y="98" class="serif" font-size="24" fill="{t["text"]}">{e(head)}</text>')
        for j, it in enumerate(items):
            b.append(f'<text x="{x:.1f}" y="{142 + j * 30}" class="sans" font-size="16" fill="{t["muted"]}">{e(it)}</text>')
        b.append('</g>')
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
