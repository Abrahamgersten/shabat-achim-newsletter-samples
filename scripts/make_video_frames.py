#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compose 1280x720 base frames (image + Hebrew caption bar) for each video
scene. ffmpeg then applies Ken Burns zoom + fades to these frames."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bidi.algorithm import get_display

SITE = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים\site"
IMG = os.path.join(SITE, "assets", "images")
OUT = os.path.join(SITE, "scripts", "video_frames")
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"

BRAND_NAVY = (25, 51, 82)
BRAND_YELLOW = (247, 183, 49)
BRAND_SKY = (117, 190, 233)


def rtl(text):
    return get_display(text)


def wrap_rtl_lines(draw, text, font, max_width):
    words = text.split(" ")
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        if draw.textlength(" ".join(trial), font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def cover_fit(im, w, h):
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale) + 1, int(ih * scale) + 1
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def make_scene(name, image_path, caption, subcaption=None, dim=0.28):
    base = Image.new("RGB", (W, H), BRAND_NAVY)
    if image_path:
        im = Image.open(image_path).convert("RGB")
        im = cover_fit(im, W, H)
        base.paste(im, (0, 0))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # bottom gradient scrim for caption legibility
    grad_h = 300
    for i in range(grad_h):
        a = int(dim * 255 * (i / grad_h) + (1 - dim) * 0)
        a = int(230 * (i / grad_h) ** 1.4)
        od.line([(0, H - grad_h + i), (W, H - grad_h + i)], fill=(10, 20, 35, a))
    base = Image.alpha_composite(base.convert("RGBA"), overlay)
    d = ImageDraw.Draw(base)

    font_cap = ImageFont.truetype(FONT_BOLD, 54)
    font_sub = ImageFont.truetype(FONT_REG, 32)

    lines = wrap_rtl_lines(d, caption, font_cap, W - 160)
    total_h = len(lines) * 66 + (28 + 40 if subcaption else 0)
    y = H - 70 - total_h
    for ln in lines:
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_cap)
        d.text(((W - tw) / 2, y), txt, font=font_cap, fill=(255, 255, 255, 255))
        y += 66
    if subcaption:
        y += 10
        txt = rtl(subcaption)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, y), txt, font=font_sub, fill=(247, 200, 110, 255))

    base.convert("RGB").save(os.path.join(OUT, f"{name}.png"), quality=95)
    print("scene:", name)


def make_title_card(name, logo_path, title, subtitle):
    base = Image.new("RGB", (W, H), BRAND_SKY)
    # soft radial-ish gradient using vertical blend navy->sky
    top = Image.new("RGB", (W, H), (137, 205, 240))
    bottom = Image.new("RGB", (W, H), (75, 150, 205))
    mask = Image.new("L", (1, H), color=0)
    for y in range(H):
        mask.putpixel((0, y), int(255 * (y / H)))
    mask = mask.resize((W, H))
    base = Image.composite(bottom, top, mask)
    d = ImageDraw.Draw(base)

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lw = 300
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.LANCZOS)
        base.paste(logo, ((W - lw) // 2, 90), logo)

    font_title = ImageFont.truetype(FONT_BOLD, 62)
    font_sub = ImageFont.truetype(FONT_REG, 34)
    ty = 90 + (lh if logo_path else 0) + 50
    txt = rtl(title)
    tw = d.textlength(txt, font=font_title)
    d.text(((W - tw) / 2, ty), txt, font=font_title, fill=(20, 40, 70))
    ty += 80
    for ln in subtitle.split("\n"):
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, ty), txt, font=font_sub, fill=(30, 55, 90))
        ty += 46

    base.save(os.path.join(OUT, f"{name}.png"), quality=95)
    print("title card:", name)


def make_closing_card(name, logo_path, title, subtitle):
    base = Image.new("RGB", (W, H), BRAND_NAVY)
    top = Image.new("RGB", (W, H), (20, 40, 70))
    bottom = Image.new("RGB", (W, H), (35, 70, 110))
    mask = Image.new("L", (1, H), color=0)
    for y in range(H):
        mask.putpixel((0, y), int(255 * (y / H)))
    mask = mask.resize((W, H))
    base = Image.composite(top, bottom, mask)
    d = ImageDraw.Draw(base)

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lw = 260
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.LANCZOS)
        base.paste(logo, ((W - lw) // 2, 70), logo)
    else:
        lh = 0

    font_title = ImageFont.truetype(FONT_BOLD, 58)
    font_sub = ImageFont.truetype(FONT_REG, 34)
    ty = 70 + lh + 55
    for ln in title.split("\n"):
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_title)
        d.text(((W - tw) / 2, ty), txt, font=font_title, fill=BRAND_YELLOW)
        ty += 74
    ty += 16
    for ln in subtitle.split("\n"):
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, ty), txt, font=font_sub, fill=(230, 238, 245))
        ty += 44

    base.save(os.path.join(OUT, f"{name}.png"), quality=95)
    print("closing card:", name)


if __name__ == "__main__":
    logo = os.path.join(IMG, "misc", "logo.png")

    make_title_card(
        "00_title", logo,
        "עלון פרשת שבוע לבית הספר שלכם",
        "בעיצוב אישי, עם התוכן שלכם, כל שבוע",
    )

    make_scene(
        "01_vertical",
        os.path.join(IMG, "covers", "vertical-1-p1.webp"),
        "עלון אנכי", "מעוצב במיוחד עבור בית הספר שלכם",
    )
    make_scene(
        "02_horizontal",
        os.path.join(IMG, "covers", "horizontal-2-p1.webp"),
        "או עלון אופקי, מתקפל לשניים",
    )
    make_scene(
        "03_styles",
        os.path.join(IMG, "design-styles", "style-2.webp"),
        "עשרות כיוונים עיצוביים לבחירה",
        "השם, הלוגו, הצבעים והדמויות - הכל אישי",
    )
    make_scene(
        "04_sections",
        os.path.join(IMG, "sections", "section-12.webp"),
        "דבר תורה, חידות, קומיקס ועוד",
        "מדורים תורניים ברמה גבוהה בכל שבוע",
    )
    make_scene(
        "05_sharing",
        os.path.join(IMG, "sharing", "sharing-01.webp"),
        "מקום קבוע לתוכן ולתמונות מבית הספר",
        "כל מה שקורה אצלכם, מגיע הביתה",
    )
    make_scene(
        "06_bw",
        os.path.join(IMG, "covers", "color-and-bw-p1.webp"),
        "קובץ צבעוני דיגיטלי, וקובץ להדפסה שחור-לבן",
        "כל שבוע, שני הקבצים אצלכם",
    )
    make_scene(
        "07_levels",
        os.path.join(IMG, "covers", "age-older-p1.webp"),
        "אפשר גם להתאים לפי שכבות גיל",
        "עלון נפרד לצעירים ולבוגרים",
    )
    make_scene(
        "08_activity1",
        os.path.join(IMG, "sharing", "sharing-04.webp"),
        "לא רק עלון - חוויה חינוכית שלמה",
        "כל חודש: מבצע ערכי חדש בבית הספר",
    )
    make_scene(
        "09_activity2",
        os.path.join(IMG, "sharing", "sharing-02.webp"),
        "ופעילות שממשיכה גם בבית, במשפחה",
        "מפעילים תלמידים והורים יחד, סביב שולחן השבת",
    )

    make_closing_card(
        "99_cta", logo,
        "בואו תנסו חודש חינם",
        "בחרו את הכיוון שאתם אוהבים\nונחזור אליכם להתחיל",
    )

    print("DONE")
