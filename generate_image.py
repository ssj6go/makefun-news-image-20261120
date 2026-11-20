#!/usr/bin/env python3
"""Render the news-image-20261120 entry: one 1024x1024 PNG summing up the
world news of Friday, 20 November 2026.

Original artwork drawn with PIL primitives (no downloaded images). The
submitted program (main.ts) only copies the rendered entry.png, so this
script's only job is producing that file deterministically.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (250, 246, 239)      # warm off-white page
INK = (20, 20, 20)           # near-black text
SUB = (62, 62, 62)           # sub-line grey
FAINT = (122, 122, 122)      # location-line grey
CARD = (255, 255, 255)       # panel card
BORDER = (216, 210, 196)     # panel border
NAVY = (15, 30, 58)          # masthead / ticker band
GOLD = (227, 179, 65)        # masthead accent

DEJAVU = "/usr/share/fonts/truetype/dejavu/"
F_TITLE = ImageFont.truetype(DEJAVU + "DejaVuSerif-Bold.ttf", 44)
F_DATE = ImageFont.truetype(DEJAVU + "DejaVuSans-Bold.ttf", 56)
F_TAG = ImageFont.truetype(DEJAVU + "DejaVuSans-Bold.ttf", 18)
F_HEAD = ImageFont.truetype(DEJAVU + "DejaVuSans-Bold.ttf", 30)
F_HEAD_SMALL = ImageFont.truetype(DEJAVU + "DejaVuSans-Bold.ttf", 27)
F_SUB = ImageFont.truetype(DEJAVU + "DejaVuSans.ttf", 21)
F_LOC = ImageFont.truetype(DEJAVU + "DejaVuSans-Bold.ttf", 16)
F_TICK = ImageFont.truetype(DEJAVU + "DejaVuSans.ttf", 19)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    import math
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- icons
def icon_flags(d, cx, cy):
    """Three flags stacked vertically: US, China, Russia -- the summit."""
    fw, fh, gap = 64, 40, 8
    x0 = cx - fw // 2
    y0 = cy - (3 * fh + 2 * gap) // 2
    # US: stripes + blue canton
    for i in range(5):
        d.rectangle([x0, y0 + i * fh / 5, x0 + fw, y0 + (i + 1) * fh / 5],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x0, y0, x0 + fw * 0.45, y0 + fh * 0.55], fill=(30, 50, 110))
    for dx in (6, 14, 22):
        for dy in (5, 13):
            d.ellipse([x0 + dx, y0 + dy, x0 + dx + 3, y0 + dy + 3],
                      fill="white")
    # China: red + yellow star
    y1 = y0 + fh + gap
    d.rectangle([x0, y1, x0 + fw, y1 + fh], fill=(222, 41, 16))
    d.polygon(star_points(x0 + 16, y1 + 15, 10, 4), fill=(255, 222, 0))
    # Russia: white / blue / red bands
    y2 = y1 + fh + gap
    for i, col in enumerate([(255, 255, 255), (0, 87, 184), (213, 0, 50)]):
        d.rectangle([x0, y2 + i * fh / 3, x0 + fw, y2 + (i + 1) * fh / 3],
                    fill=col)
    for y in (y0, y1, y2):
        d.rectangle([x0, y, x0 + fw, y + fh], outline=(90, 90, 90), width=1)


def icon_scales(d, cx, cy):
    """Scales of justice -- the ICJ ruling."""
    col = (107, 79, 161)
    d.line([cx, cy - 42, cx, cy + 44], fill=col, width=6)
    d.line([cx - 44, cy - 30, cx + 44, cy - 30], fill=col, width=6)
    d.ellipse([cx - 6, cy - 50, cx + 6, cy - 38], fill=col)
    for sx in (-44, 44):
        d.line([cx + sx, cy - 30, cx + sx - 16, cy + 6], fill=col, width=3)
        d.line([cx + sx, cy - 30, cx + sx + 16, cy + 6], fill=col, width=3)
        d.line([cx + sx, cy - 30, cx + sx, cy + 6], fill=col, width=3)
        d.pieslice([cx + sx - 20, cy - 6, cx + sx + 20, cy + 26],
                   start=0, end=180, fill=col)
    d.line([cx - 22, cy + 44, cx + 22, cy + 44], fill=col, width=6)


def icon_bridge(d, cx, cy):
    """A bridge under attack -- Kyiv."""
    slate = (70, 80, 95)
    d.rectangle([cx - 52, cy + 8, cx + 52, cy + 18], fill=slate)      # deck
    d.arc([cx - 40, cy - 14, cx + 40, cy + 26], start=180, end=360,
          fill=slate, width=6)                                       # arch
    d.rectangle([cx - 46, cy + 18, cx - 38, cy + 48], fill=slate)     # pillars
    d.rectangle([cx + 38, cy + 18, cx + 46, cy + 48], fill=slate)
    d.line([cx - 52, cy + 48, cx + 52, cy + 48], fill=slate, width=4)  # water
    d.polygon(star_points(cx, cy - 26, 26, 10, n=8), fill=(245, 176, 65))
    d.polygon(star_points(cx, cy - 26, 14, 6, n=8), fill=(231, 76, 60))
    d.ellipse([cx - 34, cy - 48, cx - 20, cy - 34], fill=(160, 160, 160))
    d.ellipse([cx + 22, cy - 44, cx + 34, cy - 32], fill=(160, 160, 160))


def icon_tower(d, cx, cy):
    """A skyscraper cracked by a missile -- Riyadh."""
    bld = (41, 65, 110)
    d.polygon([(cx - 22, cy + 48), (cx - 22, cy - 44), (cx - 10, cy - 52),
               (cx + 10, cy - 52), (cx + 22, cy - 44), (cx + 22, cy + 48)],
              fill=bld)
    for row in range(6):
        for col_i in range(3):
            wx = cx - 14 + col_i * 11
            wy = cy - 30 + row * 12
            d.rectangle([wx, wy, wx + 6, wy + 7], fill=(170, 205, 235))
    # impact burst + crack
    d.polygon(star_points(cx + 24, cy - 18, 20, 8, n=8), fill=(245, 176, 65))
    d.polygon(star_points(cx + 24, cy - 18, 11, 5, n=8), fill=(231, 76, 60))
    crack = [(cx + 20, cy - 12), (cx + 8, cy - 2), (cx + 16, cy + 8),
             (cx + 4, cy + 20), (cx + 12, cy + 32)]
    d.line(crack, fill=(20, 20, 20), width=3)
    d.line([cx - 30, cy + 48, cx + 30, cy + 48], fill=(70, 80, 95), width=4)


def icon_cyclone(d, cx, cy):
    """A spiral storm with rain -- Cyclone Akvan."""
    import math
    teal = (14, 124, 123)
    pts = []
    for t in range(0, 540, 6):
        a = math.radians(t)
        r = 4 + t * 0.085
        pts.append((cx + r * math.cos(a), cy - 6 + r * math.sin(a) * 0.85))
    d.line(pts, fill=teal, width=7)
    d.ellipse([cx - 7, cy - 13, cx + 7, cy + 1], fill=(255, 255, 255),
              outline=teal, width=3)
    for i, rx in enumerate((-38, -14, 12, 36)):
        x = cx + rx
        d.line([x, cy + 26 + (i % 2) * 6, x - 6, cy + 44 + (i % 2) * 6],
               fill=(70, 140, 200), width=4)


def icon_chart(d, cx, cy):
    """A falling market chart -- the sell-off."""
    d.line([cx - 48, cy + 40, cx + 48, cy + 40], fill=(90, 90, 90), width=4)
    d.line([cx - 48, cy + 40, cx - 48, cy - 44], fill=(90, 90, 90), width=4)
    pts = [(cx - 42, cy - 30), (cx - 18, cy - 18), (cx + 2, cy - 26),
           (cx + 22, cy + 2), (cx + 44, cy + 28)]
    d.line(pts, fill=(192, 57, 43), width=6)
    d.polygon([(cx + 44, cy + 28), (cx + 32, cy + 24), (cx + 40, cy + 14)],
              fill=(192, 57, 43))
    for x, y in pts[:-1]:
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(192, 57, 43))


def icon_layer(fn, size=200, max_w=118, max_h=186):
    """Draw an icon on its own layer, then scale its actual content to fit
    the panel's icon column (never overflowing into the text)."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fn(d, size // 2, size // 2)
    bbox = layer.getbbox()
    if not bbox:
        return layer
    content = layer.crop(bbox)
    scale = min(max_w / content.width, max_h / content.height, 1.6)
    new = (max(1, int(content.width * scale)),
           max(1, int(content.height * scale)))
    return content.resize(new, Image.LANCZOS)


ICONS = {
    "summit": icon_flags,
    "justice": icon_scales,
    "kyiv": icon_bridge,
    "riyadh": icon_tower,
    "cyclone": icon_cyclone,
    "markets": icon_chart,
}

# tag, headline, sub-line, location, accent colour, icon key
PANELS = [
    ("DIPLOMACY", "THREE POWERS SIGN PEACE PACT",
     "Trump, Xi & Putin's joint declaration in Shenzhen",
     "SHENZHEN, CHINA", (31, 111, 235), "summit"),
    ("JUSTICE", "WORLD COURT FINDS GENOCIDE",
     "ICJ: Myanmar guilty over the Rohingya",
     "THE HAGUE, NETHERLANDS", (107, 79, 161), "justice"),
    ("WAR IN UKRAINE", "KYIV BRIDGES HIT",
     "Russian overnight strikes kill 8, injure 28",
     "KYIV, UKRAINE", (192, 57, 43), "kyiv"),
    ("MIDDLE EAST", "MISSILE HITS RIYADH TOWER",
     "Houthi strike damages PIF skyscraper",
     "RIYADH, SAUDI ARABIA", (202, 111, 30), "riyadh"),
    ("WEATHER", "CYCLONE AKVAN HITS INDIA",
     "300,000 evacuated as storm hits Odisha",
     "ODISHA, INDIA", (14, 124, 123), "cyclone"),
    ("ECONOMY", "MARKETS TUMBLE",
     "Nikkei \u22124.8%; S&P 500 down a 6th day",
     "NEW YORK & TOKYO", (93, 109, 126), "markets"),
]

TICKER = ("ALSO TODAY: Kenya's last Ebola patient goes home  \u2022  "
          "EU & UK seal reset deal in Brussels  \u2022  "
          "COP31 drops fossil-fuel phase-out")


def draw_panel(img, d, px, py, panel):
    tag, head, sub, loc, accent, icon_key = panel
    pw, ph = 488, 240
    d.rectangle([px, py, px + pw, py + ph], fill=CARD, outline=BORDER, width=2)
    d.rectangle([px, py, px + pw, py + 8], fill=accent)
    # tinted icon column so the left of the panel is not dead white space
    d.rounded_rectangle([px + 12, py + 22, px + 138, py + ph - 14],
                        radius=10, fill=(247, 243, 236))
    layer = icon_layer(ICONS[icon_key])
    img.paste(layer, (px + 75 - layer.width // 2, py + 124 - layer.height // 2),
              mask=layer)
    tx = px + 150
    tw = px + pw - 14 - tx
    d.text((tx, py + 24), tag, font=F_TAG, fill=accent)
    font = F_HEAD
    lines = wrap(d, head, font, tw)
    if len(lines) > 2:
        font = F_HEAD_SMALL
        lines = wrap(d, head, font, tw)
    y = py + 50
    for line in lines[:2]:
        d.text((tx, y), line, font=font, fill=INK)
        y += 36 if font is F_HEAD else 32
    d.line([tx, y + 6, tx + 46, y + 6], fill=accent, width=3)
    y += 16
    for line in wrap(d, sub, F_SUB, tw)[:3]:
        d.text((tx, y), line, font=F_SUB, fill=SUB)
        y += 27
    d.text((tx, py + ph - 28), loc, font=F_LOC, fill=FAINT)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 170], fill=NAVY)
    d.line([0, 170, W, 170], fill=GOLD, width=4)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=F_TITLE)
    d.text(((W - tw) / 2, 22), title, font=F_TITLE, fill=(255, 255, 255))
    date = "FRIDAY, 20 NOVEMBER 2026"
    dw = d.textlength(date, font=F_DATE)
    d.text(((W - dw) / 2, 84), date, font=F_DATE, fill=GOLD)

    # ---- six panels: 2 cols x 3 rows ----
    xs = [16, 520]
    ys = [186, 442, 698]
    for i, panel in enumerate(PANELS):
        draw_panel(img, d, xs[i % 2], ys[i // 2], panel)

    # ---- ticker ----
    d.rectangle([0, 954, W, H], fill=NAVY)
    d.line([0, 954, W, 954], fill=GOLD, width=3)
    lines = wrap(d, TICKER, F_TICK, W - 48)
    y = 962
    for line in lines[:2]:
        lw = d.textlength(line, font=F_TICK)
        d.text(((W - lw) / 2, y), line, font=F_TICK, fill=(235, 235, 235))
        y += 25

    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
