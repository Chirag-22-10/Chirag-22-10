"""Build the README's images, each in a light and a dark variant.

hero      the top banner in two columns. Left: the name stacked in condensed caps (with a rare
          glitch), a red role tag, a typed tagline and three headline numbers. Right: a terminal
          that types `cat whoami.json` and prints it.
btn-*     link buttons for LinkedIn, email and repositories.
h-*       section headers: a red index kicker, a hairline and the title in display caps.
fig*      line drawings of the work (see bp.py); loadout is the tool pack (see loadout.py).

2D only: inline SVG with subset fonts embedded and CSS/SMIL animation. Nothing is fetched at view time.

    npm install && pip install -r requirements.txt && python3 build.py   # writes ../*.svg
"""
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from common import MONO_ADV, PALETTES, Fonts, chamfer, pts, svg_doc, text_width

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- hero
KICKER = "ANDROID · KOTLIN · ON-DEVICE ML"
ROLE = "ANDROID ENGINEER"
TAGLINES = [  # typed, held, deleted, next; loops forever
    "field apps that work offline and never lose a reading",
    "ml models on the phone, the api as a backup",
    "kotlin + compose, from the camera to the server",
    "talking to smart meters over bluetooth",
    "write it once with kotlin multiplatform",
]
TAGLINE = TAGLINES[0]
STATS = [  # number, two label lines, in red
    ("6", ("ANDROID APPS", "BUILT AT SUJANIX"), False),
    ("11", ("ONNX MODELS", "RUNNING ON-DEVICE"), True),
    ("124", ("COMMITS TO TRUEREAD", "AUG → NOV 2026"), False),
]
WHOAMI = """{
  "base": "Bengaluru, India",
  "now": "TrueRead field apps @ Sujanix",
  "stack": ["kotlin", "compose", "onnx"],
  "rules": {
    "offline": "room outbox",
    "models": "aes-gcm, sha-256",
    "fallback": "local -> api"
  },
  "open_to_android_roles": true
}"""
TOKEN = re.compile(r'("(?:[^"\\]|\\.)*")(\s*:)?|(true|false|null)|([{}\[\],:])|( +)')


def json_tspans(line, P, fonts):
    """One line of JSON as tspans: keys red, strings light, punctuation grey, booleans red."""
    out = []
    for m in TOKEN.finditer(line):
        st, colon, kw, punct, _space = m.groups()
        if st is not None:
            spans = [(st, P["term_red"] if colon else P["term_ink"])] + ([(colon.strip(), P["term_muted"])] if colon else [])
        elif kw is not None:
            spans = [(kw, P["term_red"])]
        elif punct is not None:
            spans = [(punct, P["term_muted"])]
        else:
            spans = [(" ", None)]
        for text, col in spans:
            fonts.use("mono", text)
            out.append(" " if col is None else f'<tspan fill="{col}">{escape(text)}</tspan>')
    return "".join(out)


def hero(theme):
    P = PALETTES[theme]
    W, H = 900, 426
    fonts = Fonts()
    defs, css, body = [], [], []
    css.append(
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
        "@keyframes slide{from{opacity:0;transform:translateX(-16px)}to{opacity:1;transform:none}}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        "@keyframes blink{0%{opacity:1}50%{opacity:0}}"
    )
    count = [0]

    def intro(kind, delay, dur=0.5):
        count[0] += 1
        c = f"i{count[0]}"
        css.append(f".{c}{{animation:{kind} {dur}s cubic-bezier(.2,.8,.2,1) {delay}s both}}")
        return c

    # ---- left column: who, and the three numbers that matter
    x0, col_w = 2, 486
    fonts.use("mono", KICKER)
    body.append(f'<g class="{intro("fade", .05)}"><rect x="{x0}" y="13" width="8" height="8" fill="{P["red"]}"/>'
                f'<text x="{x0 + 16}" y="21" class="mono" font-size="11" fill="{P["muted"]}" letter-spacing="1.6">{escape(KICKER)}</text></g>')

    size, lead = 118, 8
    cap = 0.8 * size
    y1 = 36 + cap
    y2 = y1 + lead + cap
    fonts.use("d9", "CHIRAGKUMAR.")
    assert text_width("d9", "CHIRAG", size, 1) < col_w, "name too wide"
    w_last = text_width("d9", "KUMAR", size, 1)

    def name(cls, fill, clip=""):
        return (f'<g class="{cls}"{clip}><text x="{x0 - 5}" y="{y1:.1f}" class="d9" font-size="{size}" fill="{fill}" letter-spacing="1">CHIRAG</text>'
                f'<text x="{x0 - 5}" y="{y2:.1f}" class="d9" font-size="{size}" fill="{fill}" letter-spacing="1">KUMAR</text></g>')

    # a rare glitch: two slices jump sideways for a quarter of a second
    defs.append(
        f'<clipPath id="ga"><rect x="0" y="{y1 - cap * 0.66:.1f}" width="{col_w}" height="{cap * 0.2:.1f}"/>'
        f'<rect x="0" y="{y2 - cap * 0.3:.1f}" width="{col_w}" height="{cap * 0.14:.1f}"/></clipPath>'
        f'<clipPath id="gb"><rect x="0" y="{y1 - cap * 0.3:.1f}" width="{col_w}" height="{cap * 0.12:.1f}"/>'
        f'<rect x="0" y="{y2 - cap * 0.78:.1f}" width="{col_w}" height="{cap * 0.18:.1f}"/></clipPath>'
    )
    css.append(
        ".ga,.gb{opacity:0}"
        ".ga{animation:ga 7s steps(1) 2.4s infinite}.gb{animation:gb 7s steps(1) 2.4s infinite}.gm{animation:gm 7s steps(1) 2.4s infinite}"
        "@keyframes ga{0%,90%{opacity:0;transform:none}90.5%{opacity:1;transform:translate(-7px,0)}92%{opacity:1;transform:translate(5px,0)}"
        "93.5%,100%{opacity:0;transform:none}}"
        "@keyframes gb{0%,90%{opacity:0;transform:none}90.5%{opacity:1;transform:translate(6px,0)}92%{opacity:1;transform:translate(-4px,0)}"
        "93.5%,100%{opacity:0;transform:none}}"
        "@keyframes gm{0%,90%{transform:none}90.5%{transform:translate(2px,0)}92%{transform:translate(-2px,0)}93.5%,100%{transform:none}}"
    )
    body.append(f'<g class="{intro("rise", .1, .6)}">'
                + name("ga", P["red"], ' clip-path="url(#ga)"') + name("gb", P["muted"], ' clip-path="url(#gb)"')
                + name("gm", P["ink"])
                + f'<text x="{x0 - 5 + w_last:.1f}" y="{y2:.1f}" class="d9" font-size="{size}" fill="{P["red"]}">.</text></g>')

    # role tag
    fonts.use("d8", ROLE)
    ts = 19
    tw = text_width("d8", ROLE, ts, 1.6) + 34
    ty = y2 + 20
    body.append(
        f'<g class="{intro("slide", .45)}"><path d="M{x0 + 10} {ty:.1f} H{x0 + tw:.1f} L{x0 + tw - 10:.1f} {ty + 30:.1f} H{x0} Z" fill="{P["red"]}"/>'
        f'<text x="{x0 + 17}" y="{ty + 21.5:.1f}" class="d8" font-size="{ts}" fill="{P["on_red"]}" letter-spacing="1.6">{ROLE}</text></g>'
    )

    # taglines: each one is typed, held, deleted, then the next; the cycle repeats forever
    st, yt = 14, ty + 58
    cw = MONO_ADV * st
    tx = x0 + 2 * cw
    fonts.use("mono", ">")
    type_dt, del_dt, hold, gap, begin = 0.045, 0.018, 2.4, 0.35, 1.0
    slots, t = [], 0.0
    for line in TAGLINES:
        assert tx + len(line) * cw < x0 + col_w, f"tagline too long: {line}"
        fonts.use("mono", line)
        slots.append((line, t))
        t += len(line) * type_dt + hold + len(line) * del_dt + gap
    cycle = t
    events = []  # (time, visible chars) for every step of every line

    def steps(line, t0):
        n, out = len(line), [(t0, 0)]
        out += [(t0 + (k + 1) * type_dt, k + 1) for k in range(n)]
        t1 = t0 + n * type_dt + hold
        out += [(t1 + (k + 1) * del_dt, n - k - 1) for k in range(n)]
        return out

    def anim(attr, frames, fmt):
        frames = sorted(frames)
        if frames[0][0] > 0:
            frames = [(0.0, frames[0][1] if False else 0)] + frames
        kt = ";".join(f"{min(f[0] / cycle, 1):.5f}" for f in frames)
        vals = ";".join(fmt(f[1]) for f in frames)
        return (f'<animate attributeName="{attr}" begin="{begin}s" dur="{cycle:.3f}s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="{kt}" values="{vals}"/>')

    body_t = [f'<text x="{x0}" y="{yt:.1f}" class="mono" font-size="{st}" fill="{P["red"]}">&gt;</text>']
    for li, (line, t0) in enumerate(slots):
        fr = steps(line, t0)
        events += fr
        defs.append(f'<clipPath id="tag{li}"><rect x="{tx:.1f}" y="{yt - st:.1f}" width="0" height="{st * 1.5:.1f}">'
                    + anim("width", fr, lambda c: f"{c * cw:.1f}") + '</rect></clipPath>')
        body_t.append(f'<text x="{tx:.1f}" y="{yt:.1f}" class="mono" font-size="{st}" fill="{P["ink2"]}" '
                      f'clip-path="url(#tag{li})">{escape(line)}</text>')
    body_t.append(f'<rect x="{tx:.1f}" y="{yt - st * 0.8:.1f}" width="{cw * 0.62:.1f}" height="{st:.1f}" fill="{P["red"]}" class="cur">'
                  + anim("x", events, lambda c: f"{tx + c * cw:.1f}") + '</rect>')
    body.append(f'<g class="{intro("fade", .8)}">{"".join(body_t)}</g>')
    css.append(".cur{animation:blink 1s steps(1) infinite}")

    # three numbers
    sy = yt + 64
    pitch = col_w / 3
    for i, (num, label, hot) in enumerate(STATS):
        x = x0 + i * pitch + (16 if i else 0)
        fonts.use("d9", num)
        g = [f'<text x="{x - 1:.1f}" y="{sy:.1f}" class="d9" font-size="46" fill="{P["red"] if hot else P["ink"]}" letter-spacing="1">{escape(num)}</text>']
        for k, ln in enumerate(label):
            fonts.use("mono", ln)
            assert text_width("mono", ln, 9.5, 1) < pitch - 20, ln
            g.append(f'<text x="{x:.1f}" y="{sy + 18 + 13 * k:.1f}" class="mono" font-size="9.5" fill="{P["muted"]}" letter-spacing="1">{escape(ln)}</text>')
        if i:
            g.append(f'<path d="M{x - 16:.1f} {sy - 36:.1f} V{sy + 34:.1f}" stroke="{P["faint"]}" stroke-width="1.2"/>')
        body.append(f'<g class="{intro("rise", 1.1 + .12 * i)}">{"".join(g)}</g>')
    assert sy + 36 < H, "stats run off the banner"

    # ---- right column: the terminal
    cx0, cy0, cwid, chei = 522, 6, 376, H - 10
    card = chamfer(cx0, cy0, cwid, chei, tr=20, bl=20)
    stroke = f' stroke="{P["term_line"]}" stroke-width="1.2"' if theme == "dark" else ""
    body.append(f'<g class="{intro("fade", .3, .6)}"><path d="M{pts(card)}Z" fill="{P["term"]}"{stroke}/>'
                f'<path d="M{cx0} {cy0} H{cx0 + 44}" stroke="{P["term_red"]}" stroke-width="3"/>')
    where = "~/chirag/whoami.json"
    fonts.use("mono", where)
    body.append(f'<text x="{cx0 + 18}" y="{cy0 + 26}" class="mono" font-size="11" fill="{P["term_muted"]}" letter-spacing=".6">{escape(where)}</text>')
    for k in range(3):
        col = P["term_red"] if k == 2 else P["term_muted"]
        body.append(f'<rect x="{cx0 + cwid - 66 + k * 13}" y="{cy0 + 17}" width="7" height="7" fill="{col}"/>')
    body.append(f'<path d="M{cx0 + 18} {cy0 + 40} H{cx0 + cwid - 18}" stroke="{P["term_muted"]}" stroke-opacity=".35" stroke-width="1"/></g>')

    size_j, lh = 12, 24
    cwj = MONO_ADV * size_j
    jx = cx0 + 18
    yp = cy0 + 70
    fonts.use("mono", "~ $ cat whoami.json")
    cmd = "cat whoami.json"
    cmd_x = jx + 4 * cwj
    c0, cdt = 0.7, 0.05
    ctotal = c0 + len(cmd) * cdt + 0.1
    ckeys = [0.0] + [(c0 + (i + 1) * cdt) / ctotal for i in range(len(cmd))]
    defs.append(
        f'<clipPath id="cmd"><rect x="{cmd_x:.1f}" y="{yp - size_j:.1f}" width="0" height="{size_j * 1.5:.1f}">'
        f'<animate attributeName="width" dur="{ctotal:.2f}s" fill="freeze" calcMode="discrete" '
        f'keyTimes="{";".join(f"{v:.4f}" for v in ckeys)}" values="{";".join(f"{i * cwj:.1f}" for i in range(len(cmd) + 1))}"/></rect></clipPath>'
    )

    def prompt(y, cls):
        return (f'<text x="{jx}" y="{y:.1f}" class="mono {cls}" font-size="{size_j}" fill="{P["term_muted"]}">~ '
                f'<tspan fill="{P["term_red"]}">$</tspan></text>')

    body.append(prompt(yp, intro("fade", .5)))
    body.append(f'<text x="{cmd_x:.1f}" y="{yp:.1f}" class="mono" font-size="{size_j}" fill="{P["term_ink"]}" clip-path="url(#cmd)">{cmd}</text>')
    lines = WHOAMI.split("\n")
    start = c0 + len(cmd) * cdt + 0.3
    for i, line in enumerate(lines):
        indent = len(line) - len(line.lstrip(" "))
        assert jx + len(line) * cwj < cx0 + cwid - 14, line
        y = yp + 28 + i * lh
        body.append(f'<text x="{jx + indent * cwj:.1f}" y="{y:.1f}" class="mono {intro("fade", start + i * .07, .25)}" '
                    f'font-size="{size_j}" xml:space="preserve">{json_tspans(line.lstrip(" "), P, fonts)}</text>')
    y_end = yp + 28 + len(lines) * lh + 8
    assert y_end < cy0 + chei - 14, "terminal overflows its card"
    t_end = start + len(lines) * .07 + .2
    body.append(prompt(y_end, intro("fade", t_end, .2)))
    body.append(f'<g class="{intro("fade", t_end, .2)}"><rect x="{jx + 4 * cwj:.1f}" y="{y_end - size_j * 0.8:.1f}" width="{cwj * 0.62:.1f}" '
                f'height="{size_j}" fill="{P["term_red"]}" class="cur"/></g>')

    style = fonts.css() + "".join(css)
    return svg_doc(
        W, H, "Chirag Kumar",
        f"Chirag Kumar, Android engineer: {KICKER.lower()}. Rotating taglines: {'; '.join(TAGLINES)}. 6 Android apps built at Sujanix; 11 ONNX models "
        "running on-device; 124 commits to TrueRead from August to November 2026. A terminal prints whoami.json: base Bengaluru, "
        "India; now TrueRead field apps at Sujanix; stack kotlin, compose, onnx; rules: offline room outbox, models aes-gcm and "
        "sha-256, fallback local to api; open to Android roles.",
        style, "".join(body), "".join(defs),
    )


# ---------------------------------------------------------------- link buttons
LINKS = {"linkedin": "LINKEDIN", "email": "EMAIL", "repos": "REPOS"}


def button(theme, label):
    P = PALETTES[theme]
    fonts = Fonts()
    fonts.use("d8", label)
    fonts.use("monob", "↗")
    W, H = round(text_width("d8", label, 15, 1.8) + 52), 34
    outline = chamfer(0.75, 0.75, W - 1.5, H - 1.5, tr=8, bl=8)
    body = (f'<path d="M{pts(outline)}Z" fill="none" stroke="{P["ink"]}" stroke-width="1.5"/>'
            f'<path d="M0.75 0.75 H16" stroke="{P["red"]}" stroke-width="3"/>'
            f'<text x="15" y="22.5" class="d8" font-size="15" fill="{P["ink"]}" letter-spacing="1.8">{label}</text>'
            f'<text x="{W - 24}" y="22" class="monob" font-size="13" fill="{P["red"]}">↗</text>')
    return svg_doc(W, H, label.title(), f"{label.title()} link", fonts.css(), body)


# ---------------------------------------------------------------- section headers
SECTIONS = {
    "work": ("01", "THE WORK", "SUJANIX // TRUEREAD FIELD APPS"),
    "hardware": ("02", "HARDWARE", "SMART METERS // DLMS OVER BLUETOOTH"),
    "quests": ("03", "SIDE QUESTS", "MULTIPLATFORM // OFFLINE-FIRST"),
    "loadout": ("04", "LOADOUT", "PRIMARY // SIDEARMS"),
    "career": ("05", "CAREER", "2026 → NOW"),
    "rules": ("06", "RULES OF ENGAGEMENT", "SEVEN, SO FAR"),
}


def header(theme, no, title, meta):
    P = PALETTES[theme]
    W, H = 900, 84
    fonts = Fonts()
    kick = f"// {no}"
    fonts.use("monob", kick)
    fonts.use("mono", meta)
    fonts.use("d9", title)
    kw = text_width("monob", kick, 12, 1.5)
    mw = text_width("mono", meta, 11, 1.4)
    x_line0, x_line1 = 2 + kw + 14, W - 2 - mw - 14
    body = [
        f'<text x="2" y="18" class="monob" font-size="12" fill="{P["red"]}" letter-spacing="1.5">{kick}</text>',
        f'<path d="M{x_line0:.1f} 14 H{x_line1:.1f}" pathLength="1" stroke="{P["faint"]}" stroke-width="1.2" class="ln"/>',
        f'<rect x="{x_line1 - 6:.1f}" y="11" width="6" height="6" fill="{P["red"]}" class="tip"/>',
        f'<text x="{W - 2}" y="18" class="mono" font-size="11" fill="{P["muted"]}" letter-spacing="1.4" text-anchor="end">{escape(meta)}</text>',
        f'<text x="0" y="74" class="d9 tt" font-size="50" fill="{P["ink"]}" letter-spacing="1.2">{escape(title)}</text>',
    ]
    css = (
        ".ln{stroke-dasharray:1 1;animation:draw .9s cubic-bezier(.4,0,.2,1) .1s both}"
        ".tip{animation:fade .3s ease-out .9s both}"
        ".tt{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
    )
    return svg_doc(W, H, f"{no} {title.title()}", f"Section {no}: {title.lower()}. {meta.lower()}.", fonts.css() + css, "".join(body))


def main():
    from bp import DRAWINGS
    from loadout import loadout
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [("hero", hero), ("loadout", loadout), *DRAWINGS.items()]
    jobs += [(f"h-{key}", (lambda k: lambda th: header(th, *SECTIONS[k]))(key)) for key in SECTIONS]
    jobs += [(f"btn-{key}", (lambda k: lambda th: button(th, LINKS[k]))(key)) for key in LINKS]
    total = 0
    for theme in ("light", "dark"):
        for name, fn in jobs:
            data = fn(theme)
            path = OUT / f"{name}-{theme}.svg"
            path.write_text(data)
            total += len(data)
            print(f"{path.name:26s} {len(data) / 1024:6.1f} KB")
    print(f"{'total':26s} {total / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
