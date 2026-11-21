"""Line drawings for the work (FIG 01-06): on-device reading, offline sync, model updates, DLMS over
Bluetooth, Room-Splits and FieldProof.

Every drawing sketches itself in over a faint dot grid: strokes draw on, labels fade
in, dimension lines appear. Then the loop starts: red pulses run along the wires and
nodes flash as data passes. Now and then a cyan or pink spark shows up, Jinx-style.
Panels and nodes have cut corners, labels are set in the display face (see common.py).
"""
import math
from xml.sax.saxutils import escape

from common import PALETTES, Fonts, chamfer, svg_doc, text_width

START = 2.8  # seconds: the drawing is finished, the loop begins
TOTAL_SHEETS = 6


# ---------------------------------------------------------------- geometry
def rounded(points, r=7.0, seg=6):
    """Orthogonal polyline with its corners rounded (quadratic, sampled)."""
    if len(points) < 3:
        return list(points)
    out = [points[0]]
    for i in range(1, len(points) - 1):
        p0, p1, p2 = points[i - 1], points[i], points[i + 1]
        l1 = math.dist(p0, p1)
        l2 = math.dist(p1, p2)
        rr = min(r, l1 / 2, l2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) / l1 * rr, p1[1] + (p0[1] - p1[1]) / l1 * rr)
        b = (p1[0] + (p2[0] - p1[0]) / l2 * rr, p1[1] + (p2[1] - p1[1]) / l2 * rr)
        for k in range(seg + 1):
            t = k / seg
            out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p1[0] + t * t * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p1[1] + t * t * b[1]))
    out.append(points[-1])
    return out


def plen(points):
    return sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))


def pathd(points):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)


def pct(x):
    return f"{max(0.0, min(100.0, x * 100)):.3f}%"


# ---------------------------------------------------------------- drawing engine
class Drawing:
    def __init__(self, theme, w, h, title, desc):
        self.theme, self.P = theme, PALETTES[theme]
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.fonts = Fonts()
        self.defs, self.css, self.body = [], [], []
        self.n = 0
        self.css.append(
            "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
            "@keyframes fade{from{opacity:0}to{opacity:1}}"
            ".dr{stroke-dasharray:1 1;stroke-dashoffset:0}"
        )

    def uid(self, p="e"):
        self.n += 1
        return f"{p}{self.n}"

    def add(self, s):
        self.body.append(s)

    # -- animation classes
    def c_draw(self, delay, dur):
        c = self.uid("d")
        self.css.append(f".{c}{{animation:draw {dur:.2f}s cubic-bezier(.4,0,.2,1) {delay:.2f}s both}}")
        return c

    def c_fade(self, delay, dur=0.45):
        c = self.uid("f")
        self.css.append(f".{c}{{animation:fade {dur:.2f}s ease-out {delay:.2f}s both}}")
        return c

    # -- primitives
    def path(self, points, delay=0.0, stroke=None, width=1.2, speed=650, dashed=None, opacity=None, fill="none"):
        """A stroke that draws itself on (or fades in, if dashed). Returns (d, length)."""
        stroke = stroke or self.P["ink"]
        d, L = pathd(points), plen(points)
        o = f' opacity="{opacity}"' if opacity is not None else ""
        if dashed:
            self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
                     f'stroke-dasharray="{dashed}" class="{self.c_fade(delay, .6)}"{o}/>')
        else:
            dur = max(0.25, min(1.1, L / speed))
            self.add(f'<path d="{d}" pathLength="1" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
                     f'stroke-linecap="round" stroke-linejoin="round" class="dr {self.c_draw(delay, dur)}"{o}/>')
        return d, L

    def text(self, x, y, s, size=10, fill=None, fam="mono", anchor="start", ls=0.0, delay=None, cls="", op=None):
        fill = fill or self.P["ink"]
        self.fonts.use(fam, s)
        classes = [fam] + ([self.c_fade(delay)] if delay is not None else []) + ([cls] if cls else [])
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        l = f' letter-spacing="{ls:g}"' if ls else ""
        o = f' opacity="{op}"' if op is not None else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{" ".join(classes)}" font-size="{size:g}" fill="{fill}"{a}{l}{o}>{escape(s)}</text>')

    def grid(self, x, y, w, h, step=16):
        gid = self.uid("g")
        self.defs.append(
            f'<pattern id="{gid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" x="{x}" y="{y}">'
            f'<circle cx="1" cy="1" r=".8" fill="{self.P["grid"]}"/></pattern>'
        )
        self.add(f'<g opacity=".11"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})" class="{self.c_fade(0, .9)}"/></g>')

    def frame(self, no, title, subtitle):
        """Panel outline with two cut corners, a red FIG tag, the title and a title block."""
        P, m, cut = self.P, 14, 22
        x0, y0, x1, y1 = m, m, self.w - m, self.h - m
        self.grid(x0 + 6, y0 + 6, x1 - x0 - 12, y1 - y0 - 12)
        self.path(chamfer(x0, y0, x1 - x0, y1 - y0, tr=cut, bl=cut), 0.05, P["faint"], 1.0, speed=2600)
        self.path([(x0, y0), (x0 + 44, y0)], 0.0, P["red"], 2.6, speed=200)
        self.path([(x1, y1), (x1 - 44, y1)], 0.0, P["red"], 2.6, speed=200)
        tag = f"FIG {no:02d}"
        tw = text_width("d8", tag, 13, 1.2) + 22
        self.add(f'<path d="M{34 + 7} 31 H{34 + tw:.1f} L{34 + tw - 7:.1f} 51 H34 Z" fill="{P["red"]}" class="{self.c_fade(0.1)}"/>')
        self.text(34 + 12, 46, tag, 13, P["on_red"], fam="d8", ls=1.2, delay=0.1)
        self.text(34 + tw + 12, 48.5, title, 21, P["ink"], fam="d8", ls=1.0, delay=0.2)
        self.text(34, 70, subtitle, 10, P["muted"], delay=0.4)
        bw, bh = 236, 34
        bx, by = x1 - bw, y1 - bh
        self.path([(bx, y1), (bx, by), (x1, by)], 0.3, P["faint"], 0.8, speed=900)
        self.path([(bx + 150, by), (bx + 150, y1)], 0.45, P["faint"], 0.8)
        self.text(bx + 9, by + 14, "CHIRAG KUMAR · SUJANIX", 8, P["muted"], ls=0.6, delay=0.5)
        self.text(bx + 9, by + 27, title.lower()[:24], 8, P["muted"], ls=0.3, delay=0.55)
        self.text(bx + 158, by + 14, f"FIG {no:02d} / {TOTAL_SHEETS:02d}", 8, P["muted"], ls=0.6, delay=0.5)
        self.text(bx + 158, by + 27, "REV 2026.11", 8, P["muted"], ls=0.6, delay=0.55)

    def box(self, x, y, w, h, delay, width=1.25, stroke=None, dashed=None, cut=0.0):
        d, _ = self.path(chamfer(x, y, w, h, tr=cut), delay, stroke, width, speed=900, dashed=dashed)
        return d

    def node(self, x, y, w, h, label, sub, delay, sub_fill=None, dashed=None):
        """A stage: cut top-right corner, a red tick on the top edge, label in display caps, detail in mono."""
        d = self.box(x, y, w, h, delay, dashed=dashed, cut=8)
        self.path([(x, y), (x + 14, y)], delay + 0.3, self.P["red"], 2.4, speed=200)
        t = delay + 0.35
        assert text_width("d8", label, 15.5, 0.7) < w - 16, label
        assert text_width("mono", sub, 9.3) < w - 16, sub
        short = h <= 40
        self.text(x + 10, y + (18 if short else 20), label, 15.5, self.P["ink"], fam="d8", ls=0.7, delay=t)
        self.text(x + 10, y + h - (7 if short else 10), sub, 9.3, sub_fill or self.P["muted"], delay=t + 0.1)
        return d

    def dim(self, x1, x2, y, label, delay, below=False):
        c = self.P["muted"]
        self.path([(x1, y - 4), (x1, y + 4)], delay, c, 0.9)
        self.path([(x2, y - 4), (x2, y + 4)], delay, c, 0.9)
        self.path([(x1, y), (x2, y)], delay + 0.05, c, 0.8, speed=900)
        self.path([(x1 + 5, y - 2.6), (x1, y), (x1 + 5, y + 2.6)], delay + 0.15, c, 0.8)
        self.path([(x2 - 5, y - 2.6), (x2, y), (x2 - 5, y + 2.6)], delay + 0.15, c, 0.8)
        self.text((x1 + x2) / 2, y + (12 if below else -4), label, 8.8, c, anchor="middle", delay=delay + 0.25)

    def wire(self, points, delay, r=7.0, width=1.25, stroke=None, dashed=None):
        pts_ = rounded(points, r)
        d, L = self.path(pts_, delay, stroke, width, dashed=dashed)
        return d, L

    # -- looping effects (start at START, repeat every `period` seconds)
    def pulse(self, wire, windows, period, color, length=18, width=2.2):
        d, L = wire
        p = length / L
        for a, b in windows:
            c = self.uid("p")
            self.css.append(
                f"@keyframes {c}{{0%,{pct(a)}{{stroke-dashoffset:{p:.4f}}}{pct(b)},100%{{stroke-dashoffset:-1}}}}"
                f".{c}{{stroke-dashoffset:{p:.4f};animation:{c} {period:.2f}s linear {START}s infinite both}}"
            )
            for wdt, op in ((width * 3.4, 0.22), (width, 1)):
                self.add(f'<path d="{d}" pathLength="1" fill="none" stroke="{color}" stroke-width="{wdt:.1f}" '
                         f'stroke-opacity="{op}" stroke-dasharray="{p:.4f} 1" class="{c}"/>')

    def _blink_css(self, c, windows, period, peak=1.0):
        frames = ["0%{opacity:0}"]
        for a, b in windows:
            ramp = min(0.012, (b - a) / 4)
            frames.append(f"{pct(a)}{{opacity:0}}{pct(a + ramp)}{{opacity:{peak}}}{pct(b - ramp)}{{opacity:{peak}}}{pct(b)}{{opacity:0}}")
        frames.append("100%{opacity:0}")
        self.css.append(f"@keyframes {c}{{{''.join(frames)}}}.{c}{{opacity:0;animation:{c} {period:.2f}s linear {START}s infinite both}}")

    def flash(self, d, windows, period, color, width=1.9):
        c = self.uid("h")
        self._blink_css(c, windows, period)
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" class="{c}"/>')

    def blink_rect(self, x, y, w, h, windows, period, color, rx=2):
        """An engine lighting up: a soft wash plus a red outline, so its label stays readable."""
        c = self.uid("b")
        self._blink_css(c, windows, period)
        self.add(f'<g class="{c}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{color}" '
                 f'fill-opacity=".16" stroke="{color}" stroke-width="1.6"/></g>')

    def blink_text(self, x, y, s, windows, period, color, size=10, anchor="middle", fam="mono"):
        c = self.uid("t")
        self._blink_css(c, windows, period)
        self.text(x, y, s, size, color, fam=fam, anchor=anchor, cls=c)

    def spark(self, x, y, windows, period, color, r=7):
        """A small four-ray star that flickers for a moment."""
        c = self.uid("s")
        self._blink_css(c, windows, period)
        rays = "".join(
            f'<line x1="{x + math.cos(a) * 2:.1f}" y1="{y + math.sin(a) * 2:.1f}" x2="{x + math.cos(a) * r:.1f}" '
            f'y2="{y + math.sin(a) * r:.1f}" stroke="{color}" stroke-width="1.4" stroke-linecap="round"/>'
            for a in (0.4, 0.4 + math.pi / 2, 0.4 + math.pi, 0.4 + 3 * math.pi / 2)
        )
        self.add(f'<g class="{c}">{rays}<circle cx="{x}" cy="{y}" r="1.8" fill="{color}"/></g>')

    def render(self):
        style = self.fonts.css() + "".join(self.css)
        return svg_doc(self.w, self.h, self.title, self.desc, style, "".join(self.body), "".join(self.defs))


def loops(a, b, ks, n):
    """Windows for one step that happens in loop k of n (period = n × T)."""
    return [((k + a) / n, (k + b) / n) for k in ks]


# ================================================================= FIG 01 on-device reading
def dwg_reading(theme):
    D = Drawing(theme, 900, 404, "FIG 01 · on-device reading",
                "Blueprint of a TrueRead meter reading: CameraX photo, the TrueRead app, an AIDL call (processReadingV4) to "
                "the separate Engine app, a router that prefers one path and allows one fallback, the local ONNX Runtime "
                "pipeline (11 INT8 models, decrypted in memory) or the API, then a reading with per-digit confidence. "
                "Red pulses are digital reads, cyan analog reads, pink a local failure that falls back to the API.")
    P = D.P
    D.frame(1, "ON-DEVICE READING", "one photo in, one reading out · the models run on the phone, the api is the fallback")
    cy = 158
    cam = D.node(40, 132, 96, 52, "CAMERA", "camerax · jpeg", 0.5)
    app = D.node(164, 132, 112, 52, "TRUEREAD", "compose · hilt", 0.65)
    eng = D.node(304, 132, 112, 52, "ENGINE", "bound service", 0.8)
    rtr = D.node(444, 132, 100, 52, "ROUTER", "1 fallback", 0.95)
    loc = D.node(580, 96, 122, 46, "LOCAL", "onnx rt · int8", 1.1)
    api = D.node(580, 174, 122, 46, "API", "8 s timeout", 1.15)
    red_ = D.node(744, 132, 116, 52, "READING", '"005269" · 97%', 1.3, sub_fill=P["ink2"])
    w1 = D.wire([(136, cy), (164, cy)], 0.75)
    w2 = D.wire([(276, cy), (304, cy)], 0.9)
    w3 = D.wire([(416, cy), (444, cy)], 1.05)
    w4l = D.wire([(544, cy), (562, cy), (562, 119), (580, 119)], 1.2)
    w4a = D.wire([(544, cy), (562, cy), (562, 197), (580, 197)], 1.2)
    w5l = D.wire([(702, 119), (723, 119), (723, cy), (744, cy)], 1.4)
    w5a = D.wire([(702, 197), (723, 197), (723, cy), (744, cy)], 1.4)
    D.dim(164, 416, 206, "aidl · processReadingV4 · separate apk", 1.6)
    D.dim(444, 544, 206, "3 fails → 5 min", 1.7)
    D.dim(580, 702, 84, "11 sessions · ≤ 4 threads", 1.85)
    D.dim(744, 860, 206, "edit only < 85 %", 1.9)
    # the Engine's model rail: 11 INT8 ONNX models, decrypted in memory
    D.box(40, 262, 820, 60, 1.5, width=1.0, stroke=P["ink2"])
    D.text(52, 278, "TRUEREAD ENGINE · ONNX RUNTIME · 11 × INT8 · AES-GCM FILES, DECRYPTED IN MEMORY", 9, P["muted"], ls=0.8, delay=1.9)
    engines = {}
    for key, x, w in (("spoof", 52, 62), ("presence", 120, 76), ("dial-obb", 202, 72), ("classifier", 280, 88), ("parameter", 374, 82)):
        D.box(x, 290, w, 22, 2.0, width=0.9)
        D.text(x + w / 2, 304.5, key, 8.6, P["ink2"], anchor="middle", delay=2.2)
        engines[key] = (x, 290, w, 22)
    for gx, glab in ((480, "svtrv2"), (630, "analog")):
        D.text(gx, 286, glab, 8, P["muted"], delay=2.2)
        for k, sz in enumerate("sml"):
            x = gx + k * 42
            D.box(x, 290, 36, 22, 2.05 + 0.05 * k, width=0.9)
            D.text(x + 18, 304.5, sz, 8.6, P["ink2"], anchor="middle", delay=2.25)
            engines[f"{glab}-{sz}"] = (x, 290, 36, 22)
    D.text(762, 304.5, "1 file · 1 session", 8, P["muted"], delay=2.3)
    drop_e = D.wire([(360, 212), (360, 262)], 1.95, width=0.9, stroke=P["faint"])

    T, N = 6.0, 3
    red, cyan, pink = P["red"], P["cyan"], P["pink"]
    every = lambda a, b: loops(a, b, range(N), N)
    D.pulse(w1, every(0.00, 0.07), N * T, red)
    D.flash(app, every(0.07, 0.15), N * T, red)
    D.pulse(w2, every(0.15, 0.22), N * T, red)
    D.flash(eng, every(0.22, 0.30), N * T, red)
    D.pulse(drop_e, every(0.22, 0.27), N * T, red, length=12, width=1.6)
    for k, key in enumerate(("spoof", "presence", "dial-obb", "classifier")):
        D.blink_rect(*engines[key], every(0.27 + 0.04 * k, 0.32 + 0.04 * k), N * T, red)
    D.pulse(w3, every(0.30, 0.37), N * T, red)
    D.flash(rtr, every(0.37, 0.45), N * T, red)
    # photo 0 digital (red), photo 1 analog (cyan), photo 2: local fails, API answers (pink)
    D.pulse(w4l, loops(0.45, 0.52, (0,), N), N * T, red)
    D.flash(loc, loops(0.52, 0.64, (0,), N), N * T, red)
    D.blink_rect(*engines["svtrv2-m"], loops(0.54, 0.62, (0,), N), N * T, red)
    D.pulse(w5l, loops(0.64, 0.72, (0,), N), N * T, red)
    D.flash(red_, loops(0.72, 0.92, (0,), N), N * T, red)
    D.pulse(w4l, loops(0.45, 0.52, (1,), N), N * T, cyan)
    D.flash(loc, loops(0.52, 0.64, (1,), N), N * T, cyan)
    for sz in "sml":
        D.blink_rect(*engines[f"analog-{sz}"], loops(0.54, 0.62, (1,), N), N * T, cyan)
    D.pulse(w5l, loops(0.64, 0.72, (1,), N), N * T, cyan)
    D.flash(red_, loops(0.72, 0.92, (1,), N), N * T, cyan)
    D.pulse(w4l, loops(0.45, 0.52, (2,), N), N * T, red)
    D.flash(loc, loops(0.52, 0.58, (2,), N), N * T, pink)
    D.spark(641, 96, loops(0.53, 0.57, (2,), N), N * T, pink, r=8)
    D.pulse(w4a, loops(0.58, 0.65, (2,), N), N * T, pink)
    D.flash(api, loops(0.65, 0.74, (2,), N), N * T, pink)
    D.pulse(w5a, loops(0.74, 0.81, (2,), N), N * T, pink)
    D.flash(red_, loops(0.81, 0.95, (2,), N), N * T, pink)
    D.spark(838, 268, [(0.62, 0.64)], 11.0, cyan)
    return D.render()


# ================================================================= FIG 02 offline sync
def dwg_sync(theme):
    D = Drawing(theme, 900, 392, "FIG 02 · offline sync",
                "Blueprint of how a reading leaves the phone: Submit saves it to Room (meter table plus an outbox row keyed "
                "by record_id), a WorkManager worker uploads the photos to S3, the record is validated on the phone against "
                "the payload contract, then it goes to the intake API, or to the failed API with the broken rule's error "
                "code. Network, server and key problems keep it on the phone for the next run; nothing is dropped.")
    P = D.P
    D.frame(2, "OFFLINE SYNC", "a reading is done only when the server confirms it · until then it waits on the phone")
    sub = D.node(40, 172, 100, 52, "SUBMIT", "reader taps", 0.5)
    room = D.node(170, 172, 116, 52, "ROOM", "outbox row", 0.65)
    work = D.node(316, 172, 112, 52, "WORKER", "workmanager", 0.8)
    s3 = D.node(458, 172, 96, 52, "S3", "photos first", 0.95)
    cx, cyy = 624, 198
    diamond = [(cx, cyy - 34), (cx + 36, cyy), (cx, cyy + 34), (cx - 36, cyy), (cx, cyy - 34)]
    D.path(diamond, 1.05, width=1.25)
    D.text(cx, cyy + 4, "CHECK", 12.5, P["ink"], fam="d8", anchor="middle", ls=0.8, delay=1.3)
    intake = D.node(700, 98, 160, 46, "INTAKE API", "SENT", 1.15)
    failed = D.node(700, 256, 160, 46, "FAILED API", "error code + field", 1.2)
    w1 = D.wire([(140, 198), (170, 198)], 0.7)
    w2 = D.wire([(286, 198), (316, 198)], 0.85)
    w3 = D.wire([(428, 198), (458, 198)], 1.0)
    w4 = D.wire([(554, 198), (588, 198)], 1.1)
    w_ok = D.wire([(cx, cyy - 34), (cx, 121), (700, 121)], 1.2)
    w_bad = D.wire([(cx, cyy + 34), (cx, 279), (700, 279)], 1.2)
    w_retry = D.wire([(506, 172), (506, 128), (228, 128), (228, 172)], 1.4, dashed="4 4", width=1.0, stroke=P["muted"])
    D.text(250, 121, "network · 5xx · bad key → kept on phone, retried", 8.4, P["muted"], delay=1.6)
    D.text(632, 114, "passes", 8.4, P["muted"], delay=1.6)
    D.text(632, 272, "rule broken", 8.4, P["muted"], delay=1.65)
    D.text(cx + 44, cyy + 4, "contract v2", 8.4, P["muted"], delay=1.7)
    D.dim(700, 860, 87, "state: SENT · FAILED_REPORTED", 1.8)
    D.dim(40, 554, 252, "foreground: ≥ batch size or 2 h old · background: always", 1.85, below=True)
    D.text(40, 300, "billing blocked at 20 pending · resend replaces its row, never a second copy", 9, P["ink2"], delay=2.0)

    T, N = 6.0, 3
    red, cyan, pink = P["red"], P["cyan"], P["pink"]
    every = lambda a, b: loops(a, b, range(N), N)
    D.flash(sub, every(0.00, 0.06), N * T, red)
    D.pulse(w1, every(0.05, 0.12), N * T, red)
    D.flash(room, every(0.12, 0.22), N * T, red)
    D.pulse(w2, every(0.22, 0.29), N * T, red)
    D.flash(work, every(0.29, 0.37), N * T, red)
    D.pulse(w3, every(0.37, 0.44), N * T, red)
    # loop 0: passes → intake; loop 1: breaks a rule → failed API (cyan); loop 2: network down → back to Room (pink)
    D.flash(s3, loops(0.44, 0.52, (0, 1), N), N * T, red)
    D.pulse(w4, loops(0.52, 0.58, (0, 1), N), N * T, red)
    D.flash(pathd(diamond), loops(0.58, 0.66, (0, 1), N), N * T, red)
    D.pulse(w_ok, loops(0.66, 0.74, (0,), N), N * T, red)
    D.flash(intake, loops(0.74, 0.92, (0,), N), N * T, red)
    D.pulse(w_bad, loops(0.66, 0.74, (1,), N), N * T, cyan)
    D.flash(failed, loops(0.74, 0.92, (1,), N), N * T, cyan)
    D.flash(s3, loops(0.44, 0.50, (2,), N), N * T, pink)
    D.spark(506, 172, loops(0.46, 0.50, (2,), N), N * T, pink, r=8)
    D.pulse(w_retry, loops(0.50, 0.66, (2,), N), N * T, pink)
    D.flash(room, loops(0.66, 0.80, (2,), N), N * T, pink)
    return D.render()


# ================================================================= FIG 03 model updates
def dwg_models(theme):
    D = Drawing(theme, 900, 330, "FIG 03 · model updates",
                "Line drawing of a model update as five checkpoint gates on a track: download (WorkManager, from a Firebase "
                "manifest), verify (size and SHA-256), encrypt (AES-GCM with an Android Keystore key), warm (load and run "
                "every model once), activate. An update token passes through; now and then a model fails to load at the "
                "warm gate and the Engine rolls back to the previous set.")
    P = D.P
    D.frame(3, "MODEL UPDATES", "new models reach phones in the field · a bad set fails while loading, never at a reading")
    ty = 216
    D.path([(40, ty), (860, ty)], 0.4, P["ink"], 1.3, speed=1400)
    for k, x in enumerate(range(48, 860, 16)):
        D.path([(x, ty + 2), (x, ty + 7)], 0.6 + k * 0.004, P["faint"], 0.9)
    stages = [("DOWNLOAD", "firebase manifest · worker"), ("VERIFY", "size + sha-256"),
              ("ENCRYPT", "aes-gcm · keystore key"), ("WARM", "load + run all 11"),
              ("ACTIVATE", "swap the active set")]
    xs = [124, 286, 448, 610, 772]
    gates = []
    for i, ((name, sub), cx) in enumerate(zip(stages, xs)):
        dl = 0.7 + 0.22 * i
        cap = [(cx - 42, 132), (cx - 36, 126), (cx + 36, 126), (cx + 42, 132)]
        posts = [[(cx - 30, ty), (cx - 30, 126)], [(cx + 30, ty), (cx + 30, 126)]]
        bar = [(cx - 30, 146), (cx + 30, 146)]
        D.path(cap, dl, P["ink"], 1.6, speed=300)
        for post in posts:
            D.path(post, dl + 0.15, P["ink"], 1.4, speed=300)
        D.path(bar, dl + 0.35, P["ink2"], 1.0, dashed="3 3")
        D.add(f'<rect x="{cx - 4}" y="{114}" width="8" height="8" fill="none" stroke="{P["ink2"]}" stroke-width="1.1" '
              f'class="{D.c_fade(dl + 0.4)}"/>')
        D.text(cx, 104, f"{i + 1:02d}", 13, P["muted"], fam="d8", anchor="middle", ls=1.0, delay=dl + 0.4)
        D.text(cx, ty + 31, name, 15, P["ink"], fam="d8", anchor="middle", ls=1.0, delay=dl + 0.5)
        D.text(cx, ty + 47, sub, 8.8, P["muted"], anchor="middle", delay=dl + 0.55)
        lamp = f"M{cx - 4} 114 h8 v8 h-8 Z"
        gates.append(" ".join([pathd(cap), *(pathd(q) for q in posts), pathd(bar), lamp]))

    T, N = 7.0, 3
    period = N * T
    x_start, x_end, pause = 46, 846, 0.05

    def run_frames(k, fail):
        t0, span = k / N, 1 / N
        fr = [(t0, x_start, 0.0), (t0 + 0.02 * span, x_start, 1.0)]
        t, prev = t0 + 0.02 * span, x_start
        for x in (xs[:4] if fail else xs):
            t += (x - prev) / (x_end - x_start) * 0.55 * span
            fr.append((t, x, 1.0))
            t += pause * span
            fr.append((t, x, 1.0))
            prev = x
        if fail:
            fr += [(t + 0.03 * span, xs[3] - 10, 1.0), (t + 0.05 * span, xs[3] - 4, 1.0),
                   (t + 0.20 * span, x_start, 0.25), ((k + 1) / N - 0.001, x_start, 0.0)]
        else:
            t += (x_end - prev) / (x_end - x_start) * 0.55 * span
            fr += [(t, x_end, 1.0), (t + 0.04 * span, x_end, 0.0), ((k + 1) / N - 0.001, x_start, 0.0)]
        return fr

    frames = run_frames(0, False) + run_frames(1, False) + run_frames(2, True)
    assert all(b[0] > a[0] for a, b in zip(frames, frames[1:])), "token keyframes overlap"
    kc = D.uid("tok")
    kf = "".join(f"{pct(t)}{{transform:translateX({x - x_start:.1f}px);opacity:{o}}}" for t, x, o in frames)
    D.css.append(f"@keyframes {kc}{{{kf}}}.{kc}{{opacity:0;animation:{kc} {period:.1f}s linear {START}s infinite both}}")
    D.add(f'<g class="{kc}"><path d="M{x_start} {ty - 19} l9 9 l-9 9 l-9 -9 Z" fill="{P["red"]}"/>'
          f'<path d="M{x_start} {ty - 14} v8" stroke="{P["on_red"]}" stroke-width="1.6" stroke-linecap="round"/></g>')
    for k in range(N):
        fail = k == 2
        fr = run_frames(k, fail)
        for gi, cx in enumerate(xs):
            hits = [t for t, x, o in fr if abs(x - cx) < 0.5 and o > 0]
            if not hits:
                continue
            a, b = min(hits) - 0.004, max(hits) + 0.02
            col = P["pink"] if (fail and gi == 3) else P["red"]
            D.flash(gates[gi], [(a, b)], period, col, width=2.2)
            mark = "× rolled back" if (fail and gi == 3) else "✓"
            D.blink_text(cx, 86, mark, [(a, min((k + 1) / N - 0.01, b + 0.18))], period, col, size=11)
    D.spark(xs[3], 150, loops(0.62, 0.66, (2,), N), period, P["pink"], r=9)
    D.spark(xs[2], 128, [(0.41, 0.43)], 12.0, P["cyan"])
    return D.render()


# ================================================================= FIG 04 DLMS over Bluetooth
def dwg_dlms(theme):
    D = Drawing(theme, 900, 440, "FIG 04 · DLMS over Bluetooth",
                "Sequence drawing of a DLMS/COSEM read over Bluetooth. On the phone, a scanner finds meters over BLE and "
                "Classic at once, one channel interface hides GATT and SPP, and the Gurux-based client runs the IEC 62056-46 "
                "HDLC session: SNRM and UA, AARQ with LOW authentication and AARE, then a GET per OBIS code whose response "
                "can span several blocks, then DISC. Out come 13 months of billing history, tariff zones T1 to T6, max "
                "demand, voltage, current and power factor.")
    P = D.P
    D.frame(4, "DLMS OVER BLUETOOTH", "phone and smart meter talk iec 62056-46 hdlc · every frame drawn below")
    scan = D.node(40, 112, 168, 46, "SCANNER", "ble + classic at once", 0.5)
    chan = D.node(40, 196, 168, 46, "CHANNEL", "gatt | spp socket", 0.65)
    cli = D.node(40, 280, 168, 46, "DLMS CLIENT", "gurux · hdlc · obis", 0.8)
    D.wire([(124, 158), (124, 196)], 0.75)
    D.wire([(124, 242), (124, 280)], 0.9)
    phone = D.node(250, 86, 120, 36, "PHONE", "mvvm · stateflow", 0.6)
    meter = D.node(720, 86, 140, 36, "METER", "dlms/cosem", 0.7)
    px, mx = 310, 790
    D.path([(px, 122), (px, 360)], 0.9, P["faint"], 1.0, dashed="3 4")
    D.path([(mx, 122), (mx, 360)], 0.95, P["faint"], 1.0, dashed="3 4")
    D.wire([(208, 290), (px, 290)], 1.0, width=1.0, stroke=P["muted"])
    msgs = [("SNRM", True, "link"), ("UA", False, ""), ("AARQ · auth = LOW", True, "association"), ("AARE", False, ""),
            ("GET · OBIS", True, ""), ("GET RESPONSE · block 1..n", False, ""), ("DISC", True, "teardown")]
    wires = []
    for i, (lab, out, note) in enumerate(msgs):
        y = 146 + i * 32
        dl = 1.1 + 0.12 * i
        a, b = (px, mx) if out else (mx, px)
        w = D.wire([(a, y), (b, y)], dl, width=1.2)
        tip = -1 if out else 1
        D.path([(b + 6 * tip, y - 3.5), (b, y), (b + 6 * tip, y + 3.5)], dl + 0.3, P["ink"], 1.2)
        D.text((px + mx) / 2, y - 5, lab, 10.5, P["ink"], fam="d8", anchor="middle", ls=0.8, delay=dl + 0.2)
        if note:
            D.text(mx + 10, y + 3, note, 8.4, P["muted"], delay=dl + 0.25)
        wires.append(w)
    D.path([(mx + 6, 274), (mx + 12, 274), (mx + 12, 310), (mx + 6, 310)], 1.9, P["muted"], 0.9)
    D.text(mx + 16, 296, "repeat", 8.4, P["muted"], delay=2.0)
    D.text(40, 384, "billing profile · 13 months · tariff zones T1–T6 (kWh, kVAh) · max demand + timestamp", 9, P["ink2"], delay=2.1)
    D.text(40, 400, "instantaneous: voltage · current · power factor · active + apparent power", 9, P["muted"], delay=2.2)

    T, N = 6.5, 3
    red, cyan, pink = P["red"], P["cyan"], P["pink"]
    every = lambda a, b: loops(a, b, range(N), N)
    D.flash(scan, every(0.00, 0.06), N * T, red)
    D.flash(chan, every(0.05, 0.11), N * T, red)
    D.flash(cli, every(0.10, 0.16), N * T, red)
    t = 0.16
    for i, w in enumerate(wires):
        col = red if msgs[i][1] else cyan
        span = 0.16 if i == 5 else 0.09
        D.pulse(w, every(t, t + span * 0.8), N * T, col, length=22)
        if i == 5:  # multi-block: two more pulses
            D.pulse(w, every(t + 0.04, t + 0.04 + span * 0.6), N * T, col, length=14, width=1.6)
        t += span
    D.flash(phone, every(0.93, 0.99), N * T, red)
    D.flash(meter, loops(0.18, 0.24, (2,), N), N * T, pink)
    D.spark(mx, 146, loops(0.18, 0.21, (2,), N), N * T, pink)
    return D.render()


# ================================================================= FIG 05 Room-Splits
def dwg_splits(theme):
    D = Drawing(theme, 900, 392, "FIG 05 · Room-Splits",
                "Blueprint of Room-Splits, a Kotlin Multiplatform expense-sharing app. Android, iOS and Web (Wasm) share one "
                "Compose Multiplatform UI and one shared module (domain, data, MVI stores, Koin). The shared module keeps a "
                "local SQLDelight database for offline use and talks to a Ktor server on PostgreSQL through the Ktor client. "
                "Everything past the scaffold is planned and drawn dashed.")
    P = D.P
    D.frame(5, "ROOM-SPLITS", "share logic once, ship to android, ios and web · dashed parts are on the roadmap")
    dash = "4 4"
    andr = D.node(40, 96, 112, 40, "ANDROID", "androidMain", 0.5)
    ios = D.node(40, 178, 112, 40, "IOS", "iosMain · xcode", 0.6)
    web = D.node(40, 260, 112, 40, "WEB", "wasmJsMain", 0.7)
    ui = D.node(196, 168, 140, 60, "COMPOSE MP", "one ui · 3 targets", 0.8)
    sh = D.node(380, 168, 150, 60, "SHARED", "domain · data · mvi", 0.95)
    db = D.node(580, 96, 126, 46, "SQLDELIGHT", "offline-first", 1.1, dashed=dash)
    kc = D.node(580, 250, 126, 46, "KTOR CLIENT", "sync · koin", 1.15, dashed=dash)
    srv = D.node(744, 250, 116, 46, "KTOR SERVER", "postgresql", 1.3, dashed=dash)
    wa = D.wire([(152, 116), (174, 116), (174, 198), (196, 198)], 0.7)
    wi = D.wire([(152, 198), (196, 198)], 0.75)
    ww = D.wire([(152, 280), (174, 280), (174, 198), (196, 198)], 0.8)
    wu = D.wire([(336, 198), (380, 198)], 0.95)
    wd = D.wire([(530, 198), (555, 198), (555, 119), (580, 119)], 1.1, dashed=dash)
    wk = D.wire([(530, 198), (555, 198), (555, 273), (580, 273)], 1.15, dashed=dash)
    ws = D.wire([(706, 273), (744, 273)], 1.3, dashed=dash)
    D.dim(380, 530, 248, "kotlin multiplatform", 1.6, below=True)
    D.text(724, 122, "groups · expenses · balances", 8.4, P["muted"], delay=1.7)
    D.text(724, 134, "equal · exact · % · shares", 8.4, P["muted"], delay=1.75)
    D.text(40, 340, "phases: foundation → auth → groups → expenses + splits → balances + settle-up → offline sync, export, currency", 9, P["ink2"], delay=2.0)
    D.text(40, 356, "clean architecture + mvi · coroutines + flow · kotlinx.serialization · github actions", 9, P["muted"], delay=2.1)

    T, N = 6.0, 3
    red, cyan, pink = P["red"], P["cyan"], P["pink"]
    starts = [(wa, andr), (wi, ios), (ww, web)]
    for k, (w, n) in enumerate(starts):
        D.flash(n, loops(0.00, 0.08, (k,), N), N * T, red)
        D.pulse(w, loops(0.08, 0.18, (k,), N), N * T, red)
    every = lambda a, b: loops(a, b, range(N), N)
    D.flash(ui, every(0.18, 0.28), N * T, red)
    D.pulse(wu, every(0.28, 0.35), N * T, red)
    D.flash(sh, every(0.35, 0.46), N * T, red)
    D.pulse(wd, every(0.46, 0.56), N * T, cyan)
    D.flash(db, every(0.56, 0.66), N * T, cyan)
    D.pulse(wk, loops(0.60, 0.70, (0, 1), N), N * T, red)
    D.flash(kc, loops(0.70, 0.78, (0, 1), N), N * T, red)
    D.pulse(ws, loops(0.78, 0.84, (0, 1), N), N * T, red)
    D.flash(srv, loops(0.84, 0.95, (0, 1), N), N * T, red)
    D.spark(580, 273, loops(0.66, 0.70, (2,), N), N * T, pink, r=8)
    return D.render()


# ================================================================= FIG 06 FieldProof
def dwg_fieldproof(theme):
    D = Drawing(theme, 900, 392, "FIG 06 · FieldProof",
                "Blueprint of FieldProof, an offline-first field inspection app. Capture: Compose UI and CameraX save "
                "inspections, checklist outcomes and photos to Room, the single source of truth, with a durable sync "
                "operation per upload carrying a stable idempotency key. Sync state machine: queued, uploading, synced; a "
                "transient failure goes back to queued, an exhausted retry budget to failed, and a version conflict to "
                "needs resolution. The server is a FastAPI service on PostgreSQL that dedupes by idempotency key and "
                "renders PDF reports.")
    P = D.P
    D.frame(6, "FIELDPROOF", "works in airplane mode · a retry never makes a second copy of the evidence")
    cap = D.node(40, 98, 120, 46, "CAPTURE", "compose · camerax", 0.5)
    room = D.node(40, 196, 120, 46, "ROOM", "source of truth", 0.65)
    op = D.node(40, 290, 120, 46, "SYNC OP", "idempotency key", 0.8)
    D.wire([(100, 144), (100, 196)], 0.6)
    D.wire([(100, 242), (100, 290)], 0.75)
    q = D.node(220, 172, 112, 52, "QUEUED", "durable", 0.9)
    up = D.node(386, 172, 120, 52, "UPLOADING", "retrofit · okhttp", 1.0)
    ok = D.node(560, 98, 112, 46, "SYNCED", "server version", 1.15)
    fl = D.node(560, 172, 112, 46, "FAILED", "budget spent", 1.2)
    nr = D.node(560, 250, 140, 46, "NEEDS REVIEW", "version conflict", 1.25)
    srv = D.node(764, 98, 96, 46, "FASTAPI", "postgres · pdf", 1.35)
    w_op = D.wire([(160, 313), (190, 313), (190, 198), (220, 198)], 0.85)
    w_qu = D.wire([(332, 198), (386, 198)], 1.0)
    w_ok = D.wire([(506, 186), (533, 186), (533, 121), (560, 121)], 1.15)
    w_fl = D.wire([(506, 198), (560, 198)], 1.2)
    w_nr = D.wire([(506, 210), (533, 210), (533, 273), (560, 273)], 1.25)
    w_sv = D.wire([(672, 121), (764, 121)], 1.3)
    w_rt = D.wire([(446, 224), (446, 252), (276, 252), (276, 224)], 1.4, dashed="4 4", width=1.0, stroke=P["muted"])
    D.text(290, 266, "transient → retry, backoff", 8.4, P["muted"], delay=1.6)
    D.text(678, 114, "Idempotency-Key", 8.4, P["muted"], delay=1.65)
    D.dim(764, 860, 160, "dedupe by key", 1.8, below=True)
    D.text(40, 362, "177 android tests (jvm + instrumented) · 95 backend tests · ci emulator lane · signed release pipeline", 9, P["ink2"], delay=2.0)

    T, N = 6.0, 3
    red, cyan, pink = P["red"], P["cyan"], P["pink"]
    every = lambda a, b: loops(a, b, range(N), N)
    D.flash(cap, every(0.00, 0.07), N * T, red)
    D.flash(room, every(0.07, 0.14), N * T, red)
    D.flash(op, every(0.14, 0.20), N * T, red)
    D.pulse(w_op, every(0.20, 0.28), N * T, red)
    D.flash(q, every(0.28, 0.36), N * T, red)
    D.pulse(w_qu, every(0.36, 0.42), N * T, red)
    D.flash(up, every(0.42, 0.52), N * T, red)
    # loop 0: synced; loop 1: transient failure, retry, then synced; loop 2: version conflict
    D.pulse(w_ok, loops(0.52, 0.60, (0,), N), N * T, red)
    D.flash(ok, loops(0.60, 0.70, (0,), N), N * T, red)
    D.pulse(w_sv, loops(0.62, 0.70, (0,), N), N * T, red)
    D.flash(srv, loops(0.70, 0.85, (0,), N), N * T, red)
    D.spark(446, 224, loops(0.52, 0.55, (1,), N), N * T, pink, r=8)
    D.pulse(w_rt, loops(0.52, 0.64, (1,), N), N * T, pink)
    D.flash(q, loops(0.64, 0.72, (1,), N), N * T, pink)
    D.pulse(w_qu, loops(0.72, 0.78, (1,), N), N * T, red)
    D.flash(up, loops(0.78, 0.84, (1,), N), N * T, red)
    D.pulse(w_ok, loops(0.84, 0.90, (1,), N), N * T, red)
    D.flash(ok, loops(0.90, 0.98, (1,), N), N * T, red)
    D.pulse(w_nr, loops(0.52, 0.60, (2,), N), N * T, cyan)
    D.flash(nr, loops(0.60, 0.80, (2,), N), N * T, cyan)
    D.spark(838, 104, [(0.31, 0.33)], 13.0, cyan)
    return D.render()


DRAWINGS = {
    "fig01-reading": dwg_reading,
    "fig02-sync": dwg_sync,
    "fig03-models": dwg_models,
    "fig04-dlms": dwg_dlms,
    "fig05-splits": dwg_splits,
    "fig06-fieldproof": dwg_fieldproof,
}
