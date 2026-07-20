#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate favicon + Open Graph share image from the logo."""
import os
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

SITE = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים\site"
IMG = os.path.join(SITE, "assets", "images")
LOGO = os.path.join(IMG, "misc", "logo.png")

BRAND_SKY_TOP = (137, 205, 240)
BRAND_SKY_BOTTOM = (75, 150, 205)
BRAND_NAVY = (20, 40, 70)
BRAND_YELLOW = (247, 183, 49)

def rtl(t):
    return get_display(t)

# --- favicon ---
logo = Image.open(LOGO).convert("RGBA")
sq = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
# circular sky background
d = ImageDraw.Draw(sq)
d.ellipse([0, 0, 512, 512], fill=(117, 190, 233, 255))
lw = 400
lh = int(logo.height * (lw / logo.width))
logo_r = logo.resize((lw, lh), Image.LANCZOS)
sq.paste(logo_r, ((512 - lw) // 2, (512 - lh) // 2), logo_r)
sq.save(os.path.join(SITE, "favicon.png"))
for size in (16, 32, 48, 180):
    sq.resize((size, size), Image.LANCZOS).save(os.path.join(SITE, f"favicon-{size}.png"))
sq.resize((180, 180), Image.LANCZOS).save(os.path.join(SITE, "apple-touch-icon.png"))
print("favicon done")

# --- OG image 1200x630 ---
W, H = 1200, 630
base = Image.new("RGB", (W, H), BRAND_SKY_TOP)
mask = Image.new("L", (1, H), 0)
for y in range(H):
    mask.putpixel((0, y), int(255 * (y / H)))
mask = mask.resize((W, H))
top = Image.new("RGB", (W, H), BRAND_SKY_TOP)
bottom = Image.new("RGB", (W, H), BRAND_SKY_BOTTOM)
base = Image.composite(bottom, top, mask)

lw = 260
lh = int(logo.height * (lw / logo.width))
logo_r = logo.resize((lw, lh), Image.LANCZOS)
base.paste(logo_r, ((W - lw) // 2, 60), logo_r)

d = ImageDraw.Draw(base)
font_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 58)
font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 32)

title = rtl("עלוני פרשת שבוע מותאמים לבתי ספר")
tw = d.textlength(title, font=font_title)
d.text(((W - tw) / 2, 60 + lh + 40), title, font=font_title, fill=BRAND_NAVY)

sub = rtl("בחרו עיצוב וכיוון - והצטרפו לחודש התנסות חינם")
sw = d.textlength(sub, font=font_sub)
d.text(((W - sw) / 2, 60 + lh + 120), sub, font=font_sub, fill=(30, 55, 90))

# small badge
badge = rtl("חודש התנסות חינם")
font_badge = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 30)
bw = d.textlength(badge, font=font_badge)
pad = 24
bx0 = (W - bw) / 2 - pad
by0 = 60 + lh + 190
d.rounded_rectangle([bx0, by0, bx0 + bw + 2 * pad, by0 + 60], radius=30, fill=BRAND_YELLOW)
d.text(((W - bw) / 2, by0 + 14), badge, font=font_badge, fill=(50, 30, 0))

base.save(os.path.join(SITE, "og-image.jpg"), quality=90)
print("OG image done")
