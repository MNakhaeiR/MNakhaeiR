"""
Generates every SVG under assets/ for the profile README.

    pip install pillow   # only needed if you change the screenshots
    python scripts/build.py

Edit the data blocks below (projects, journey, stats…) and re-run. Everything is
plain SVG with CSS/SMIL animation — no external services, so nothing can rate-limit
or go down. Screenshots in scripts/shots/ are embedded straight into the cards.
"""

import base64
import itertools
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SHOTS = Path(__file__).resolve().parent / "shots"

# ---------------------------------------------------------------------------
# Design tokens — matched to mnakhae.ir (zinc neutrals + Tailwind blue-600).
# ---------------------------------------------------------------------------
BG = "#09090B"
SURFACE = "#111113"
RAISED = "#18181B"
BORDER = "#27272A"
TEXT = "#FAFAFA"
MUTED = "#A1A1AA"
DIM = "#71717A"
FAINT = "#52525B"

BLUE = "#155DFC"
BLUE_L = "#6E9BFF"
VIOLET = "#AD46FF"
EMERALD = "#00BC7D"
AMBER = "#FD9A00"
ROSE = "#FF2056"
SILVER = "#E4E4E7"

SANS = "'Segoe UI Variable Display','Segoe UI',system-ui,-apple-system,'SF Pro Display','Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
FA = "'Segoe UI','Vazirmatn','Geeza Pro','Noto Sans Arabic',Tahoma,sans-serif"

# Width of one monospace character, as a fraction of font size. Every mono run
# that has to line up with something uses textLength, so this is exact everywhere.
MONO_W = 0.6

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
PROJECTS = [
    dict(slug="gameline", title="Game Line", kind="GAMING · OPS", accent=VIOLET, url="https://gamelinee.ir",
         blurb="Bookings, a play-time wallet and live station status for a gaming club & café.",
         tags=["Next.js", "NestJS", ".NET"]),
    dict(slug="nibolingo", title="NiboLingo", kind="EDTECH", accent=EMERALD, url="https://nibolingo.com",
         blurb="Live 1-on-1 English classes for kids aged 4–15, in English and Chinese.",
         tags=["Next.js", "Tailwind", "i18n"]),
    dict(slug="matteo-comedy", title="Matteo Comedy", kind="TICKETING", accent=AMBER, url="https://matteocomedy.com",
         blurb="Stand-up comedy tickets with automatic card-to-card payment matching.",
         tags=["Next.js", "Tailwind", "Payments"]),
    dict(slug="iranbnb", title="Iranbnb", kind="TRAVEL", accent=ROSE, url="https://beenb.ir",
         blurb="Book Airbnb stays from Iran, paid in toman, with live booking status.",
         tags=["Next.js", "Tailwind", "Wallet"]),
    dict(slug="hyper-sadra", title="Hyper Sadra", kind="E-COMMERCE", accent=BLUE_L, url="https://hypersadra.mnakhae.ir",
         blurb="An installment-based store for home appliances, with fast credit checks.",
         tags=["Next.js", "Node.js", "TypeScript"]),
    dict(slug="rose-photo-art", title="Rose Photo Art", kind="PORTFOLIO · CMS", accent=SILVER, url="https://rosephoto.art",
         blurb="A photography portfolio with a self-serve CMS, so new work ships without code.",
         tags=["Next.js", "GSAP", "Supabase"]),
    dict(slug="vasset", title="Vasset", kind="PRICE COMPARISON", accent=EMERALD, url="https://vasset.ir",
         blurb="Compare fashion prices across Turkish and UAE stores, converted to toman.",
         tags=["Next.js", "Tailwind", "TypeScript"]),
    dict(slug="mano-computer-studio", title="Mano Computer Studio", kind="EDU · SIMULATOR", accent=VIOLET,
         url="https://ca.mnakhae.ir",
         blurb="An interactive simulator for Morris Mano's Basic Computer architecture.",
         tags=["Next.js", "shadcn/ui", "TypeScript"]),
]

STATS = [
    ("17", "products live", "in production", BLUE_L),
    ("3+", "years shipping", "for real clients", VIOLET),
    ("59%", "of my code", "is TypeScript", EMERALD),
    ("♫", "classical music", "on repeat", AMBER),
]

LANGUAGES = [  # share of bytes across all my repositories
    ("TypeScript", 58.8, "#3178C6"),
    ("Python", 9.2, "#3572A5"),
    ("TeX", 8.7, "#3D6117"),
    ("Dart", 6.4, "#00B4AB"),
    ("Rust", 6.1, "#DEA584"),
    ("JavaScript", 3.0, "#F1E05A"),
    ("Zig", 1.4, "#EC915C"),
    ("Other", 6.4, "#52525B"),
]

JOURNEY = [
    ("2020 — 2023", "Sharif University of Technology", "Physics — then left to build software",
     "The first-principles habit I still debug with."),
    ("JUL 2023 — NOW", "Freelance full-stack developer", "Design to deploy, end to end",
     "Next.js, NestJS and GSAP products, with AI features in PyTorch and OpenCV."),
    ("SEP 2024 — NOW", "Islamic Azad University", "B.Sc. Computer Engineering",
     "Software engineering, algorithms and AI — plus coding competitions."),
    ("FEB — JUN 2025", "SAV", "Backend developer · finance",
     "REST APIs in Laravel and MySQL, shipped with Docker and CI/CD."),
    ("2026", "17 products live", "Game Line, NiboLingo, Matteo, Iranbnb…",
     "…and the next one is already in the editor."),
]

SECTIONS = {
    "about": ("01", "ABOUT", "A physicist who fell for code"),
    "shipped": ("02", "SHIPPED", "Live in production"),
    "stack": ("03", "STACK", "Tools I reach for"),
    "journey": ("04", "JOURNEY", "From physics to production"),
    "writing": ("05", "WRITING", "Notes from the build"),
}

BUTTONS = [
    ("website", "mnakhae.ir", "globe"),
    ("linkedin", "LinkedIn", "linkedin"),
    ("telegram", "Telegram", "telegram"),
    ("email", "Email", "mail"),
    ("cv-frontend", "Frontend CV", "doc"),
    ("cv-backend", "Backend CV", "doc"),
    ("cv-ai", "AI & Data CV", "doc"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def svg(w, h, body, label, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label, {chr(34): "&quot;"})}">'
        f"<title>{escape(label)}</title>"
        f"<style>{style}{REDUCED_MOTION}</style>{body}</svg>\n"
    )


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"{path.relative_to(ROOT)}  {len(content.encode()) // 1024} KB")


def mono_len(text, size, ls=0):
    return round(len(text) * (size * MONO_W + ls), 2)


def mono(text, x, y, size, fill, ls=0, extra=""):
    """Monospace text forced to an exact width (tracking included), so layout math holds on every OS."""
    return (f'<text xml:space="preserve" x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" letter-spacing="{ls}" '
            f'textLength="{mono_len(text, size, ls)}" lengthAdjust="spacingAndGlyphs" {extra}>{escape(text)}</text>')


def wrap(text, limit):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > limit:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def panel(w, h, rx=28):
    return (f'<defs><clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
            f'<rect width="{w}" height="{h}" rx="{rx}" fill="{BG}"/>')


def border(w, h, rx=28):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" stroke="#FFFFFF" stroke-opacity=".1"/>'


_ids = itertools.count(1)


def sweep(w, y, color, dur=7, begin=0, height=2, length=260):
    """A soft highlight that travels along a hairline."""
    gid = f"sw{next(_ids)}"
    return (
        f'<defs><linearGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
        f'<rect x="{-length}" y="{y - height / 2}" width="{length}" height="{height}" fill="url(#{gid})">'
        f'<animate attributeName="x" values="{-length};{w}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></rect>'
    )


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
def typing_line(phrases, x, y, size, cycle_each=4.2):
    """Types, holds and erases each phrase in turn. Static fallback: the first phrase."""
    cw = size * MONO_W
    total = cycle_each * len(phrases)

    def events(i, n):
        """(time, visible width) steps for phrase i: type one char at a time, hold, erase."""
        start = i * cycle_each
        type_d, hold_end, erase_d = 1.5, start + 3.3, 0.45
        steps = [(start, 0.0)]
        steps += [(start + type_d * k / n, k * cw) for k in range(1, n + 1)]
        steps += [(hold_end + erase_d * k / n, (n - k) * cw) for k in range(1, n + 1)]
        return steps

    def keyframes(steps):
        steps = sorted(dict([(0.0, 0.0)] + steps + [(total, 0.0)]).items())  # dedupe t=0
        return (";".join(f"{t / total:.5f}" for t, _ in steps), [w for _, w in steps])

    out, cursor = [], []
    for i, phrase in enumerate(phrases):
        steps = events(i, len(phrase))
        cursor += steps
        kt, widths = keyframes(steps)
        static_w = len(phrase) * cw if i == 0 else 0  # what shows if SMIL is unsupported
        out.append(
            f'<clipPath id="type{i}"><rect x="{x}" y="{y - size}" height="{size * 1.4}" width="{static_w:.1f}">'
            f'<animate attributeName="width" values="{";".join(f"{w:.1f}" for w in widths)}" keyTimes="{kt}" '
            f'dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
            f'<g clip-path="url(#type{i})">{mono(phrase, x, y, size, TEXT)}</g>'
        )
    # The caret follows whichever phrase is being typed.
    kt, widths = keyframes(cursor)
    vals = ";".join(f"{x + w + 4:.1f}" for w in widths)
    out.append(
        f'<rect class="caret" x="{x + len(phrases[0]) * cw + 4:.1f}" y="{y - size * 0.82}" width="{size * 0.5}" height="{size * 1.02}" rx="2" fill="{BLUE_L}">'
        f'<animate attributeName="x" values="{vals}" keyTimes="{kt}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></rect>'
    )
    return "".join(out)


def orbit(cx, cy):
    rings = [(-24, 168, 54, 7, BLUE_L), (38, 148, 46, 10, VIOLET), (86, 124, 40, 13, ROSE)]
    out = [f'<g transform="translate({cx} {cy})">',
           f'<circle r="150" fill="url(#coreGlow)"/>',
           f'<circle r="96" fill="none" stroke="#FFFFFF" stroke-opacity=".14" stroke-dasharray="2 9">'
           f'<animateTransform attributeName="transform" type="rotate" values="0;360" dur="60s" repeatCount="indefinite"/></circle>']
    for i, (tilt, rx, ry, dur, color) in enumerate(rings):
        path = f"M {-rx} 0 A {rx} {ry} 0 1 1 {rx} 0 A {rx} {ry} 0 1 1 {-rx} 0"
        out.append(
            f'<g transform="rotate({tilt})">'
            f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke="#FFFFFF" stroke-opacity=".1" stroke-width="1.2"/>'
            f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke="url(#ring{i})" stroke-width="2"/>'
            f'<circle r="5" fill="{color}" filter="url(#glow)">'
            f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/></circle>'
            f'<circle r="3" fill="#FFFFFF" opacity=".8">'
            f'<animateMotion dur="{dur * 1.7:.1f}s" begin="-{dur / 2}s" repeatCount="indefinite" path="{path}" keyPoints="1;0" keyTimes="0;1" calcMode="linear"/></circle>'
            f"</g>"
        )
    out.append(
        '<circle r="64" fill="url(#core)"/>'
        '<circle r="64" fill="url(#coreShine)"/>'
        f'<text y="11" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="#FFFFFF" letter-spacing="1">MN</text>'
        "</g>"
    )
    return "".join(out)


def build_hero():
    W, H = 1280, 480
    ring_defs = "".join(
        f'<linearGradient id="ring{i}" x1="0" x2="1"><stop offset="0" stop-color="{c}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{c}" stop-opacity=".9"/><stop offset="1" stop-color="{c}" stop-opacity=".05"/></linearGradient>'
        for i, c in enumerate([BLUE_L, VIOLET, ROSE])
    )
    defs = (
        "<defs>"
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>'
        '<filter id="aurora" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="72"/></filter>'
        '<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#FFFFFF" fill-opacity=".09"/></pattern>'
        '<radialGradient id="dotFade" cx="30%" cy="40%" r="80%"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
        f'<mask id="dotMask"><rect width="{W}" height="{H}" fill="url(#dotFade)"/></mask>'
        '<linearGradient id="nameGrad" gradientUnits="userSpaceOnUse" x1="64" y1="0" x2="520" y2="0" spreadMethod="reflect">'
        f'<stop offset="0" stop-color="{BLUE_L}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{ROSE}"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" values="0 0;456 0;0 0" dur="9s" repeatCount="indefinite"/>'
        "</linearGradient>"
        f'<radialGradient id="core" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#B8CBFF"/><stop offset=".35" stop-color="{BLUE}"/>'
        '<stop offset="1" stop-color="#0A1238"/></radialGradient>'
        '<radialGradient id="coreShine" cx="30%" cy="22%" r="35%"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/>'
        '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="coreGlow"><stop offset="0" stop-color="{BLUE}" stop-opacity=".45"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f"{ring_defs}"
        "</defs>"
    )
    style = (
        ".a{transform-box:fill-box;transform-origin:center;animation:drift 16s ease-in-out infinite alternate}"
        ".a2{animation-duration:21s;animation-delay:-7s}.a3{animation-duration:26s;animation-delay:-13s}"
        "@keyframes drift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(-90px,50px) scale(1.18)}100%{transform:translate(60px,-30px) scale(.92)}}"
        ".pulse{animation:pulse 1.8s ease-in-out infinite}@keyframes pulse{50%{opacity:.25}}"
        ".caret{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        ".rise{animation:rise .9s cubic-bezier(.2,.7,.2,1) backwards}"
        ".d1{animation-delay:.1s}.d2{animation-delay:.25s}.d3{animation-delay:.4s}.d4{animation-delay:.55s}"
        "@keyframes rise{from{opacity:0;transform:translateY(18px)}}"
    )

    status = "AVAILABLE FOR NEW PROJECTS"
    status_w = mono_len(status, 14, 2)
    ticker_words = ["NEXT.JS", "REACT", "TYPESCRIPT", "NESTJS", "BUN", "HONO", "ELYSIA", "NODE.JS", "PYTORCH",
                    "OPENCV", "POSTGRESQL", "REDIS", "KAFKA", "DOCKER", "KUBERNETES", "THREE.JS", "GSAP", "TAILWIND"]
    ticker = "".join(f"{w}   ✦   " for w in ticker_words)
    tick_len = mono_len(ticker, 15, 2)
    meta = "◉ TEHRAN, IRAN   /   17 PRODUCTS SHIPPED   /   FREELANCE SINCE 2023"

    body = (
        defs
        + '<g clip-path="url(#frame)">'
        + f'<rect width="{W}" height="{H}" fill="{BG}"/>'
        + '<g filter="url(#aurora)" opacity=".62">'
        + f'<circle class="a" cx="990" cy="130" r="210" fill="{BLUE}"/>'
        + f'<circle class="a a2" cx="1190" cy="390" r="170" fill="{VIOLET}"/>'
        + f'<circle class="a a3" cx="720" cy="470" r="150" fill="{ROSE}" fill-opacity=".55"/>'
        + "</g>"
        + f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotMask)"/>'
        + orbit(1010, 200)
        + f'<text x="1010" y="392" text-anchor="middle" font-family="{FA}" font-size="26" font-weight="700" fill="{SILVER}" fill-opacity=".75">محمد نخعی</text>'
        # status pill
        + f'<g class="rise">'
          f'<rect x="64" y="46" width="{status_w + 66:.1f}" height="36" rx="18" fill="#FFFFFF" fill-opacity=".05" stroke="#FFFFFF" stroke-opacity=".14"/>'
          f'<circle cx="86" cy="64" r="9" fill="{EMERALD}" fill-opacity=".25" class="pulse"/>'
          f'<circle cx="86" cy="64" r="4.5" fill="{EMERALD}"/>'
          + mono(status, 104, 69, 14, SILVER, 2)
        + "</g>"
        # name
        + f'<g class="rise d1"><text x="60" y="176" font-family="{SANS}" font-size="94" font-weight="800" fill="{TEXT}" letter-spacing="-3">Mohammad</text></g>'
        + f'<g class="rise d2"><text x="60" y="268" font-family="{SANS}" font-size="94" font-weight="800" fill="url(#nameGrad)" letter-spacing="-3">Nakhaei<tspan fill="{BLUE_L}">.</tspan></text></g>'
        # role line
        + f'<g class="rise d3">'
        + mono("~$", 64, 330, 26, BLUE_L)
        + typing_line(["full-stack developer", "AI engineer", "Next.js × NestJS × PyTorch", "I turn impossible ideas into products"],
                      64 + mono_len("~$ ", 26), 330, 26)
        + "</g>"
        + f'<g class="rise d4">' + mono(meta, 64, 388, 15, MUTED, 1) + "</g>"
        # ticker
        + f'<rect y="424" width="{W}" height="56" fill="#000000" fill-opacity=".35"/>'
        + f'<line x1="0" x2="{W}" y1="424.5" y2="424.5" stroke="#FFFFFF" stroke-opacity=".1"/>'
        + f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{-tick_len} 0" dur="48s" repeatCount="indefinite"/>'
        + mono(ticker, 0, 458, 15, DIM, 2)
        + mono(ticker, tick_len, 458, 15, DIM, 2)
        + "</g>"
        + "</g>"
        + border(W, H)
    )
    write(ASSETS / "hero.svg", svg(W, H, body, "Mohammad Nakhaei — full-stack developer and AI engineer in Tehran, available for new projects", style))


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------
ICONS = {
    "globe": lambda c: (f'<circle cx="0" cy="0" r="9" fill="none" stroke="{c}" stroke-width="1.8"/>'
                        f'<ellipse rx="4" ry="9" fill="none" stroke="{c}" stroke-width="1.6"/>'
                        f'<path d="M-9 0H9M-7.5 -4.5H7.5M-7.5 4.5H7.5" stroke="{c}" stroke-width="1.4"/>'),
    "linkedin": lambda c: ('<rect x="-10" y="-10" width="20" height="20" rx="4.5" fill="#0A66C2"/>'
                           f'<text y="5.2" text-anchor="middle" font-family="{SANS}" font-size="13.5" font-weight="800" fill="#FFFFFF">in</text>'),
    "telegram": lambda c: ('<circle r="10.5" fill="#229ED9"/>'
                           '<path d="M-5.6 -0.4 5.2 -4.8c.5-.2 1 .2.8.8L4.3 4.6c-.1.6-.7.8-1.2.5L-0.1 2.8l-1.7 1.6c-.2.2-.6.1-.6-.2l.2-2.6 5-4.6c.2-.2-.1-.4-.3-.2L-3.7 1-6 .3c-.5-.2-.5-.6.4-.7z" fill="#FFFFFF"/>'),
    "mail": lambda c: (f'<rect x="-10" y="-7.5" width="20" height="15" rx="3" fill="none" stroke="{c}" stroke-width="1.8"/>'
                       f'<path d="M-9 -5.5 0 1.5 9 -5.5" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>'),
    "doc": lambda c: (f'<path d="M-7 -10H3L8 -5V10H-7Z" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>'
                      f'<path d="M3 -10V-5H8M-3.5 0H4.5M-3.5 4.5H4.5" fill="none" stroke="{c}" stroke-width="1.6"/>'),
}


def build_buttons():
    for slug, label, icon in BUTTONS:
        size = 18
        text_w = len(label) * size * 0.56
        W, H = round(text_w + 98), 52
        body = (
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="26" fill="{SURFACE}" stroke="{BORDER}"/>'
            f'<g transform="translate(32 26)">{ICONS[icon](BLUE_L)}</g>'
            f'<text x="56" y="32.5" font-family="{SANS}" font-size="{size}" font-weight="600" fill="{TEXT}">{escape(label)}</text>'
            f'<path d="M{W - 26} 21l5 5-5 5" fill="none" stroke="{DIM}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        write(ASSETS / "buttons" / f"{slug}.svg", svg(W, H, body, label))


# ---------------------------------------------------------------------------
# Section headers (light and dark variants — they sit on GitHub's own background)
# ---------------------------------------------------------------------------
def build_sections():
    W, H = 1280, 140
    for key, (num, tag, title) in SECTIONS.items():
        for theme, fg, line, sub in (("dark", TEXT, BORDER, DIM), ("light", "#09090B", "#E4E4E7", "#71717A")):
            body = (
                mono(num, 2, 34, 18, BLUE_L if theme == "dark" else BLUE, 3, 'font-weight="700"')
                + mono(f"/  {tag}", 2 + mono_len(num + "  ", 18, 3), 34, 18, sub, 3)
                + f'<text x="0" y="98" font-family="{SANS}" font-size="54" font-weight="800" fill="{fg}" letter-spacing="-1.5">{escape(title)}</text>'
                + f'<rect y="128" width="{W}" height="1.5" fill="{line}"/>'
                + sweep(W, 128.75, BLUE_L if theme == "dark" else BLUE, dur=6, height=2.5, length=320)
            )
            write(ASSETS / "sections" / f"{key}-{theme}.svg", svg(W, H, body, f"{num} — {title}"))


# ---------------------------------------------------------------------------
# about.ts
# ---------------------------------------------------------------------------
def build_about():
    k, v, s, p, c, n = BLUE_L, TEXT, "#34D399", DIM, FAINT, VIOLET  # key, plain, string, punct, comment, keyword
    lines = [
        [("const ", n), ("mohammad", v), (" = {", p)],
        [("  role", k), (": ", p), ('"full-stack developer & AI engineer"', s), (",", p)],
        [("  basedIn", k), (": ", p), ('"Tehran, Iran"', s), (",", p)],
        [("  building", k), (": [", p), ('"Next.js"', s), (", ", p), ('"Bun"', s), (", ", p), ('"NestJS"', s),
         (", ", p), ('"Hono"', s), (", ", p), ('"Elysia"', s), ("],", p)],
        [("  training", k), (": [", p), ('"PyTorch"', s), (", ", p), ('"computer vision"', s), (", ", p), ('"NLP"', s), ("],", p)],
        [("  askMeAbout", k), (": ", p), ('"algorithms"', s), (",", p)],
        [("  lookingFor", k), (": ", p), ('"collaborators with impossible ideas"', s), (",", p)],
        [("  offline", k), (": ", p), ('"classical music"', s), (",", p)],
        [("  pronouns", k), (": ", p), ('"he/him"', s), (",", p)],
        [("} ", p), ("as const", n), (";", p)],
        [],
        [("// now: shipping the next product — say hi ↓", c)],
    ]
    W, size, lh, top = 1280, 24, 40, 112
    H = top + lh * len(lines) + 30
    style = (".ln{animation:ln .55s cubic-bezier(.2,.7,.2,1) backwards}"
             "@keyframes ln{from{opacity:0;transform:translateX(-14px)}}"
             ".caret{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}")
    code = []
    for i, tokens in enumerate(lines):
        y = top + i * lh
        code.append(mono(f"{i + 1:>2}", 36, y, 18, FAINT))
        x = 96
        spans = []
        for text, color in tokens:
            spans.append(mono(text, round(x, 2), y, size, color))
            x += mono_len(text, size)
        code.append(f'<g class="ln" style="animation-delay:{0.3 + i * 0.09:.2f}s">{"".join(spans)}</g>')
        if i == len(lines) - 1:
            code.append(f'<rect class="caret" x="{x + 6:.1f}" y="{y - 20}" width="12" height="26" rx="2" fill="{BLUE_L}"/>')
    dots = "".join(f'<circle cx="{36 + i * 24}" cy="34" r="7" fill="{c}"/>' for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]))
    body = (
        panel(W, H, 24)
        + '<g clip-path="url(#frame)">'
        + f'<rect width="{W}" height="68" fill="{SURFACE}"/><rect y="67" width="{W}" height="1" fill="{BORDER}"/>'
        + dots
        + mono("about.ts", W / 2 - mono_len("about.ts", 16) / 2, 40, 16, MUTED)
        + mono("TYPESCRIPT", W - 36 - mono_len("TYPESCRIPT", 13, 2), 39, 13, FAINT, 2)
        + "".join(code)
        + sweep(W, 67.5, BLUE_L, dur=8, height=2, length=300)
        + "</g>"
        + border(W, H, 24)
    )
    write(ASSETS / "about.svg", svg(W, H, body, "about.ts — full-stack developer and AI engineer in Tehran; builds with Next.js, Bun, NestJS, Hono and Elysia; trains PyTorch models; ask me about algorithms; loves classical music", style))


def build_stats():
    W, H, gap = 1280, 210, 20
    tw = (W - gap * 3) / 4
    style = ".t{animation:pop .8s cubic-bezier(.2,.7,.2,1) backwards}@keyframes pop{from{opacity:0;transform:translateY(16px)}}"
    tiles = []
    for i, (big, l1, l2, color) in enumerate(STATS):
        x = i * (tw + gap)
        tiles.append(
            f'<g class="t" style="animation-delay:{0.15 * i:.2f}s">'
            f'<rect x="{x + .5:.1f}" y=".5" width="{tw - 1:.1f}" height="{H - 1}" rx="22" fill="{SURFACE}" stroke="{BORDER}"/>'
            f'<rect x="{x + 28:.1f}" y="0" width="56" height="3" rx="1.5" fill="{color}"/>'
            f'<text x="{x + 28:.1f}" y="104" font-family="{SANS}" font-size="72" font-weight="800" fill="{TEXT}" letter-spacing="-2">{escape(big)}</text>'
            f'<text x="{x + 28:.1f}" y="148" font-family="{SANS}" font-size="21" font-weight="600" fill="{MUTED}">{escape(l1)}</text>'
            f'<text x="{x + 28:.1f}" y="176" font-family="{SANS}" font-size="21" fill="{DIM}">{escape(l2)}</text>'
            f'<circle cx="{x + tw - 32:.1f}" cy="36" r="5" fill="{color}"><animate attributeName="opacity" values="1;.25;1" dur="{2 + i * .4:.1f}s" repeatCount="indefinite"/></circle>'
            "</g>"
        )
    write(ASSETS / "stats.svg", svg(W, H, "".join(tiles), "17 products live in production · 3+ years shipping for clients · 59% of my code is TypeScript · classical music on repeat", style))


# ---------------------------------------------------------------------------
# Project cards
# ---------------------------------------------------------------------------
def build_cards():
    W, H, IH = 600, 480, 290
    style = (".pulse{animation:pulse 1.8s ease-in-out infinite}@keyframes pulse{50%{opacity:.2}}"
             ".kb{transform-origin:300px 145px;animation:kb 18s ease-in-out infinite alternate}"
             "@keyframes kb{to{transform:scale(1.06)}}")
    for p in PROJECTS:
        img = base64.b64encode((SHOTS / f"{p['slug']}.jpg").read_bytes()).decode()
        a = p["accent"]
        domain = p["url"].split("://", 1)[1] + " ↗"
        chips, cx = [], 28
        for tag in p["tags"]:
            w = mono_len(tag, 14) + 22
            chips.append(f'<rect x="{cx:.1f}" y="424" width="{w:.1f}" height="30" rx="9" fill="{RAISED}" stroke="{BORDER}"/>'
                         + mono(tag, round(cx + 11, 1), 444, 14, MUTED))
            cx += w + 8
        desc = wrap(p["blurb"], 50)[:2]
        kind_w = mono_len(p["kind"], 12, 1.5)
        body = (
            "<defs>"
            f'<clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>'
            f'<clipPath id="shot"><rect width="{W}" height="{IH}"/></clipPath>'
            f'<linearGradient id="fadeImg" x1="0" y1="0" x2="0" y2="1"><stop offset=".45" stop-color="{SURFACE}" stop-opacity="0"/><stop offset="1" stop-color="{SURFACE}"/></linearGradient>'
            f'<radialGradient id="tint" cx="85%" cy="100%" r="70%"><stop offset="0" stop-color="{a}" stop-opacity=".22"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
            "</defs>"
            '<g clip-path="url(#card)">'
            f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>'
            f'<g clip-path="url(#shot)"><image class="kb" href="data:image/jpeg;base64,{img}" width="{W}" height="{IH}" preserveAspectRatio="xMidYMin slice"/></g>'
            f'<rect y="{IH - 120}" width="{W}" height="120" fill="url(#fadeImg)"/>'
            f'<rect y="{IH}" width="{W}" height="{H - IH}" fill="url(#tint)"/>'
            # badges
            f'<rect x="20" y="20" width="84" height="30" rx="15" fill="{BG}" fill-opacity=".82" stroke="#FFFFFF" stroke-opacity=".16"/>'
            f'<circle cx="38" cy="35" r="7" fill="{EMERALD}" fill-opacity=".3" class="pulse"/><circle cx="38" cy="35" r="3.5" fill="{EMERALD}"/>'
            + mono("LIVE", 52, 40, 13, TEXT, 2, 'font-weight="700"')
            + f'<rect x="112" y="20" width="{kind_w + 28:.1f}" height="30" rx="15" fill="{BG}" fill-opacity=".82" stroke="#FFFFFF" stroke-opacity=".16"/>'
            + mono(p["kind"], 126, 39.5, 12, a, 1.5)
            # accent hairline with a travelling glint
            + f'<rect y="{IH - 1}" width="{W}" height="1.5" fill="{a}" fill-opacity=".35"/>'
            + sweep(W, IH - 0.25, a, dur=5.5, height=2.5, length=220)
            # text
            + f'<text x="28" y="{IH + 50}" font-family="{SANS}" font-size="31" font-weight="800" fill="{TEXT}" letter-spacing="-.6">{escape(p["title"])}</text>'
            + "".join(f'<text x="28" y="{IH + 86 + i * 27}" font-family="{SANS}" font-size="19" fill="{MUTED}">{escape(line)}</text>' for i, line in enumerate(desc))
            + "".join(chips)
            + mono(domain, W - 28 - mono_len(domain, 15), 444, 15, a)
            + "</g>"
            + f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="#FFFFFF" stroke-opacity=".1"/>'
        )
        label = f"{p['title']} — {p['blurb']} Live at {p['url']}"
        write(ASSETS / "projects" / f"{p['slug']}.svg", svg(W, H, body, label, style))


# ---------------------------------------------------------------------------
# Language mix
# ---------------------------------------------------------------------------
def build_languages():
    W, H = 1280, 250
    x0, bw, by = 40, 1200, 104
    style = (".seg{transform-box:fill-box;transform-origin:left;animation:grow 1.1s cubic-bezier(.2,.7,.2,1) backwards}"
             "@keyframes grow{from{transform:scaleX(0)}}")
    segs, legend, x = [], [], x0
    for i, (name, pct, color) in enumerate(LANGUAGES):
        w = bw * pct / 100
        segs.append(f'<rect class="seg" style="animation-delay:{0.08 * i:.2f}s" x="{x:.1f}" y="{by}" width="{max(w - 3, 1):.1f}" height="16" rx="3" fill="{color}"/>')
        x += w
        col, row = i % 4, i // 4
        lx, ly = x0 + col * 300, 176 + row * 42
        legend.append(f'<circle cx="{lx + 7}" cy="{ly - 6}" r="7" fill="{color}"/>'
                      f'<text x="{lx + 24}" y="{ly}" font-family="{SANS}" font-size="20" font-weight="600" fill="{TEXT}">{escape(name)}</text>'
                      + mono(f"{pct:.1f}%", lx + 24 + len(name) * 11.4 + 10, ly, 17, DIM))
    body = (
        panel(W, H, 24) + '<g clip-path="url(#frame)">'
        + mono("LANGUAGE MIX", 40, 54, 15, BLUE_L, 3, 'font-weight="700"')
        + mono("·  BYTES ACROSS ALL MY REPOSITORIES", 40 + mono_len("LANGUAGE MIX  ", 15, 3), 54, 15, DIM, 3)
        + f'<rect x="{x0}" y="{by}" width="{bw}" height="16" rx="8" fill="{RAISED}"/>'
        + "".join(segs) + "".join(legend)
        + "</g>" + border(W, H, 24)
    )
    summary = ", ".join(f"{n} {p}%" for n, p, _ in LANGUAGES)
    write(ASSETS / "languages.svg", svg(W, H, body, f"Language mix: {summary}", style))


# ---------------------------------------------------------------------------
# Journey
# ---------------------------------------------------------------------------
def build_journey():
    W, row, top = 1280, 124, 74
    H = top + row * len(JOURNEY) - 10
    nx = 72
    first, last = top + 18, top + 18 + row * (len(JOURNEY) - 1)
    style = (".draw{stroke-dasharray:1000;animation:draw 2.4s cubic-bezier(.4,0,.2,1) backwards}"
             "@keyframes draw{from{stroke-dashoffset:1000}}"
             ".in{animation:in .7s cubic-bezier(.2,.7,.2,1) backwards}@keyframes in{from{opacity:0;transform:translateX(16px)}}"
             ".pulse{animation:pulse 1.8s ease-in-out infinite}@keyframes pulse{50%{opacity:.15}}")
    items = []
    for i, (when, title, role, desc) in enumerate(JOURNEY):
        y = top + i * row
        now = i == len(JOURNEY) - 1
        color = EMERALD if now else BLUE_L
        node = (f'<circle cx="{nx}" cy="{y + 18}" r="16" fill="{color}" fill-opacity=".18" class="pulse"/>' if now else "") + \
               f'<circle cx="{nx}" cy="{y + 18}" r="8" fill="{BG}" stroke="{color}" stroke-width="3"/>'
        items.append(
            node
            + f'<g class="in" style="animation-delay:{0.35 + i * 0.28:.2f}s">'
            + mono(when, 120, y + 24, 15, color, 2, 'font-weight="700"')
            + f'<text x="{120 + mono_len(when, 15, 2) + 22:.1f}" y="{y + 24}" font-family="{SANS}" font-size="15" fill="{FAINT}">●</text>'
            + f'<text x="{120 + mono_len(when, 15, 2) + 44:.1f}" y="{y + 24}" font-family="{SANS}" font-size="18" font-weight="600" fill="{MUTED}">{escape(role)}</text>'
            + f'<text x="120" y="{y + 62}" font-family="{SANS}" font-size="28" font-weight="800" fill="{TEXT}" letter-spacing="-.5">{escape(title)}</text>'
            + f'<text x="120" y="{y + 92}" font-family="{SANS}" font-size="19" fill="{DIM}">{escape(desc)}</text>'
            + "</g>"
        )
    body = (
        panel(W, H, 24) + '<g clip-path="url(#frame)">'
        + f'<line x1="{nx}" x2="{nx}" y1="{first}" y2="{last}" stroke="{BORDER}" stroke-width="2"/>'
        + f'<line class="draw" x1="{nx}" x2="{nx}" y1="{first}" y2="{last}" stroke="{BLUE_L}" stroke-width="2" stroke-opacity=".7"/>'
        + "".join(items)
        + "</g>" + border(W, H, 24)
    )
    summary = "; ".join(f"{w}: {t} ({r})" for w, t, r, _ in JOURNEY)
    write(ASSETS / "journey.svg", svg(W, H, body, f"Journey — {summary}", style))


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def build_footer():
    W, H = 1280, 320

    def wave(amp, period, y, phase):
        pts = []
        for i in range(0, W * 2 + period + 1, 20):
            pts.append(f"{i},{y + amp * math.sin((i / period) * 2 * math.pi + phase):.1f}")
        return "M" + " L".join(pts)

    waves = ""
    for i, (amp, period, y, color, dur, op) in enumerate([
        (18, 320, 236, BLUE_L, 14, .55), (12, 260, 250, VIOLET, 18, .45), (22, 400, 262, ROSE, 24, .3)]):
        waves += (f'<path d="{wave(amp, period, y, i)}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="2">'
                  f'<animateTransform attributeName="transform" type="translate" values="0 0;{-period * (W // period + 1)} 0" '
                  f'dur="{dur}s" repeatCount="indefinite"/></path>')
    tagline = "OPEN TO FREELANCE WORK & COLLABORATIONS   ·   TEHRAN, IRAN (UTC+3:30)"
    body = (
        panel(W, H) + "<defs>"
        '<linearGradient id="imp" gradientUnits="userSpaceOnUse" x1="640" x2="1010" spreadMethod="reflect">'
        f'<stop offset="0" stop-color="{BLUE_L}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{ROSE}"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" values="0 0;370 0;0 0" dur="8s" repeatCount="indefinite"/>'
        "</linearGradient>"
        f'<radialGradient id="spot" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="{BLUE}" stop-opacity=".28"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        "</defs>"
        + '<g clip-path="url(#frame)">'
        + f'<rect width="{W}" height="{H}" fill="url(#spot)"/>'
        + waves
        + f'<text x="{W / 2}" y="118" text-anchor="middle" font-family="{SANS}" font-size="58" font-weight="800" fill="{TEXT}" letter-spacing="-2">'
          f'Let’s build something <tspan fill="url(#imp)">impossible.</tspan></text>'
        + mono(tagline, W / 2 - mono_len(tagline, 15, 1.5) / 2, 168, 15, MUTED, 1.5)
        + "</g>" + border(W, H)
    )
    write(ASSETS / "footer.svg", svg(W, H, body, "Let’s build something impossible. Open to freelance work and collaborations — Tehran, Iran.",))


if __name__ == "__main__":
    build_hero()
    build_buttons()
    build_sections()
    build_about()
    build_stats()
    build_cards()
    build_languages()
    build_journey()
    build_footer()
