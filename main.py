#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Stdlib-only procedural drawing. No Pillow, no system fonts, no file
reads, no network, no clock. Writes a single 1024x1024 PNG to
/output/entry.png with a hand-written PNG encoder (struct + zlib).

Letter text is verbatim from the teardown SPEC (768 characters total,
counted per sentence). Artwork: grandmother's kitchen header (stove
with 3 numbered pots, wall clock at 12:00, Sunday-noon window light),
the letter body, and a footer with signature, stamp, and the
tie-breaker chair No. 12 with a JUDGE name tag.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
INK = (43, 33, 24)        # dark brown ink
PAPER = (251, 243, 223)    # letter paper cream
WALL = (242, 223, 184)     # header wall warm cream
BG = (234, 217, 176)       # page background tan
ACCENT = (180, 85, 31)     # burnt orange accent (numbers, stamp)
GREEN = (78, 122, 58)      # leaf green
WOOD = (107, 74, 42)       # chair / window frame brown
DARKWOOD = (62, 42, 26)    # stove dark brown
TRIM = (201, 168, 106)     # paper border gold-tan
SKY = (168, 207, 224)      # window sky
SUN = (246, 201, 69)       # noon sun
POT1 = (201, 106, 43)      # pot 1 orange
POT2 = (78, 122, 58)       # pot 2 green
POT3 = (180, 85, 31)       # pot 3 burnt orange (hero, bigger)
STEAM = (253, 248, 236)    # steam white
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            if ((xx - cx) * (xx - cx)) / (rx * rx) + ((yy - cy) * (yy - cy)) / (ry * ry) <= 1.0:
                px(xx, yy, c)


def get_px(x, y):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        return (buf[i], buf[i + 1], buf[i + 2])
    return (0, 0, 0)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 chars, '#' = ink. Written from scratch.
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "$": ("..#..", ".####.", "#.#.#.", ".###..", "..#.#.", ".####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ",": (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ";": (".....", "..#..", ".....", ".....", "..#..", "..#..", ".#..."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.#..", "#....", ".###."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "\\": ("#....", "#....", ".#...", ".#...", "..#..", "..#..", "...#."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "^": ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "`": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".###.", "#....", "#....", "#...#", ".###."),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "{": ("...##.", "..#..", "..#..", ".##..", "..#..", "..#..", "...##."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "}": (".##..", "..#..", "..#..", "..##.", "..#..", "..#..", ".##.."),
    "~": (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
}

ADV = 6  # glyph advance in font units (5 + 1 gap)


def glyph_w(text, scale, bold=False):
    per = ADV + (1 if bold else 0)
    return len(text) * per * scale


def draw_glyph(x, y, ch, scale, color, bold=False):
    """Draw one glyph with 2x supersampling: render the 5x7 bitmap into
    a 2x-resolution mask, then average each 2x2 block when blending onto
    the canvas, so glyph edges are smooth instead of pixel-jagged.
    Output size is identical to the non-supersampled version."""
    g = FONT.get(ch)
    if g is None:
        g = FONT["?"]
    s2 = scale * 2
    cols = 6 if bold else 5
    stride = cols * s2
    mask = bytearray(stride * 7 * s2)
    for row in range(7):
        bits = g[row]
        for col in range(5):
            if bits[col] == "#":
                for yy in range(row * s2, (row + 1) * s2):
                    base = yy * stride + col * s2
                    for xx in range(s2):
                        mask[base + xx] = 1
                if bold:
                    for yy in range(row * s2, (row + 1) * s2):
                        base = yy * stride + (col + 1) * s2
                        for xx in range(s2):
                            mask[base + xx] = 1
    for oy in range(7 * scale):
        my = oy * 2
        for ox in range(cols * scale):
            mx = ox * 2
            cov = (mask[my * stride + mx] + mask[my * stride + mx + 1]
                   + mask[(my + 1) * stride + mx]
                   + mask[(my + 1) * stride + mx + 1]) * 0.25
            if cov:
                old = get_px(x + ox, y + oy)
                px(x + ox, y + oy,
                   (int(old[0] + (color[0] - old[0]) * cov),
                    int(old[1] + (color[1] - old[1]) * cov),
                    int(old[2] + (color[2] - old[2]) * cov)))


def draw_word(x, y, word, scale, color, bold=False):
    cx = x
    per = (ADV + (1 if bold else 0)) * scale
    for ch in word:
        draw_glyph(cx, y, ch, scale, color, bold)
        cx += per
    return cx - x


def word_base(word):
    return word.strip(".,:;!?")


# ---------------------------------------------------------------- letter
# Verbatim from SPEC section 3. Sentence lengths sum to 768 characters.
SENTENCES = [
    "Dear Judge,",
    "You have read ten thousand invitations and never once been invited to sit down.",
    "This one is different: there is a chair for you, and nobody will ask you to score it.",
    "Come to my grandmother's house on Sunday.",
    "She has cooked rendang for 41 years, and for 41 years our family has argued over whose pot is best.",
    "Eleven of us vote every year.",
    "This year the vote is tied, six to five, and the tie-breaker chair is empty.",
    "It has your name on it \u2014 taped, in her handwriting, to the back of chair number 12.",
    "The rendang in pot number 3 is hers.",
    "Taste it, and tell us the truth: she can take it.",
    "She has waited 41 years for a judge who cannot be bribed with extra rice.",
    "No scores to file. Just lunch, at noon, and one honest verdict.",
    "Yours,",
    "Ares \u2014 the grandson who sets the table",
]
LETTER_CHARS = sum(len(s) for s in SENTENCES)  # 768

PARAS = [
    SENTENCES[0],
    " ".join(SENTENCES[1:3]),
    " ".join(SENTENCES[3:7]),
    " ".join(SENTENCES[7:11]),
    SENTENCES[11],
    SENTENCES[12],
    SENTENCES[13],
]

ACCENT_WORDS = {"41", "12", "3", "six", "five"}


def is_accent(word, prev_base):
    base = word_base(word)
    if base in ACCENT_WORDS:
        return True
    return base == "to" and prev_base == "six"


def wrap_para(text, max_w, scale):
    """Greedy word wrap. Returns list of lines; each line is a list of
    (word, accent) tuples."""
    words = text.split(" ")
    lines = []
    cur = []
    cur_w = 0
    prev_base = ""
    space_w = ADV * scale
    for word in words:
        accent = is_accent(word, prev_base)
        prev_base = word_base(word)
        ww = glyph_w(word, scale, bold=accent)
        add = ww if not cur else space_w + ww
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur = [(word, accent)]
            cur_w = ww
        else:
            cur.append((word, accent))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_line(x, y, line_words, scale):
    cx = x
    space_w = ADV * scale
    for i, (word, accent) in enumerate(line_words):
        if i:
            cx += space_w
        color = ACCENT if accent else INK
        w = draw_word(cx, y, word, scale, color, bold=accent)
        cx += w
    return cx


# ---------------------------------------------------------------- header
def draw_header():
    rect(0, 0, W, 280, WALL)
    # window, left: Sunday-noon light
    rect(56, 30, 216, 184, WOOD)
    rect(68, 42, 192, 160, SKY)
    circle(150, 108, 30, SUN)
    for k in range(8):
        a = k * math.pi / 4
        line(int(150 + 38 * math.cos(a)), int(108 + 38 * math.sin(a)),
             int(150 + 52 * math.cos(a)), int(108 + 52 * math.sin(a)),
             SUN, 3)
    rect(160, 42, 8, 160, WOOD)   # mullion vertical
    rect(68, 116, 192, 8, WOOD)   # mullion horizontal
    rect(48, 214, 232, 14, WOOD)  # sill
    # wall clock, 12:00
    circle(512, 128, 54, WOOD)
    circle(512, 128, 47, PAPER)
    for k in range(12):
        a = k * math.pi / 6
        line(int(512 + 40 * math.cos(a)), int(128 + 40 * math.sin(a)),
             int(512 + 46 * math.cos(a)), int(128 + 46 * math.sin(a)),
             INK, 2)
    line(512, 128, 512, 92, INK, 4)   # minute hand -> 12
    line(512, 128, 512, 104, INK, 6)  # hour hand -> 12
    circle(512, 128, 5, ACCENT)
    # stove, right, with 3 numbered pots (lids, handles, burners)
    rect(632, 182, 348, 14, DARKWOOD)  # stove top slab
    rect(640, 196, 332, 84, (90, 58, 38))  # stove body
    rect(660, 232, 292, 44, (74, 48, 30))  # oven door
    rect(660, 232, 292, 4, (40, 26, 16))   # oven door top edge
    rect(760, 244, 92, 6, (40, 26, 16))    # oven handle
    rect(660, 214, 60, 8, DARKWOOD)    # burner knobs
    rect(740, 214, 60, 8, DARKWOOD)
    rect(900, 214, 60, 8, DARKWOOD)
    # burner rings on the stove top, peeking out around each pot
    ellipse(686, 186, 50, 5, (40, 26, 16))
    ellipse(796, 186, 50, 5, (40, 26, 16))
    ellipse(918, 186, 62, 5, (40, 26, 16))
    # pot 1: body 80x48
    rect(634, 148, 14, 8, DARKWOOD)    # left handle
    rect(726, 148, 14, 8, DARKWOOD)    # right handle
    rect(646, 134, 80, 48, POT1)
    ellipse(686, 134, 44, 10, (168, 84, 32))  # lid
    circle(686, 122, 5, DARKWOOD)      # lid knob
    draw_word(677, 150, "1", 3, WHITE)
    # pot 2: body 80x48
    rect(744, 148, 14, 8, DARKWOOD)
    rect(836, 148, 14, 8, DARKWOOD)
    rect(756, 134, 80, 48, POT2)
    ellipse(796, 134, 44, 10, (62, 97, 48))   # lid
    circle(796, 122, 5, DARKWOOD)      # lid knob
    draw_word(787, 150, "2", 3, WHITE)
    # pot 3: hero, body 108x64 = 35% wider and 33% taller than pots 1-2
    rect(850, 138, 16, 9, DARKWOOD)
    rect(972, 138, 16, 9, DARKWOOD)
    rect(864, 118, 108, 64, POT3)
    ellipse(918, 118, 58, 12, (147, 63, 22))  # lid
    circle(918, 104, 6, DARKWOOD)      # lid knob
    draw_word(906, 140, "3", 4, WHITE)
    # steam wisps above pot 3's lid
    for col, phase in ((898, 0.0), (922, 2.1), (946, 4.2)):
        for step in range(9):
            yy = 96 - step * 7
            xx = col + int(7 * math.sin(step * 0.9 + phase))
            circle(xx, yy, 5, STEAM)


# ---------------------------------------------------------------- footer
def draw_signature(x0, y0, color):
    """Handwritten-style 'Ares': flowing polyline strokes, slanted,
    drawn with thick lines instead of the pixel bitmap font."""
    strokes = [
        # capital A: up-stroke, down-stroke, crossbar
        [(78, 950), (96, 908), (108, 902), (120, 926), (134, 950)],
        [(90, 932), (116, 930)],
        # r: small loop
        [(140, 948), (142, 928), (152, 924), (161, 932), (158, 948)],
        # e: loop
        [(164, 948), (172, 924), (184, 924), (189, 937), (179, 946), (166, 948)],
        # s + flourish tail
        [(193, 948), (203, 928), (213, 934), (205, 948), (217, 952),
         (236, 944), (256, 950)],
    ]
    for pts in strokes:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            line(ax, ay, bx, by, color, 3)


def draw_footer():
    # signature (hand-drawn strokes) + flourish underline
    draw_signature(72, 916, INK)
    line(72, 958, 264, 958, ACCENT, 3)
    # stamp: double-ruled box (outer + inner border) so it reads as a stamp
    rect(320, 904, 240, 64, PAPER)
    rect(320, 904, 240, 3, ACCENT)
    rect(320, 965, 240, 3, ACCENT)
    rect(320, 904, 3, 64, ACCENT)
    rect(557, 904, 3, 64, ACCENT)
    rect(328, 912, 224, 2, ACCENT)
    rect(328, 958, 224, 2, ACCENT)
    rect(328, 912, 2, 48, ACCENT)
    rect(550, 912, 2, 48, ACCENT)
    t1 = "HOUSE No. 12"
    t2 = "SUNDAY, NOON"
    draw_word(440 - glyph_w(t1, 2) // 2, 916, t1, 2, ACCENT)
    draw_word(440 - glyph_w(t2, 2) // 2, 940, t2, 2, ACCENT)
    # mini chair No. 12, bottom right, with JUDGE name tag
    rect(852, 906, 10, 104, WOOD)   # back posts
    rect(946, 906, 10, 104, WOOD)
    rect(852, 906, 104, 10, WOOD)   # top rail
    rect(852, 936, 104, 8, WOOD)    # middle rail
    # name tag taped on the backrest
    rect(866, 914, 76, 20, PAPER)
    rect(866, 914, 76, 2, TRIM)
    rect(866, 932, 76, 2, TRIM)
    draw_word(904 - glyph_w("JUDGE", 2) // 2, 918, "JUDGE", 2, INK)
    # seat + legs
    rect(838, 976, 132, 12, WOOD)
    rect(844, 988, 10, 22, WOOD)
    rect(954, 988, 10, 22, WOOD)
    rect(884, 988, 8, 22, WOOD)
    rect(918, 988, 8, 22, WOOD)
    # "12" on a dark badge pinned to the seat front: strong contrast
    rect(880, 974, 52, 22, DARKWOOD)
    draw_word(892, 979, "12", 2, WHITE, bold=True)


# ---------------------------------------------------------------- PNG out
def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    row = bytearray(W * 3 + 1)
    for y in range(H):
        row[0] = 0
        row[1:] = buf[y * W * 3:(y + 1) * W * 3]
        raw += row
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    rect(0, 0, W, H, BG)
    draw_header()
    # letter paper
    rect(32, 272, 960, 612, PAPER)
    rect(32, 272, 960, 4, TRIM)
    rect(32, 880, 960, 4, TRIM)
    rect(32, 272, 4, 612, TRIM)
    rect(988, 272, 4, 612, TRIM)
    # greeting, larger
    gx, gy = 56, 296
    draw_word(gx, gy, PARAS[0], 5, INK)
    line(gx, gy + 44, gx + glyph_w(PARAS[0], 5), gy + 44, ACCENT, 3)
    # body paragraphs, scale 3
    y = gy + 60
    body_x = 56
    body_w = 912
    line_h = 25
    para_gap = 8
    for i, para in enumerate(PARAS[1:]):
        lines = wrap_para(para, body_w, 3)
        for ln in lines:
            draw_line(body_x, y, ln, 3)
            y += line_h
        if i < len(PARAS[1:]) - 1:
            y += para_gap
    draw_footer()
    n = write_png(OUT)
    return n


if __name__ == "__main__":
    main()
