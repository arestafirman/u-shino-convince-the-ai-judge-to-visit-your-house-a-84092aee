#!/usr/bin/env python3
"""Procedural one-image letter for Make.fun competition
u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.

Draws a 1024x1024 PNG letter (grandmother's kitchen header, the letter
body, footer with signature + stamp + mini chair) entirely with Pillow
shapes and text. Offline, deterministic, no network, no clock.
Writes /output/entry.png
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

HEADER_H = 288          # header illustration band
BODY_TOP = HEADER_H
BODY_BOTTOM = 884       # body band: 596 px
FOOTER_TOP = BODY_BOTTOM

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

# ---- palette (flat warm kitchen) ----
WALL = (243, 222, 174)
WALL_SHADE = (238, 210, 156)
PAPER = (251, 243, 223)
PAPER_EDGE = (232, 214, 180)
INK = (46, 33, 24)
ACCENT = (178, 80, 28)        # burnt orange, for the key numbers
WOOD = (122, 74, 34)
WOOD_DARK = (94, 56, 26)
STOVE = (62, 56, 50)
POT1 = (74, 96, 58)           # leaf green pot
POT2 = (146, 74, 40)          # terracotta pot
POT3 = (58, 74, 96)           # deep blue pot, grandma's, slightly bigger
LID = (214, 192, 150)
SKY = (251, 215, 116)
SUN = (245, 166, 35)
LEAF = (92, 122, 58)
STAMP_RED = (150, 40, 30)
CREAM = (255, 248, 232)

GREETING = "Dear Judge,"

BODY_PARAS = [
    "You have read ten thousand invitations and never once been invited "
    "to sit down. This one is different: there is a chair for you, and "
    "nobody will ask you to score it.",
    "Come to my grandmother's house on Sunday. She has cooked rendang "
    "for 41 years, and for 41 years our family has argued over whose "
    "pot is best. Eleven of us vote every year. This year the vote is "
    "tied, six to five, and the tie-breaker chair is empty.",
    "It has your name on it \u2014 taped, in her handwriting, to the "
    "back of chair number 12. The rendang in pot number 3 is hers. "
    "Taste it, and tell us the truth: she can take it. She has waited "
    "41 years for a judge who cannot be bribed with extra rice.",
    "No scores to file. Just lunch, at noon, and one honest verdict.",
]

CLOSING = "Yours,"


def font(path, size):
    return ImageFont.truetype(path, size)


def is_key_word(word):
    """Words carrying a number get bold + accent: 41, 6-5, 12, 3."""
    return any(ch.isdigit() for ch in word)


# ---------------------------------------------------------------- header
def draw_header(img, d):
    d.rectangle([0, 0, W, HEADER_H], fill=WALL)
    # soft floor shadow band at the bottom of the wall
    d.rectangle([0, HEADER_H - 26, W, HEADER_H], fill=WALL_SHADE)

    # ---- window, right side: Sunday noon sun ----
    wx0, wy0, wx1, wy1 = 688, 26, 972, 196
    d.rectangle([wx0 - 8, wy0 - 8, wx1 + 8, wy1 + 8], fill=WOOD)
    d.rectangle([wx0, wy0, wx1, wy1], fill=SKY)
    # sun + rays
    sx, sy = 830, 108
    for r, col in ((58, (250, 190, 60)), (40, SUN)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        x0 = sx + int(64 * math.cos(a))
        y0 = sy + int(64 * math.sin(a))
        x1 = sx + int(80 * math.cos(a))
        y1 = sy + int(80 * math.sin(a))
        d.line([x0, y0, x1, y1], fill=SUN, width=5)
    # window cross bars
    d.rectangle([wx0, (wy0 + wy1) // 2 - 4, wx1, (wy0 + wy1) // 2 + 4], fill=WOOD)
    d.rectangle([(wx0 + wx1) // 2 - 4, wy0, (wx0 + wx1) // 2 + 4, wy1], fill=WOOD)
    # sunbeam polygons spilling left onto the wall
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(700, 196), (560, 288), (430, 288), (640, 196)],
               fill=(255, 236, 160, 70))
    bd.polygon([(880, 196), (800, 288), (700, 288), (820, 196)],
               fill=(255, 236, 160, 55))
    img.paste(Image.alpha_composite(img.convert("RGBA"), beam).convert("RGB"),
              (0, 0))

    # ---- wall clock showing 12:00 (kept clear of pot 1 below) ----
    cx, cy, cr = 118, 80, 44
    d.ellipse([cx - cr - 6, cy - cr - 6, cx + cr + 6, cy + cr + 6], fill=WOOD_DARK)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=CREAM)
    for i in range(12):
        import math
        a = math.radians(i * 30)
        x0 = cx + int((cr - 8) * math.sin(a))
        y0 = cy - int((cr - 8) * math.cos(a))
        x1 = cx + int((cr - 2) * math.sin(a))
        y1 = cy - int((cr - 2) * math.cos(a))
        d.line([x0, y0, x1, y1], fill=INK, width=3 if i % 3 == 0 else 1)
    # both hands point straight up: 12:00
    d.line([cx, cy, cx, cy - cr + 18], fill=INK, width=4)   # minute hand
    d.line([cx, cy, cx, cy - cr + 30], fill=INK, width=6)   # hour hand
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=ACCENT)

    # ---- hanging herbs, left of the window ----
    for hx, hy, ln in ((330, 60, 46), (372, 52, 58), (414, 62, 40)):
        d.line([hx, hy - 14, hx, hy], fill=WOOD_DARK, width=2)
        for k in range(4):
            yy = hy + k * (ln // 4)
            d.ellipse([hx - 9, yy, hx + 9, yy + 12], fill=LEAF)

    # ---- stove + three numbered pots ----
    d.rectangle([0, 232, W, HEADER_H], fill=WOOD)          # counter top
    d.rectangle([0, 240, W, HEADER_H], fill=WOOD_DARK)     # counter front
    d.rectangle([0, 232, W, 240], fill=(164, 110, 58))
    # stove slab
    d.rectangle([36, 214, 664, 240], fill=STOVE)
    for bx in (130, 330, 520):
        d.ellipse([bx - 52, 218, bx + 52, 238], fill=(30, 27, 24))

    def pot(x0, y_bottom, w, h, body_col, number):
        x1 = x0 + w
        y0 = y_bottom - h
        # handles
        d.rectangle([x0 - 14, y0 + 14, x0, y0 + 26], fill=WOOD_DARK)
        d.rectangle([x1, y0 + 14, x1 + 14, y0 + 26], fill=WOOD_DARK)
        # body + lid
        d.rounded_rectangle([x0, y0 + 12, x1, y_bottom], radius=10, fill=body_col)
        d.ellipse([x0 - 4, y0 - 6, x1 + 4, y0 + 18], fill=LID)
        d.ellipse([x0 + w // 2 - 8, y0 - 14, x0 + w // 2 + 8, y0 + 2], fill=WOOD_DARK)
        # number badge
        fnum = font(SERIF_BOLD, 34 if w < 150 else 38)
        bx, by = x0 + w // 2, y0 + 12 + (h - 12) // 2 + 4
        d.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=CREAM)
        tw = d.textlength(number, font=fnum)
        d.text((bx - tw / 2, by - 20), number, font=fnum, fill=INK)
        return y0

    pot(78, 216, 118, 82, POT1, "1")
    pot(268, 216, 118, 82, POT2, "2")
    pot3_top = pot(436, 216, 158, 100, POT3, "3")   # grandma's pot, bigger

    # ---- steam curls above pot 3: smooth wavy lines ----
    import math
    steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for sx0 in (486, 516, 546):
        pts = []
        for k in range(25):
            yy = pot3_top - 6 - k * 3
            xx = sx0 + 6 * math.sin(k * 0.55)
            pts.append((xx, yy))
        sd.line(pts, fill=(255, 255, 255, 170), width=5, joint="curve")
    img.paste(Image.alpha_composite(img.convert("RGBA"), steam).convert("RGB"),
              (0, 0))


# ---------------------------------------------------------------- body
def wrap_paragraph(text, freg, fbold, max_w):
    """Greedy wrap; returns list of lines, each a list of (word, font, col)."""
    space_w = freg.getlength(" ")
    lines, cur, cur_w = [], [], 0.0
    for word in text.split(" "):
        if is_key_word(word):
            f, col = fbold, ACCENT
        else:
            f, col = freg, INK
        ww = f.getlength(word)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(word, f, col)], ww
        else:
            cur.append((word, f, col))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def layout_body(max_w, body_h):
    """Pick the largest body size (30-33px) whose lines fit body_h."""
    for size in (33, 32, 31, 30):
        freg = font(SERIF, size)
        fbold = font(SERIF_BOLD, size)
        fgreet = font(SERIF_BOLD, 44)
        greet_h = int(44 * 1.25)
        lines = []
        for para in BODY_PARAS:
            lines.extend(wrap_paragraph(para, freg, fbold, max_w))
        n_lines = len(lines)
        for spacing in (1.30, 1.24, 1.18):
            total = greet_h + 16 + int(n_lines * size * spacing) \
                + (len(BODY_PARAS) - 1) * 12 + 18 + int(30 * 1.3)
            if total <= body_h:
                return size, spacing, fgreet, freg, fbold, lines
    # fallback: smallest size, tightest spacing
    size = 30
    freg = font(SERIF, size)
    fbold = font(SERIF_BOLD, size)
    fgreet = font(SERIF_BOLD, 44)
    lines = []
    for para in BODY_PARAS:
        lines.extend(wrap_paragraph(para, freg, fbold, max_w))
    return size, 1.18, fgreet, freg, fbold, lines


def draw_body(img, d):
    d.rectangle([0, BODY_TOP, W, BODY_BOTTOM], fill=PAPER)
    d.line([0, BODY_TOP, W, BODY_TOP], fill=PAPER_EDGE, width=2)
    d.line([0, BODY_BOTTOM - 1, W, BODY_BOTTOM - 1], fill=PAPER_EDGE, width=2)

    margin = 56
    max_w = W - 2 * margin
    inner_h = BODY_BOTTOM - BODY_TOP - 20 - 14
    size, spacing, fgreet, freg, fbold, lines = layout_body(max_w, inner_h)
    fclosing = font(SERIF_ITALIC, 30)

    y = BODY_TOP + 20
    d.text((margin, y), GREETING, font=fgreet, fill=INK)
    y += int(44 * 1.25) + 14

    # re-walk paragraphs to keep paragraph gaps
    line_h = int(size * spacing)
    para_idx = 0
    counts = []
    for para in BODY_PARAS:
        counts.append(len(wrap_paragraph(para, freg, fbold, max_w)))
    flat = lines
    pos = 0
    for pi, cnt in enumerate(counts):
        for _ in range(cnt):
            x = margin
            for j, (word, f, col) in enumerate(flat[pos]):
                if j > 0:
                    x += freg.getlength(" ")
                d.text((x, y), word, font=f, fill=col)
                x += f.getlength(word)
            y += line_h
            pos += 1
        y += 12  # paragraph gap
    # closing line
    d.text((margin, y - 2), CLOSING, font=fclosing, fill=INK)


# ---------------------------------------------------------------- footer
def draw_footer(img, d):
    d.rectangle([0, FOOTER_TOP, W, H], fill=(246, 232, 200))
    d.line([0, FOOTER_TOP, W, FOOTER_TOP], fill=PAPER_EDGE, width=2)

    # signature
    fsig = font(SERIF_ITALIC, 52)
    d.text((56, FOOTER_TOP + 14), "Ares", font=fsig, fill=INK)
    fsub = font(SERIF_ITALIC, 21)
    d.text((58, FOOTER_TOP + 78), "the grandson who sets the table",
           font=fsub, fill=(90, 66, 44))

    # stamp: rotated rounded rectangle, "HOUSE No. 12 - SUNDAY, NOON"
    stamp = Image.new("RGBA", (330, 92), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, 325, 87], radius=10,
                         outline=STAMP_RED, width=3)
    sd.rounded_rectangle([10, 10, 319, 81], radius=7,
                         outline=STAMP_RED, width=1)
    f1 = font(SERIF_BOLD, 26)
    f2 = font(SERIF_BOLD, 22)
    t1, t2 = "HOUSE No. 12", "SUNDAY, NOON"
    sd.text(((330 - sd.textlength(t1, font=f1)) / 2, 12), t1,
            font=f1, fill=STAMP_RED)
    sd.text(((330 - sd.textlength(t2, font=f2)) / 2, 46), t2,
            font=f2, fill=STAMP_RED)
    stamp = stamp.rotate(-4, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (400, FOOTER_TOP + 22), stamp)

    # mini chair no. 12, bottom-right, with a JUDGE name tag
    cx0, cy0 = 872, FOOTER_TOP + 6
    # backrest posts + slats
    d.rectangle([cx0, cy0, cx0 + 8, cy0 + 78], fill=WOOD)
    d.rectangle([cx0 + 82, cy0, cx0 + 90, cy0 + 78], fill=WOOD)
    d.rectangle([cx0, cy0, cx0 + 90, cy0 + 10], fill=WOOD)
    d.rectangle([cx0, cy0 + 28, cx0 + 90, cy0 + 38], fill=WOOD)
    # seat + legs
    d.rectangle([cx0 - 6, cy0 + 78, cx0 + 96, cy0 + 90], fill=WOOD)
    d.rectangle([cx0, cy0 + 90, cx0 + 8, cy0 + 128], fill=WOOD_DARK)
    d.rectangle([cx0 + 82, cy0 + 90, cx0 + 90, cy0 + 128], fill=WOOD_DARK)
    d.rectangle([cx0 + 8, cy0 + 108, cx0 + 82, cy0 + 114], fill=WOOD_DARK)
    # name tag taped to the backrest
    tag = Image.new("RGBA", (76, 30), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rectangle([0, 0, 75, 29], fill=(255, 252, 240), outline=INK, width=1)
    ftag = font(SERIF_BOLD, 17)
    tt = "JUDGE"
    td.text(((76 - td.textlength(tt, font=ftag)) / 2, 5), tt,
            font=ftag, fill=INK)
    tag = tag.rotate(-6, expand=True, resample=Image.BICUBIC)
    img.paste(tag, (cx0 + 8, cy0 + 38), tag)


def main():
    os.makedirs("/output", exist_ok=True)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(img, d)
    # rebind draw after header pastes (paste keeps same image; d stays valid)
    d = ImageDraw.Draw(img)
    draw_body(img, d)
    d = ImageDraw.Draw(img)
    draw_footer(img, d)
    img.save(OUT, format="PNG", optimize=True)
    print("saved", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
