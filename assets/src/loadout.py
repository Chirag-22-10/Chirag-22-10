"""Loadout: the tool pack in two tiers. PRIMARY is what the production work runs on; SIDEARMS is everything else,
grouped by category. Brand-coloured logos on neutral tiles with a cut corner, light and dark.

Logos come from Simple Icons (CC0) in their official colours. Tools Simple Icons does not carry
(Jetpack libraries, AWS services, Firebase products, Koin, SQL) get a monogram in a brand-style colour.
Any logo too faint against its tile is nudged darker (light theme) or lighter (dark theme).
"""
import json
import re
from functools import lru_cache
from xml.sax.saxutils import escape

from common import NM, PALETTES, Fonts, chamfer, pts, svg_doc, text_width

# (simple-icons slug | None, label[, colour, monogram])
PRIMARY = [("kotlin", "Kotlin"), ("jetpackcompose", "Compose"), ("android", "Android"),
           (None, "Coroutines", "#7F52FF", "co"), (None, "Hilt", "#3DDC84", "Hilt"), (None, "Room", "#3DDC84", "Room"),
           (None, "WorkManager", "#4285F4", "WM"), (None, "Retrofit", "#48B983", "Rf"), (None, "CameraX", "#4285F4", "CX"),
           ("onnx", "ONNX RT"), ("opencv", "OpenCV"), ("firebase", "Firebase")]

SIDEARMS = [  # each row holds one or two categories
    [("LANG", [("openjdk", "Java"), ("dart", "Dart"), ("python", "Python"), (None, "SQL", "#336791", "SQL")]),
     ("DATA", [("sqlite", "SQLite"), ("postgresql", "PostgreSQL"), (None, "DataStore", "#3DDC84", "DS"),
               (None, "SQLDelight", "#4B6FB5", "SQD")])],
    [("ANDROID", [("bluetooth", "Bluetooth"), (None, "AIDL", "#3DDC84", "IPC"), (None, "Keystore", "#3DDC84", "KS"),
                  ("tensorflow", "TFLite"), (None, "ML Kit", "#4285F4", "ML"), ("googlemaps", "Maps"),
                  ("materialdesign", "Material 3"), (None, "Gurux DLMS", "#0B6FB8", "DLMS")])],
    [("KMP", [("kotlin", "Kotlin MP"), ("jetpackcompose", "Compose MP"), ("ktor", "Ktor"), (None, "Koin", "#F18A00", "Ko"),
                        ("ios", "iOS"), ("webassembly", "Wasm"), ("flutter", "Flutter")])],
    [("CLOUD", [(None, "S3", "#3F8624", "S3"), (None, "DynamoDB", "#4053D6", "DDB"), (None, "Lambda", "#FF9900", "λ"),
                (None, "FCM", "#FFA000", "FCM"), (None, "Remote Cfg", "#FFA000", "RC"), (None, "Crashlytics", "#FFA000", "Cr"),
                ("fastapi", "FastAPI"), ("docker", "Docker")])],
    [("TOOLS", [("androidstudio", "Studio"), ("gradle", "Gradle"), ("git", "Git"), ("githubactions", "Actions"),
                ("postman", "Postman"), ("figma", "Figma"), ("googleplay", "Play"), ("jira", "Jira")])],
]


@lru_cache(None)
def simple_icon(slug):
    svg = (NM / "simple-icons/icons" / f"{slug}.svg").read_text()
    return re.search(r' d="([^"]+)"', svg).group(1)


@lru_cache(None)
def _brands():
    return json.loads((NM / "simple-icons/data/simple-icons.json").read_text())


def brand_hex(slug):
    for ic in _brands():
        if ic.get("slug") == slug or re.sub(r"[^a-z0-9]", "", ic["title"].lower()) == slug:
            return "#" + ic["hex"]
    raise KeyError(slug)


def _lum(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _mix(hex_, toward, t):
    c = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
    d = [int(toward[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(c, d))


def legible(color, bg, theme, minimum=None):
    """Keep the brand hue but make sure it reads on the tile."""
    target = "#000000" if theme == "light" else "#FFFFFF"
    minimum = minimum or (2.4 if theme == "light" else 3.4)
    t, out = 0.0, color
    while _contrast(out, bg) < minimum and t < 1:
        t += 0.05
        out = _mix(color, target, t)
    return out


def loadout(theme):
    P = PALETTES[theme]
    fonts = Fonts()
    W = 900
    css = [
        ".t{transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,1.4,.4,1) both}"
        "@keyframes pop{from{opacity:0;transform:translateY(6px) scale(.85)}to{opacity:1;transform:none}}"
        ".hd{animation:fade .5s ease-out both}@keyframes fade{from{opacity:0}to{opacity:1}}"
        ".shine{animation:shine 8s cubic-bezier(.6,0,.3,1) 2.5s infinite}"
        f"@keyframes shine{{0%{{transform:translateX(0)}}22%,100%{{transform:translateX({W + 320}px)}}}}"
    ]
    defs, body, clips, names = [], [], [], []

    def tier(y, title, note, delay):
        fonts.use("d9", title)
        fonts.use("mono", note)
        tw = text_width("d9", title, 22, 1.2)
        nx = 2 + tw + 12
        line0 = nx + text_width("mono", note, 10, 1) + 14
        body.append(f'<g class="hd" style="animation-delay:{delay:.2f}s">'
                    f'<text x="2" y="{y}" class="d9" font-size="22" fill="{P["ink"]}" letter-spacing="1.2">{title}</text>'
                    f'<text x="{nx:.1f}" y="{y - 1}" class="mono" font-size="10" fill="{P["muted"]}" letter-spacing="1">{escape(note)}</text>'
                    f'<path d="M{line0:.1f} {y - 5} H{W - 10}" stroke="{P["faint"]}" stroke-width="1.1"/>'
                    f'<rect x="{W - 8}" y="{y - 8}" width="6" height="6" fill="{P["red"]}"/></g>')

    def tile(x, y, size, item, logo, label_size, label_fill, delay, accent=False):
        slug, label = item[0], item[1]
        names.append(label)
        cut = round(size * 0.18)
        outline = chamfer(x, y, size, size, tr=cut)
        g = [f'<path d="M{pts(outline)}Z" fill="{P["tile"]}" stroke="{P["tile_line"]}" stroke-width="1.1"/>']
        if accent:
            g.append(f'<path d="M{x} {y} H{x + 14}" stroke="{P["red"]}" stroke-width="2.4"/>')
        if slug:
            col = legible(brand_hex(slug), P["tile"], theme)
            off = (size - logo) / 2
            g.append(f'<path transform="translate({x + off:.1f} {y + off:.1f}) scale({logo / 24:.4f})" d="{simple_icon(slug)}" fill="{col}"/>')
        else:
            col, mono = legible(item[2], P["tile"], theme), item[3]
            fs = logo * {1: 0.92, 2: 0.7, 3: 0.56, 4: 0.48}[len(mono)]
            fonts.use("monob", mono)
            g.append(f'<text x="{x + size / 2:.1f}" y="{y + size / 2 + fs * 0.36:.1f}" class="monob" font-size="{fs:.1f}" '
                     f'fill="{col}" text-anchor="middle">{escape(mono)}</text>')
        fonts.use("mono", label)
        g.append(f'<text x="{x + size / 2:.1f}" y="{y + size + label_size + 5:.1f}" class="mono" font-size="{label_size}" '
                 f'fill="{label_fill}" text-anchor="middle">{escape(label)}</text>')
        body.append(f'<g class="t" style="animation-delay:{delay:.2f}s">{"".join(g)}</g>')
        return outline

    # PRIMARY: one row of big tiles; a light sweep crosses them now and then
    y = 24
    tier(y, "PRIMARY", f"// {len(PRIMARY)} · the production stack", 0)
    size, pitch = 62, 74
    x0 = (W - (len(PRIMARY) - 1) * pitch - size) / 2
    y += 18
    for i, item in enumerate(PRIMARY):
        outline = tile(x0 + i * pitch, y, size, item, 30, 9.5, P["ink2"], 0.1 + i * 0.04, accent=True)
        clips.append(f'<path d="M{pts(outline)}Z"/>')
    y += size + 52

    # SIDEARMS: category rows of small tiles
    n_side = sum(len(items) for row in SIDEARMS for _, items in row)
    tier(y, "SIDEARMS", f"// {n_side} · everything else I reach for", 0.4)
    y += 22
    size, pitch, label_w, gap = 40, 60, 92, 44
    for r, row in enumerate(SIDEARMS):
        x = 2
        for cat, items in row:
            fonts.use("d8", cat)
            body.append(f'<text x="{x}" y="{y + size / 2 + 5}" class="d8 hd" font-size="14" fill="{P["muted"]}" letter-spacing="1.4" '
                        f'style="animation-delay:{0.5 + r * 0.08:.2f}s">{cat}</text>')
            for c, item in enumerate(items):
                assert text_width("mono", item[1], 8.4) < pitch - 4, item[1]
                tile(x + label_w + c * pitch, y, size, item, 21, 8.4, P["muted"], 0.55 + r * 0.08 + c * 0.03)
            x += label_w + (len(items) - 1) * pitch + size + gap
        assert x - gap <= W, f"sidearm row {r} overflows"
        y += size + 30
    H = int(y - 4)

    defs.append(f'<clipPath id="tiles">{"".join(clips)}</clipPath>')
    defs.append('<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="#fff" stop-opacity="{".6" if theme == "light" else ".12"}"/>'
                '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    body.append(f'<g clip-path="url(#tiles)"><g transform="skewX(-18)"><rect class="shine" x="-320" y="0" width="160" '
                f'height="{H}" fill="url(#sh)"/></g></g>')
    style = fonts.css() + "".join(css)
    return svg_doc(W, H, "loadout",
                   f"Primary: {', '.join(i[1] for i in PRIMARY)}. Sidearms: "
                   + "; ".join(f"{cat.lower()}: {', '.join(i[1] for i in items)}" for row in SIDEARMS for cat, items in row) + ".",
                   style, "".join(body), "".join(defs))
