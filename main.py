#!/usr/bin/env python3
"""news-image-20261118 entry: Wednesday 18 November 2026 in one image.

A newspaper front page drawn programmatically, stdlib only (struct +
zlib + math + os). Fully deterministic: fixed constants, no time, no
OS randomness, no network, no external assets. Writes exactly one
1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

The day, as reported by the morning of 18 Nov 2026 (07:10 WIB):
  1. Trump lands in Manila - Quad talks, then a China visit.
  2. Ukraine hits the Crimea bridge a second day running; Russia
     pounds bridges in Kyiv.
  3. The US and Iran trade fire at the Strait of Hormuz: US jets hit
     an IRGC missile site on Qeshm Island after Iranian drones
     targeted a US radar in Bahrain.
  4. Cyclone Akvan strengthens in the Bay of Bengal, severe by 19 Nov.
  5. Canada and China extend trade deals as Xi meets Carney ahead
     of the APEC summit.

Design: a masthead naming the day, one big lead story (Manila) and
four picture panels, each with a short headline and sub-line, so a
viewer who missed the day can tell what happened from the image
alone. Text is drawn with a built-in 5x7 bitmap font (no font files,
no Pillow - the sandbox runs stdlib only).

REFRESH NOTE: this build covers the news as reported up to ~00:10
UTC / 07:10 WIB on 18 Nov. The day is still young; before the final
submit (deadline 20 Nov 07:00 WIB) the headlines should be refreshed
against the full day's news and the image redrawn if a bigger story
lands later on the 18th. See BUILD-REPORT.md.
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (26, 26, 46)
NAVY = (20, 38, 74)
NAVY_LT = (38, 62, 110)
RED = (192, 57, 43)
RED_LT = (231, 76, 60)
SKY = (135, 196, 235)
SKY_PALE = (208, 232, 248)
SEA = (23, 94, 138)
SEA_DK = (13, 60, 92)
GOLD = (243, 192, 60)
WHITE = (255, 255, 255)
GREY = (120, 124, 132)
ORANGE = (243, 140, 40)
YELLOW = (255, 214, 64)

# ---------------------------------------------------------------- helpers

def clamp(v):
    if v < 0:
        return 0
    if v > 255:
        return 255
    return int(v)


def lerp(a, b, t):
    return a + (b - a) * t


def mix3(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def set_px(buf, x, y, col):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = col[0]
        buf[i + 1] = col[1]
        buf[i + 2] = col[2]


def add_px(buf, x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = clamp(buf[i] + r)
        buf[i + 1] = clamp(buf[i + 1] + g)
        buf[i + 2] = clamp(buf[i + 2] + b)


def fill_rect(buf, x0, y0, x1, y1, col):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    if x0 >= x1 or y0 >= y1:
        return
    r, g, b = col
    row = bytes((r, g, b)) * (x1 - x0)
    for y in range(y0, y1):
        s = y * W * 3 + x0 * 3
        buf[s:s + len(row)] = row


def fill_disc(buf, cx, cy, rad, col):
    r0 = int(rad)
    for dy in range(-r0, r0 + 1):
        y = cy + dy
        if y < 0 or y >= H:
            continue
        half = int(math.sqrt(max(0, r0 * r0 - dy * dy)))
        fill_rect(buf, cx - half, y, cx + half + 1, y + 1, col)


def add_disc(buf, cx, cy, rad, col, strength=1.0):
    r0 = int(rad)
    for dy in range(-r0, r0 + 1):
        y = cy + dy
        if y < 0 or y >= H:
            continue
        half = int(math.sqrt(max(0, r0 * r0 - dy * dy)))
        for dx in range(-half, half + 1):
            d = math.sqrt(dx * dx + dy * dy) / rad
            f = (1.0 - d * d) * strength
            if f <= 0:
                continue
            add_px(buf, cx + dx, y, col[0] * f, col[1] * f, col[2] * f)


def fill_triangle(buf, p1, p2, p3, col):
    """Flat filled triangle by scanline interpolation."""
    pts = sorted([p1, p2, p3], key=lambda p: p[1])
    (x1, y1), (x2, y2), (x3, y3) = pts
    if y1 == y3:
        return
    def edge_x(xa, ya, xb, yb, y):
        if yb == ya:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)
    for y in range(max(0, y1), min(H, y3 + 1)):
        if y < y2:
            xa = edge_x(x1, y1, x2, y2, y)
            xb = edge_x(x1, y1, x3, y3, y)
        else:
            xa = edge_x(x2, y2, x3, y3, y)
            xb = edge_x(x1, y1, x3, y3, y)
        if xa > xb:
            xa, xb = xb, xa
        fill_rect(buf, int(xa), y, int(xb) + 1, y + 1, col)


def draw_line(buf, x0, y0, x1, y1, col, thick=1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + (x1 - x0) * t)
        y = int(y0 + (y1 - y0) * t)
        fill_disc(buf, x, y, max(1, thick // 2), col)


def vgrad(buf, x0, y0, x1, y1, top, bottom):
    """Vertical gradient fill of a rectangle."""
    h = max(1, y1 - y0)
    for y in range(max(0, y0), min(H, y1)):
        t = (y - y0) / h
        c = mix3(top, bottom, t)
        fill_rect(buf, x0, y, x1, y + 1,
                  (clamp(c[0]), clamp(c[1]), clamp(c[2])))


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits ('1' = ink). Uppercase only; text is
# uppercased before drawing.

FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '+': ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '*': ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
}


def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(buf, x, y, s, scale, col):
    """Draw text at (x, y); top-left origin. Returns width drawn."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT['?'])
        for row in range(7):
            bits = glyph[row]
            for bit in range(5):
                if bits[bit] == '1':
                    fill_rect(buf, cx + bit * scale, y + row * scale,
                              cx + (bit + 1) * scale,
                              y + (row + 1) * scale, col)
        cx += 6 * scale
    return cx - x


def draw_text_centered(buf, cx, y, s, scale, col):
    w = text_width(s, scale)
    draw_text(buf, cx - w // 2, y, s, scale, col)


def wrap_text(s, max_chars):
    """Greedy word wrap; returns list of lines, each <= max_chars."""
    words = s.split(' ')
    lines = []
    cur = ''
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += ' ' + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- PNG writer

def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, buf):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: None
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)  # fixed level -> deterministic
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", comp)
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- scenes
# Each scene paints into a rectangle (x0, y0, x1, y1) of the buffer.
# All shapes are flat and bold so they read at ~300px wide.

def scene_manila(buf, x0, y0, x1, y1):
    """Lead: Trump lands in Manila - plane over a city skyline."""
    vgrad(buf, x0, y0, x1, y1, (168, 214, 244), (250, 226, 178))
    # Sun, top right.
    fill_disc(buf, x1 - 90, y0 + 42, 30, GOLD)
    fill_disc(buf, x1 - 90, y0 + 42, 22, (255, 226, 110))
    # Clouds.
    for (cx, cy, r) in ((x0 + 90, y0 + 34, 22), (x0 + 118, y0 + 28, 16),
                        (x0 + 330, y0 + 22, 18), (x0 + 352, y0 + 30, 13)):
        fill_disc(buf, cx, cy, r, WHITE)
    # Skyline silhouettes, two layers.
    base = y1
    far = [(0, 46, 62), (52, 60, 84), (118, 44, 56), (168, 70, 96),
           (244, 52, 70), (302, 66, 88), (374, 48, 60), (428, 74, 104),
           (508, 56, 76), (570, 64, 92), (640, 48, 64), (694, 72, 98),
           (772, 54, 72), (832, 66, 86), (904, 50, 66), (960, 58, 80)]
    for (dx, w, h) in far:
        fill_rect(buf, x0 + dx, base - h, x0 + dx + w, base, (96, 120, 168))
    near = [(20, 70, 108), (120, 84, 138), (240, 64, 96), (330, 90, 150),
            (450, 72, 112), (550, 96, 158), (680, 70, 104), (780, 88, 140),
            (900, 76, 118)]
    for (dx, w, h) in near:
        fill_rect(buf, x0 + dx, base - h, x0 + dx + w, base, NAVY_LT)
        # Lit windows.
        for wy in range(base - h + 12, base - 10, 18):
            for wx in range(x0 + dx + 10, x0 + dx + w - 8, 16):
                if ((wx * 7 + wy * 13) % 5) < 2:
                    fill_rect(buf, wx, wy, wx + 6, wy + 8, GOLD)
    # Airplane crossing the sky, nose right.
    px, py = x0 + 430, y0 + 62
    fill_rect(buf, px, py - 7, px + 190, py + 7, WHITE)          # fuselage
    fill_triangle(buf, (px + 190, py - 7), (px + 224, py),
                  (px + 190, py + 7), WHITE)                     # nose
    fill_triangle(buf, (px + 8, py - 7), (px - 26, py - 34),
                  (px + 30, py - 7), WHITE)                      # tail fin
    fill_triangle(buf, (px + 70, py + 7), (px + 110, py + 44),
                  (px + 130, py + 7), (228, 236, 248))           # wing
    fill_triangle(buf, (px + 120, py - 7), (px + 150, py - 30),
                  (px + 168, py - 7), (228, 236, 248))           # far wing
    for wx in range(px + 24, px + 180, 18):                      # windows
        fill_rect(buf, wx, py - 3, wx + 8, py + 2, NAVY)
    # Contrail.
    draw_line(buf, x0 + 30, py + 26, px - 30, py + 6, WHITE, 3)
    draw_line(buf, x0 + 30, py + 38, px - 40, py + 18, (240, 244, 250), 2)


def scene_crimea(buf, x0, y0, x1, y1):
    """Ukraine hits the Crimea bridge again - bridge, blast, sea."""
    vgrad(buf, x0, y0, x1, y1, SKY_PALE, (190, 214, 232))
    mid = y0 + (y1 - y0) * 2 // 3
    fill_rect(buf, x0, mid, x1, y1, SEA)
    # Waves.
    for i in range(6):
        wx = x0 + 20 + i * 82
        draw_line(buf, wx, mid + 26 + (i % 3) * 12, wx + 44,
                  mid + 26 + (i % 3) * 12, (120, 190, 225), 3)
    # Bridge deck with a gap blown out at the middle.
    deck_y = y0 + 96
    bx = x0 + (x1 - x0) // 2
    fill_rect(buf, x0 + 6, deck_y, bx - 34, deck_y + 12, (70, 74, 84))
    fill_rect(buf, bx + 34, deck_y, x1 - 6, deck_y + 12, (70, 74, 84))
    # Towers and cables.
    for tx in (x0 + 92, x1 - 92):
        fill_rect(buf, tx - 7, deck_y - 62, tx + 7, deck_y, (52, 56, 66))
        draw_line(buf, tx, deck_y - 62, x0 + 10, deck_y, (120, 124, 132), 2)
        draw_line(buf, tx, deck_y - 62, x1 - 10, deck_y, (120, 124, 132), 2)
    # Explosion at the gap: layered fireball with flame spikes + smoke.
    for (ang, ln) in ((200, 26), (245, 32), (290, 24), (335, 30),
                      (155, 22), (110, 28), (65, 24)):
        a = math.radians(ang)
        tx = int(bx + (46 + ln) * math.cos(a))
        ty = int(deck_y - 6 + (46 + ln) * math.sin(a) * 0.8)
        fill_triangle(buf, (bx, deck_y - 6),
                      (int(bx + 40 * math.cos(a - 0.18)),
                       int(deck_y - 6 + 40 * math.sin(a - 0.18) * 0.8)),
                      (tx, ty), ORANGE)
    fill_disc(buf, bx, deck_y - 6, 46, ORANGE)
    fill_disc(buf, bx, deck_y - 10, 34, RED_LT)
    fill_disc(buf, bx - 4, deck_y - 12, 20, YELLOW)
    fill_disc(buf, bx - 30, deck_y - 44, 16, GREY)
    fill_disc(buf, bx + 6, deck_y - 58, 20, (150, 152, 156))
    fill_disc(buf, bx + 34, deck_y - 40, 13, GREY)
    # Falling debris sparks.
    for (dx, dy) in ((-52, 22), (58, 30), (-70, 4), (74, 8)):
        fill_disc(buf, bx + dx, deck_y + dy, 4, ORANGE)


def scene_hormuz(buf, x0, y0, x1, y1):
    """US-Iran fire at Hormuz - tanker, missile streak, drones."""
    vgrad(buf, x0, y0, x1, y1, (58, 66, 92), (24, 30, 52))
    mid = y0 + (y1 - y0) * 2 // 3
    fill_rect(buf, x0, mid, x1, y1, SEA_DK)
    for i in range(5):
        wx = x0 + 30 + i * 96
        draw_line(buf, wx, mid + 24 + (i % 2) * 14, wx + 48,
                  mid + 24 + (i % 2) * 14, (60, 130, 170), 3)
    # Tanker: dark hull, red containers, bridge tower.
    hx0, hx1 = x0 + 60, x1 - 60
    hy = mid + 8
    fill_rect(buf, hx0, hy, hx1, hy + 26, (24, 24, 30))
    fill_triangle(buf, (hx1, hy), (hx1 + 34, hy + 13), (hx1, hy + 26),
                  (24, 24, 30))
    for i, c in enumerate((RED, GOLD, (40, 120, 180), RED, GOLD)):
        fill_rect(buf, hx0 + 18 + i * 62, hy - 22, hx0 + 72 + i * 62,
                  hy, c)
    fill_rect(buf, hx0 + 8, hy - 44, hx0 + 40, hy - 22, WHITE)
    # Missile streak from top right with flame.
    draw_line(buf, x1 - 60, y0 + 14, x0 + 300, y0 + 84, ORANGE, 5)
    draw_line(buf, x1 - 60, y0 + 14, x0 + 330, y0 + 74, YELLOW, 3)
    fill_disc(buf, x1 - 58, y0 + 16, 12, YELLOW)
    # Two drones (small dark crosses with red lights).
    for (dx, dy) in ((x0 + 90, y0 + 30), (x0 + 150, y0 + 52)):
        fill_rect(buf, dx - 12, dy - 2, dx + 12, dy + 2, INK)
        fill_rect(buf, dx - 2, dy - 10, dx + 2, dy + 10, INK)
        fill_disc(buf, dx, dy, 3, RED_LT)
    # Blast flash on the water.
    add_disc(buf, x0 + 320, mid + 30, 40, ORANGE, 0.8)


def scene_cyclone(buf, x0, y0, x1, y1):
    """Cyclone Akvan - spiral storm over the sea."""
    vgrad(buf, x0, y0, x1, y1, (90, 110, 150), (40, 56, 92))
    mid = y0 + (y1 - y0) * 3 // 4
    fill_rect(buf, x0, mid, x1, y1, (18, 52, 84))
    cx = x0 + (x1 - x0) // 2
    cy = y0 + (y1 - y0) // 2 - 6
    # Spiral arms: dots along an Archimedean spiral, widening outward.
    for k in range(240):
        t = k / 240.0
        ang = t * math.pi * 5.2
        r = 8 + t * 150
        x = int(cx + r * math.cos(ang))
        y = int(cy + r * math.sin(ang) * 0.62)
        shade = 255 - int(t * 70)
        fill_disc(buf, x, y, max(3, int(9 - t * 4)), (shade, shade, shade))
    # Calm eye.
    fill_disc(buf, cx, cy, 16, (30, 44, 74))
    fill_disc(buf, cx, cy, 10, (52, 70, 110))
    # Rain streaks over the sea.
    for i in range(14):
        rx = x0 + 14 + i * 34
        draw_line(buf, rx, mid + 6, rx - 10, mid + 30, (150, 190, 225), 2)


def scene_trade(buf, x0, y0, x1, y1):
    """Canada-China trade deals - two flags over a globe."""
    vgrad(buf, x0, y0, x1, y1, SKY_PALE, (196, 220, 240))
    mid = y0 + (y1 - y0) // 2 + 8
    # Globe, low and centred.
    gx, gy, gr = x0 + (x1 - x0) // 2, mid + 46, 32
    fill_disc(buf, gx, gy, gr, SEA)
    fill_disc(buf, gx - 10, gy - 7, 11, (74, 160, 96))
    fill_disc(buf, gx + 11, gy + 8, 8, (74, 160, 96))
    draw_line(buf, gx - gr, gy, gx + gr, gy, (120, 190, 225), 2)
    # Flag poles.
    pole_y0 = y0 + 12
    fill_rect(buf, x0 + 58, pole_y0, x0 + 62, mid - 26, (80, 82, 88))
    fill_rect(buf, x1 - 62, pole_y0, x1 - 58, mid - 26, (80, 82, 88))
    # Canada flag (left): red-white-red with a red maple diamond.
    fx0, fy0, fw, fh = x0 + 62, pole_y0 + 2, 118, 58
    fill_rect(buf, fx0, fy0, fx0 + 24, fy0 + fh, RED)
    fill_rect(buf, fx0 + 24, fy0, fx0 + fw - 24, fy0 + fh, WHITE)
    fill_rect(buf, fx0 + fw - 24, fy0, fx0 + fw, fy0 + fh, RED)
    mcx, mcy = fx0 + fw // 2, fy0 + fh // 2
    fill_triangle(buf, (mcx, mcy - 14), (mcx - 12, mcy + 2),
                  (mcx + 12, mcy + 2), RED)
    fill_triangle(buf, (mcx, mcy + 11), (mcx - 12, mcy - 2),
                  (mcx + 12, mcy - 2), RED)
    fill_rect(buf, mcx - 2, mcy + 9, mcx + 2, mcy + 16, RED)
    # China flag (right): red with five small yellow stars.
    cx0 = x1 - 62 - fw
    fill_rect(buf, cx0, fy0, cx0 + fw, fy0 + fh, (222, 41, 16))
    for (sx, sy, sr) in ((cx0 + 17, fy0 + 15, 7), (cx0 + 41, fy0 + 9, 4),
                         (cx0 + 52, fy0 + 18, 4), (cx0 + 50, fy0 + 31, 4),
                         (cx0 + 37, fy0 + 37, 4)):
        fill_disc(buf, sx, sy, sr, YELLOW)
    # Gold "deal" check between the flags.
    ccx = x0 + (x1 - x0) // 2
    ccy = fy0 + fh // 2
    fill_disc(buf, ccx, ccy, 15, GOLD)
    draw_line(buf, ccx - 7, ccy, ccx - 2, ccy + 6, INK, 3)
    draw_line(buf, ccx - 2, ccy + 6, ccx + 8, ccy - 6, INK, 3)


# ---------------------------------------------------------------- layout

def card_border(buf, x0, y0, x1, y1, col=NAVY, t=3):
    fill_rect(buf, x0, y0, x1, y0 + t, col)
    fill_rect(buf, x0, y1 - t, x1, y1, col)
    fill_rect(buf, x0, y0, x0 + t, y1, col)
    fill_rect(buf, x1 - t, y0, x1, y1, col)


def number_badge(buf, cx, cy, n):
    fill_disc(buf, cx, cy, 16, RED)
    draw_text_centered(buf, cx, cy - 7, str(n), 2, WHITE)


def story_panel(buf, x0, y0, x1, y1, num, scene, head_lines, sub):
    fill_rect(buf, x0, y0, x1, y1, WHITE)
    card_border(buf, x0, y0, x1, y1)
    art_y1 = y0 + 154
    scene(buf, x0 + 3, y0 + 3, x1 - 3, art_y1)
    number_badge(buf, x0 + 26, y0 + 26, num)
    hy = art_y1 + 10
    for line in head_lines:
        draw_text_centered(buf, (x0 + x1) // 2, hy, line, 3, INK)
        hy += 24
    draw_text_centered(buf, (x0 + x1) // 2, hy + 6, sub, 2, RED)


def paint(buf):
    fill_rect(buf, 0, 0, W, H, PAPER)

    # --- masthead ---
    fill_rect(buf, 0, 0, W, 96, NAVY)
    draw_text_centered(buf, W // 2, 12, "THE WORLD TODAY", 5, WHITE)
    draw_text_centered(buf, W // 2, 60, "WEDNESDAY 18 NOVEMBER 2026",
                       2, GOLD)
    fill_rect(buf, 0, 92, W, 96, RED)

    # --- lead story: Trump in Manila ---
    lx0, ly0, lx1, ly1 = 8, 104, 1016, 424
    fill_rect(buf, lx0, ly0, lx1, ly1, WHITE)
    card_border(buf, lx0, ly0, lx1, ly1)
    scene_manila(buf, lx0 + 3, ly0 + 3, lx1 - 3, ly0 + 188)
    number_badge(buf, lx0 + 26, ly0 + 26, 1)
    draw_text_centered(buf, W // 2, ly0 + 200, "TRUMP LANDS IN MANILA",
                       4, INK)
    draw_text_centered(buf, W // 2, ly0 + 238,
                       "QUAD TALKS IN MANILA, THEN CHINA VISIT", 2, RED)

    # --- four picture panels ---
    cols = (8, 516)
    rows = (432, 708)
    pw, ph = 500, 268
    panels = [
        (2, scene_crimea, ["UKRAINE HITS CRIMEA", "BRIDGE AGAIN"],
         "RUSSIA POUNDS KYIV BRIDGES"),
        (3, scene_hormuz, ["US, IRAN TRADE", "FIRE AT HORMUZ"],
         "US HITS IRGC SITE ON QESHM"),
        (4, scene_cyclone, ["CYCLONE AKVAN", "BEARS DOWN"],
         "SEVERE STORM BY 19 NOV"),
        (5, scene_trade, ["CANADA, CHINA", "EXTEND TRADE DEALS"],
         "XI MEETS CARNEY BEFORE APEC"),
    ]
    for i, (num, scene, heads, sub) in enumerate(panels):
        x0 = cols[i % 2]
        y0 = rows[i // 2]
        story_panel(buf, x0, y0, x0 + pw, y0 + ph, num, scene, heads, sub)

    # --- footer ---
    fill_rect(buf, 0, 984, W, H, NAVY)
    draw_text_centered(buf, W // 2, 999,
                       "THE DAY IN 5 STORIES - NEWS TO 07:10 WIB",
                       2, WHITE)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    buf = bytearray(W * H * 3)
    paint(buf)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, buf)
    print("wrote", path)


if __name__ == "__main__":
    main()
