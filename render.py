#!/usr/bin/env python3
"""Render the passport spread of the Republic of Sorellia, a country that
does not exist, as a single 1024x768 PNG.

Sorellia is an invented Mediterranean island republic; its language,
Sorellian, is written here in an Italian-flavoured form. Everything on
the spread agrees with everything else:

  * passport S8472916, issued 03 JUN 2021 in Valmarina, ten-year validity;
  * the Kordavia visa sticker (single entry, by sea, autumn 2021) covers
    the September 2021 ferry trip stamped on the facing page;
  * every stamp falls inside the passport's validity, and the trips pair
    up: out of Sorellia, into the neighbour, back again;
  * the holder, a Valmarina-born marine biologist, carries the Island
    Residents' embarkation-tax concession in her observations -- the one
    piece of paperwork that says what kind of place Sorellia is.

Drawn at twice size with Pillow and downscaled for smooth lines. The
shipped entry program (main.py) needs only the standard library.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2                      # supersampling factor
W, H = 1024 * S, 768 * S   # the spread, drawn at 2048x1536
PAGE = 512                 # one page wide, in final pixels; seam at x=PAGE

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

INK = (32, 38, 46)
NAVY = (24, 52, 92)
TEAL = (13, 74, 84)
GOLD = (166, 124, 42)
RED = (146, 30, 30)
FAINT = (110, 118, 112)
LABEL = (88, 96, 92)
PAPER_L = (246, 240, 222)
PAPER_R = (248, 243, 228)


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def spaced(draw, xy, text, fnt, fill, tracking=6, centered=False):
    """Letterspaced text drawn from final-pixel xy; returns its width."""
    x, y = xy[0] * S, xy[1] * S
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * S * (len(text) - 1)
    if centered:
        x -= total / 2
    cx = x
    for ch, w in zip(text, widths):
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += w + tracking * S
    return total / S


# ---------------------------------------------------------------- guilloche
def guilloche(size, colour, rings=5, phase=0.0):
    """A rosette of wavy concentric rings on its own transparent layer.
    `size` is in final pixels."""
    px = int(size * S)
    layer = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = px / 2
    for i in range(rings):
        r0 = px * 0.48 * (1 - i / (rings + 1.5))
        pts = []
        for a in range(0, 361, 2):
            t = math.radians(a)
            r = r0 * (1 + 0.045 * math.sin(9 * t + phase + i * 0.9)
                      + 0.022 * math.sin(23 * t - phase))
            pts.append((c + r * math.cos(t), c + r * math.sin(t)))
        d.line(pts, fill=colour + (50,), width=max(2, S))
    return layer


def blend(rgb, base, alpha):
    """The colour `rgb` at opacity alpha/255 laid over `base`, opaque."""
    a = alpha / 255
    return tuple(int(rgb[i] * a + base[i] * (1 - a)) for i in range(3))


def wave_border(img, box, colour):
    """Faint wavy rules along the top and bottom of a page, drawn on a
    layer and composited (PIL's draw does not blend fill colours)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = [v * S for v in box]
    for r in range(3):
        off = r * 7 * S
        top, bot = [], []
        for x in range(int(x0), int(x1), 8):
            t = (x - x0) / max(1, (x1 - x0))
            top.append((x, y0 + off + 5 * S * math.sin(t * 22 + r)))
            bot.append((x, y1 - off - 5 * S * math.sin(t * 22 + r)))
        draw.line(top, fill=colour + (55,), width=2 * S)
        draw.line(bot, fill=colour + (55,), width=2 * S)
    img.alpha_composite(layer)


# ------------------------------------------------------------------- emblem
def emblem(size, ink=NAVY, accent=GOLD, alpha=255):
    """The Sorellian seal: a striped lighthouse over waves, a rising sun
    behind it, light beams to either side, and the republic's name and
    motto -- MAR E LIBERTA -- lettered around the ring. `size` is final px."""
    px = int(size * S)
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = px / 2
    d.ellipse([px * 0.03, px * 0.03, px * 0.97, px * 0.97],
              outline=ink + (alpha,), width=max(2, px // 42))
    d.ellipse([px * 0.10, px * 0.10, px * 0.90, px * 0.90],
              outline=ink + (alpha,), width=max(1, px // 90))
    d.ellipse([px * 0.25, px * 0.25, px * 0.75, px * 0.75],
              outline=accent + (alpha,), width=max(1, px // 64))
    d.pieslice([c - px * 0.16, c - px * 0.19, c + px * 0.16, c + px * 0.13],
               180, 360, fill=accent + (alpha,))
    tw = px * 0.075
    top, base = c - px * 0.185, c + px * 0.125
    d.polygon([(c - tw * 0.55, top), (c + tw * 0.55, top),
               (c + tw, base), (c - tw, base)], fill=ink + (alpha,))
    for yy in (0.32, 0.58, 0.84):
        y = top + (base - top) * yy
        half = tw * (0.55 + 0.45 * yy)
        d.line([c - half, y, c + half, y], fill=(248, 243, 228) + (alpha,),
               width=max(2, px // 46))
    d.rectangle([c - tw * 0.62, top - px * 0.052, c + tw * 0.62, top],
                fill=accent + (alpha,))
    for sgn in (-1, 1):
        d.polygon([(c + sgn * tw * 0.6, top - px * 0.026),
                   (c + sgn * px * 0.20, top - px * 0.055),
                   (c + sgn * px * 0.20, top + px * 0.002)],
                  fill=accent + (int(alpha * 0.5),))
    for r in range(3):
        yy = base + px * 0.032 + r * px * 0.042
        pts = []
        for x in range(int(c - px * 0.19), int(c + px * 0.19), 4):
            t = (x - (c - px * 0.19)) / (px * 0.38)
            pts.append((x, yy + px * 0.015 * math.sin(t * 12.6 + r * 1.7)))
        d.line(pts, fill=ink + (alpha,), width=max(2, px // 52))
    ring_f = ImageFont.truetype(SERIF_B, int(px * 0.068))
    _ring_text(img, "REPUBBLICA DI SORELLIA", c, px * 0.408, ring_f,
               ink + (alpha,), top=True)
    _ring_text(img, "MAR E LIBERTA", c, px * 0.408, ring_f,
               ink + (alpha,), top=False)
    return img


def _ring_text(img, text, c, radius, fnt, fill, top=True):
    """Letters along the seal's ring. On the top arc each glyph's head
    points outward; on the bottom arc its head points inward, toward the
    centre, so both lines read left to right (PIL rotates clockwise on
    screen for positive angles, hence the signs below)."""
    n = len(text)
    for i, ch in enumerate(text):
        frac = (i / max(1, n - 1) - 0.5) if n > 1 else 0
        ang = frac * (2.55 if top else 1.95)
        if top:
            a = -math.pi / 2 + ang
            rot = -math.degrees(ang)
        else:
            a = math.pi / 2 - ang
            rot = -math.degrees(ang)
        x, y = c + radius * math.cos(a), c + radius * math.sin(a)
        tile = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((50, 50), ch, font=fnt, fill=fill, anchor="mm")
        tile = tile.rotate(rot, resample=Image.BICUBIC, center=(50, 50))
        img.alpha_composite(tile, (int(x - 50), int(y - 50)))


# ------------------------------------------------------------------- stamps
def stamp_layer(w, h, draw_fn, angle, opacity=205):
    """w, h in final pixels; the stamp is inked, rotated and roughened."""
    layer = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, w * S, h * S, opacity)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    a = layer.split()[3]
    noise = Image.effect_noise(layer.size, 38).convert("L")
    a = Image.composite(a, a.point(lambda v: int(v * 0.5)),
                        noise.point(lambda v: 255 if v > 198 else 0))
    layer.putalpha(a)
    return layer


def rect_stamp(country, place, kind, rgb):
    def fn(d, w, h, opacity):
        fill = rgb + (opacity,)
        d.rounded_rectangle([4 * S, 4 * S, w - 4 * S, h - 4 * S], radius=9 * S,
                            outline=fill, width=3 * S)
        d.rounded_rectangle([10 * S, 10 * S, w - 10 * S, h - 10 * S], radius=6 * S,
                            outline=fill, width=S)
        d.text((w / 2, 15 * S), country, font=font(SANS_B, 15), fill=fill,
               anchor="ma")
        d.text((w / 2, 38 * S), kind, font=font(SANS_B, 21), fill=fill, anchor="ma")
        d.text((w / 2, 68 * S), place, font=font(SANS, 12.5), fill=fill, anchor="ma")
    return fn


def oval_stamp(country, place, kind, rgb):
    def fn(d, w, h, opacity):
        fill = rgb + (opacity,)
        d.ellipse([4 * S, 4 * S, w - 4 * S, h - 4 * S], outline=fill, width=3 * S)
        d.ellipse([10 * S, 10 * S, w - 10 * S, h - 10 * S], outline=fill, width=S)
        d.text((w / 2, h * 0.15), country, font=font(SANS_B, 13.5), fill=fill,
               anchor="ma")
        d.text((w / 2, h * 0.36), kind, font=font(SANS_B, 15), fill=fill,
               anchor="ma")
        d.text((w / 2, h * 0.63), place, font=font(SANS, 11), fill=fill, anchor="ma")
    return fn


# ----------------------------------------------------------------------- MRZ
def check_digit(field):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(field):
        v = int(ch) if ch.isdigit() else (0 if ch == "<" else ord(ch) - 55)
        total += v * weights[i % 3]
    return str(total % 10)


def build_mrz():
    doc = "S8472916<"                    # passport number, padded to 9
    dob, expiry = "910314", "310603"
    personal = "9103142214<<<<"         # personal number, padded to 14
    line1 = "P<SRLFERRAN<<LUCIA<MARIA"
    line1 += "<" * (44 - len(line1))
    line2 = (doc + check_digit(doc) + "SRL" + dob + check_digit(dob) + "F"
             + expiry + check_digit(expiry) + personal + check_digit(personal))
    line2 += check_digit(doc + check_digit(doc) + dob + check_digit(dob)
                         + expiry + check_digit(expiry)
                         + personal + check_digit(personal))
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# --------------------------------------------------------------------- main
def main():
    random.seed(20211121)
    img = Image.new("RGBA", (W, H), PAPER_R + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    d.rectangle([0, 0, PAGE * S, H], fill=PAPER_L)
    for i in range(14):  # soft shadow down the centre seam, colours pre-blended
        a = int(64 * (1 - i / 14))
        d.line([PAGE * S - i * S, 0, PAGE * S - i * S, H],
               fill=blend((90, 84, 60), PAPER_L, a), width=S)
        d.line([PAGE * S + i * S, 0, PAGE * S + i * S, H],
               fill=blend((90, 84, 60), PAPER_R, int(a * 0.6)), width=S)
    d.line([PAGE * S, 0, PAGE * S, H], fill=blend((70, 64, 44), PAPER_R, 130),
           width=S)
    for x in (3, 8):     # page edges
        d.line([x * S, 0, x * S, H], fill=(120, 112, 84, 70), width=S)
        d.line([W - x * S, 0, W - x * S, H], fill=(120, 112, 84, 70), width=S)

    for (cx, cy, sz, col) in ((150, 120, 300, TEAL), (880, 660, 340, GOLD),
                              (1180, 640, 380, TEAL), (1930, 130, 300, GOLD),
                              (1560, 420, 560, TEAL)):
        ros = guilloche(sz // S, col, rings=6, phase=cx * 0.01)
        img.alpha_composite(ros, (int((cx - sz / 2)), int((cy - sz / 2))))
    wave_border(img, (36, 26, 476, 742), TEAL)
    wave_border(img, (548, 26, 988, 742), TEAL)

    wm = emblem(430, alpha=17)   # faint seal watermark behind the data fields
    img.alpha_composite(wm, (int(1330), int(300)))

    build_left_page(img, d)
    build_right_page(img, d)

    grain = Image.effect_noise((W, H), 7).convert("L")
    img = Image.composite(ImageEnhance.Brightness(img).enhance(1.012), img,
                          grain.point(lambda v: 26 if v > 140 else 0))
    img = img.convert("RGB").resize((1024, 768), Image.LANCZOS)
    out = os.path.join(HERE, "artwork.png")
    img.save(out, optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


def build_left_page(img, d):
    spaced(d, (256, 40), "VISAS", font(SERIF_B, 25), NAVY, tracking=10,
           centered=True)
    d.text((256 * S, 74 * S), "Visti  ·  Visas and stamps of neighbouring states",
           font=font(SANS, 12.5), fill=LABEL, anchor="ma")
    d.line([70 * S, 102 * S, 442 * S, 102 * S], fill=NAVY + (150,), width=2 * S)
    d.text((478 * S, 40 * S), "24", font=font(SANS, 12), fill=FAINT, anchor="ma")

    # ---- Kordavia visa sticker, autumn 2021: it covers the ferry trip below
    visa = Image.new("RGBA", (460 * S, 196 * S), (0, 0, 0, 0))
    vd = ImageDraw.Draw(visa)
    vd.rounded_rectangle([2 * S, 2 * S, 458 * S, 194 * S], radius=12 * S,
                         fill=(238, 232, 196, 255), outline=GOLD + (255,),
                         width=4 * S)
    vd.rounded_rectangle([11 * S, 11 * S, 449 * S, 185 * S], radius=8 * S,
                         outline=TEAL + (200,), width=2 * S)
    visa.alpha_composite(guilloche(120, TEAL, rings=5), (int(322 * S), int(58 * S)))
    vd.text((24 * S, 16 * S), "KORDAVIA", font=font(SERIF_B, 27), fill=NAVY)
    vd.text((24 * S, 50 * S), "VISA · VIZA · SINGLE ENTRY",
            font=font(SANS_B, 13), fill=TEAL)
    rows = [("HOLDER", "FERRAN LUCIA MARIA   ·   PASSPORT S8472916"),
            ("VALID", "10 SEP 2021 — 09 DEC 2021"),
            ("ENTRY", "ONE — BY SEA VIA PORT KORDA ONLY")]
    yy = 82
    for lab, val in rows:
        vd.text((24 * S, yy * S), lab, font=font(SANS_B, 11), fill=LABEL)
        vd.text((86 * S, (yy - 2) * S), val, font=font(SANS_B, 13.5), fill=INK)
        yy += 30
    vd.text((24 * S, 168 * S), "VISA No. KV 0093147", font=font(SANS, 11.5),
            fill=LABEL)
    vd.text((436 * S, 164 * S), "FEE PAID · 25 KRD", font=font(SANS_B, 12),
            fill=RED, anchor="ra")
    visa = visa.rotate(2.0, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(visa, (int(22 * S), int(118 * S)))

    BLUE = (38, 74, 148)
    PURPLE = (96, 54, 128)
    stamps = [
        # (draw fn, w, h, x, y, angle) -- x, y in final pixels
        (rect_stamp("KORDAVIA · PORT KORDA", "BY SEA · CONTROL 4",
                    "ENTRY  18 SEP 2021", BLUE), 268, 96, 26, 348, 3),
        (oval_stamp("SORELLIA", "VALMARINA FERRY PORT",
                    "EXIT  18 SEP 2021", NAVY), 226, 118, 282, 344, -7),
        (oval_stamp("SORELLIA", "VALMARINA FERRY PORT",
                    "ENTRY  26 SEP 2021", RED), 226, 118, 40, 490, 6),
        (rect_stamp("KORDAVIA · PORT KORDA", "BY SEA · CONTROL 2",
                    "EXIT  26 SEP 2021", BLUE), 268, 96, 236, 496, -4),
        (rect_stamp("SELUNIA · TESSIN INTL", "AIRPORT · CONTROL 11",
                    "ENTRY  14 MAY 2022", PURPLE), 268, 96, 26, 634, 2),
        (oval_stamp("SELUNIA", "TESSIN INTL AIRPORT",
                    "EXIT  21 MAY 2022", PURPLE), 204, 108, 304, 630, -9),
    ]
    for fn, w, h, x, y, ang in stamps:
        img.alpha_composite(stamp_layer(w, h, fn, ang), (int(x * S), int(y * S)))


def field(d, x, y, label, value, val_size=16.5, w=None):
    """One data field on the right page; x, y are final pixels from the
    page's left edge (the caller adds the page offset)."""
    d.text((x * S, y * S), label.upper(), font=font(SANS, 10), fill=LABEL)
    d.text((x * S, (y + 14) * S), value, font=font(SANS_B, val_size), fill=INK)
    if w:
        d.line([x * S, (y + 38) * S, (x + w) * S, (y + 38) * S],
               fill=(150, 150, 138, 120), width=S)


def build_right_page(img, d):
    ox = PAGE  # right page origin in final pixels

    def X(v):
        return ox + v

    # ---- header: seal, country name, document name
    img.alpha_composite(emblem(112), (int(X(24) * S), int(20 * S)))
    spaced(d, (X(152), 32), "REPUBLIC OF SORELLIA", font(SERIF_B, 25), NAVY,
           tracking=1)
    spaced(d, (X(153), 68), "REPUBBLICA DI SORELLIA", font(SANS, 14), TEAL,
           tracking=6)
    d.text((X(153) * S, 94 * S), "A republic of islands in the Sorellian Sea",
           font=font(SERIF_I, 12.5), fill=LABEL)
    d.line([X(152) * S, 120 * S, X(460) * S, 120 * S], fill=GOLD + (255,),
           width=2 * S)
    spaced(d, (X(152), 130), "PASSPORT", font(SERIF_B, 19), INK, tracking=7)
    d.text((X(322) * S, 133 * S), "·  PASSAPORTO", font=font(SERIF, 14.5),
           fill=LABEL)
    cx, cy = X(452) * S, 140 * S   # e-passport chip mark
    d.rounded_rectangle([cx - 13 * S, cy - 9 * S, cx + 13 * S, cy + 9 * S],
                        radius=3 * S, outline=GOLD + (255,), width=2 * S)
    d.ellipse([cx - 4 * S, cy - 4 * S, cx + 4 * S, cy + 4 * S],
              outline=GOLD + (255,), width=2 * S)
    d.line([cx - 13 * S, cy, cx - 4 * S, cy], fill=GOLD + (255,), width=2 * S)
    d.line([cx + 4 * S, cy, cx + 13 * S, cy], fill=GOLD + (255,), width=2 * S)

    # ---- type / code / number
    field(d, X(28), 168, "Type · Tipo", "P", w=46)
    field(d, X(96), 168, "Code · Codice", "SRL", w=58)
    d.text((X(182) * S, 168 * S), "PASSPORT NO. · PASSAPORTO N.",
           font=font(SANS, 10), fill=LABEL)
    d.text((X(182) * S, 182 * S), "S8472916", font=font(SANS_B, 18), fill=RED)
    d.line([X(182) * S, 206 * S, X(300) * S, 206 * S],
           fill=(150, 150, 138, 120), width=S)

    # ---- portrait and its hologram
    photo = Image.open(os.path.join(HERE, "assets", "portrait.jpg")).convert("RGB")
    photo = ImageOps.fit(photo, (150 * S, 196 * S), Image.LANCZOS)
    photo = ImageEnhance.Color(photo).enhance(0.94)
    px, py = X(28) * S, 222 * S
    img.paste(photo, (px, py))
    d.rectangle([px, py, px + 150 * S, py + 196 * S], outline=(90, 90, 80, 255),
                width=2 * S)
    d.rectangle([px + 4 * S, py + 4 * S, px + 146 * S, py + 192 * S],
                outline=(255, 255, 255, 90), width=S)
    holo = Image.new("RGBA", (46 * S, 46 * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(holo)
    for i, col in enumerate(((198, 160, 60), (70, 140, 140), (198, 160, 60))):
        r = (20 - i * 5) * S
        hd.ellipse([23 * S - r, 23 * S - r, 23 * S + r, 23 * S + r],
                   outline=col + (150,), width=2 * S)
    hd.text((23 * S, 23 * S), "SRL", font=font(SANS_B, 8), fill=(120, 92, 30, 200),
            anchor="mm")
    img.alpha_composite(holo, (int(px + 118 * S), int(py + 158 * S)))

    # signature under the portrait
    d.text((X(32) * S, 426 * S), "Lucia Ferran", font=font(SERIF_I, 19),
           fill=(40, 44, 60))
    d.line([X(28) * S, 452 * S, X(178) * S, 452 * S],
           fill=(150, 150, 138, 120), width=S)
    d.text((X(28) * S, 456 * S), "SIGNATURE · FIRMA", font=font(SANS, 8.5),
           fill=LABEL)

    # small physical-description fields under the signature
    field(d, X(28), 486, "Sex", "F", val_size=13)
    field(d, X(88), 486, "Eyes", "GREEN", val_size=13)
    field(d, X(28), 528, "Hair", "DARK BROWN", val_size=12.5)
    field(d, X(124), 528, "Height", "168 CM", val_size=12.5)

    # ---- main column of fields, right of the portrait
    mx = X(196)
    rows = [("Surname · Cognome", "FERRAN"),
            ("Given names · Nomi", "LUCIA MARIA"),
            ("Nationality · Cittadinanza", "SORELLIAN"),
            ("Date of birth · Data di nascita", "14 MAR 1991"),
            ("Place of birth · Luogo di nascita", "VALMARINA"),
            ("Personal No. · N. personale", "910314-2214"),
            ("Profession · Professione", "MARINE BIOLOGIST"),
            ("Residence · Residenza", "VALMARINA, ISOLA GRANDE")]
    for i, (lab, val) in enumerate(rows):
        field(d, mx, 222 + i * 45, lab, val,
              val_size=15 if i >= 6 else 16.5, w=270)

    # ---- issue / expiry / authority, full width
    field(d, X(28), 592, "Date of issue · Data di rilascio", "03 JUN 2021", w=196)
    field(d, X(262), 592, "Date of expiry · Data di scadenza", "03 JUN 2031",
          w=196)
    field(d, X(28), 644, "Authority · Autorita",
          "MINISTERO DELL'INTERNO — UFFICIO PASSAPORTI, VALMARINA",
          val_size=12, w=430)

    # ---- observations: the telling detail of Sorellian paperwork
    oy = 686
    d.text((X(28) * S, oy * S), "OBSERVATIONS · ANNOTAZIONI",
           font=font(SANS_B, 10), fill=TEAL)
    d.text((X(28) * S, (oy + 15) * S),
           "Holder resident in the Valmarina island district: exempt from the",
           font=font(SANS, 11), fill=INK)
    d.text((X(28) * S, (oy + 29) * S),
           "embarkation tax — Island Residents' Concession, Law 14/2019.",
           font=font(SANS, 11), fill=INK)

    # ---- machine-readable zone, along the foot of the data page
    line1, line2 = build_mrz()
    d.rectangle([X(14) * S, 736 * S, X(476) * S, 766 * S], fill=(252, 250, 240, 255))
    f_mrz = ImageFont.truetype(MONO, int(15.5 * S))
    d.text((X(245) * S, 738 * S), line1, font=f_mrz, fill=(20, 20, 20), anchor="ma")
    d.text((X(245) * S, 752 * S), line2, font=f_mrz, fill=(20, 20, 20), anchor="ma")

    # perforated passport number up the right edge
    for i, ch in enumerate("S8472916"):
        d.text((X(478) * S, (250 + i * 26) * S), ch, font=font(MONO_B, 12),
               fill=RED + (180,), anchor="ma")


if __name__ == "__main__":
    main()
