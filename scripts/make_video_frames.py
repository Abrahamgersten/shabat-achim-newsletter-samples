#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compose 1280x720 base frames (image + Hebrew caption card) for each video
scene. ffmpeg then applies Ken Burns motion + fades + music to these frames.

Newsletter/document scenes use CONTAIN fit (full page visible, blurred
backdrop) - photo scenes use COVER fit (full-bleed crop is fine for photos)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bidi.algorithm import get_display

SITE = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים\site"
IMG = os.path.join(SITE, "assets", "images")
OUT = os.path.join(SITE, "scripts", "video_frames")
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720
FONT_FILE = os.path.join(SITE, "scripts", "fonts", "Heebo-Bold.ttf")
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

BRAND_NAVY = (25, 51, 82)
BRAND_YELLOW = (247, 183, 49)
BRAND_SKY = (117, 190, 233)


def font(weight, size):
    f = ImageFont.truetype(FONT_FILE, size)
    f.set_variation_by_name(weight)
    return f


def rtl(text):
    return get_display(text)


def wrap_rtl_lines(draw, text, fnt, max_width):
    words = text.split(" ")
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        if draw.textlength(" ".join(trial), font=fnt) <= max_width or not cur:
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


def blurred_backdrop(im, w, h):
    bg = cover_fit(im, w, h).filter(ImageFilter.GaussianBlur(28))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.blend(bg, dark, 0.35)


def draw_caption(base, caption, subcaption, top_area_h):
    """Solid rounded caption card at the bottom, high-contrast, Heebo Black."""
    d = ImageDraw.Draw(base, "RGBA")
    font_cap = font("Black", 50)
    font_sub = font("Medium", 30)

    max_w = W - 140
    lines = wrap_rtl_lines(d, caption, font_cap, max_w)
    line_h = 60
    text_block_h = len(lines) * line_h + (44 if subcaption else 0)
    pad_v = 26
    card_h = text_block_h + pad_v * 2
    card_top = H - card_h - 26
    card_top = max(card_top, top_area_h + 10)

    d.rounded_rectangle([28, card_top, W - 28, card_top + card_h], radius=22, fill=(12, 22, 38, 210))

    y = card_top + pad_v
    for ln in lines:
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_cap)
        d.text(((W - tw) / 2, y), txt, font=font_cap, fill=(255, 255, 255, 255))
        y += line_h
    if subcaption:
        y += 6
        txt = rtl(subcaption)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, y), txt, font=font_sub, fill=(255, 205, 92, 255))


def make_scene(name, image_path, caption, subcaption=None, fit="contain"):
    im = Image.open(image_path).convert("RGB")

    if fit == "contain":
        base = blurred_backdrop(im, W, H).convert("RGB")
        avail_h = H - 210  # leave room for caption card
        iw, ih = im.size
        scale = min((W - 120) / iw, avail_h / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        sharp = im.resize((nw, nh), Image.LANCZOS)
        x, y = (W - nw) // 2, (avail_h - nh) // 2 + 14
        # white card frame behind the page for a clean "document" look
        frame_pad = 12
        base_rgba = base.convert("RGBA")
        fd = ImageDraw.Draw(base_rgba)
        fd.rounded_rectangle(
            [x - frame_pad, y - frame_pad, x + nw + frame_pad, y + nh + frame_pad],
            radius=14, fill=(255, 255, 255, 255)
        )
        base = base_rgba
        base.paste(sharp, (x, y))
        top_h = y + nh + frame_pad
    else:
        base = cover_fit(im, W, H).convert("RGBA")
        top_h = 0

    draw_caption(base, caption, subcaption, top_h if fit == "contain" else 0)
    base.convert("RGB").save(os.path.join(OUT, f"{name}.png"), quality=95)
    print("scene:", name, fit)


def vertical_gradient(w, h, top_rgb, bottom_rgb):
    top = Image.new("RGB", (w, h), top_rgb)
    bottom = Image.new("RGB", (w, h), bottom_rgb)
    mask = Image.new("L", (1, h), 0)
    for y in range(h):
        mask.putpixel((0, y), int(255 * (y / h)))
    mask = mask.resize((w, h))
    return Image.composite(bottom, top, mask)


def make_icon_scene(name, emoji, top_rgb, bottom_rgb, caption, subcaption=None, accent=(255, 205, 92)):
    base = vertical_gradient(W, H, top_rgb, bottom_rgb).convert("RGBA")
    d = ImageDraw.Draw(base, "RGBA")

    # big emoji icon in a soft circle
    circle_r = 92
    cx, cy = W // 2, 190
    d.ellipse([cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r], fill=(255, 255, 255, 60))
    font_emoji = ImageFont.truetype(EMOJI_FONT, 100)
    bbox = font_emoji.getbbox(emoji)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw / 2, cy - 85), emoji, font=font_emoji, embedded_color=True)

    font_cap = font("Black", 52)
    font_sub = font("Medium", 30)
    lines = wrap_rtl_lines(d, caption, font_cap, W - 160)
    y = 350
    for ln in lines:
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_cap)
        d.text(((W - tw) / 2, y), txt, font=font_cap, fill=(255, 255, 255, 255))
        y += 62
    if subcaption:
        y += 8
        txt = rtl(subcaption)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, y), txt, font=font_sub, fill=accent)

    base.convert("RGB").save(os.path.join(OUT, f"{name}.png"), quality=95)
    print("icon scene:", name)


def make_title_card(name, logo_path, title, subtitle):
    base = vertical_gradient(W, H, (137, 205, 240), (75, 150, 205))
    d = ImageDraw.Draw(base)

    lh = 0
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lw = 300
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.LANCZOS)
        base.paste(logo, ((W - lw) // 2, 84), logo)

    font_title = font("Black", 60)
    font_sub = font("Medium", 32)
    ty = 84 + lh + 46
    txt = rtl(title)
    tw = d.textlength(txt, font=font_title)
    d.text(((W - tw) / 2, ty), txt, font=font_title, fill=(15, 33, 58))
    ty += 76
    for ln in subtitle.split("\n"):
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, ty), txt, font=font_sub, fill=(24, 48, 82))
        ty += 44

    base.save(os.path.join(OUT, f"{name}.png"), quality=95)
    print("title card:", name)


def make_closing_card(name, logo_path, title, subtitle):
    base = vertical_gradient(W, H, (20, 40, 70), (35, 70, 110))
    d = ImageDraw.Draw(base)

    lh = 0
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lw = 250
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.LANCZOS)
        base.paste(logo, ((W - lw) // 2, 64), logo)

    font_title = font("Black", 56)
    font_sub = font("Medium", 32)
    ty = 64 + lh + 50
    for ln in title.split("\n"):
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_title)
        d.text(((W - tw) / 2, ty), txt, font=font_title, fill=BRAND_YELLOW)
        ty += 70
    ty += 14
    for ln in subtitle.split("\n"):
        txt = rtl(ln)
        tw = d.textlength(txt, font=font_sub)
        d.text(((W - tw) / 2, ty), txt, font=font_sub, fill=(230, 238, 245))
        ty += 42

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
        "עלון אנכי...",
        fit="contain",
    )
    make_scene(
        "02_horizontal",
        os.path.join(IMG, "covers", "horizontal-2-p1.webp"),
        "...או אופקי!",
        fit="contain",
    )
    make_scene(
        "03_styles",
        os.path.join(IMG, "design-styles", "style-2.webp"),
        "עשרות כיווני עיצוב",
        "השם, הצבעים, הדמויות - הכל אישי",
        fit="contain",
    )
    make_scene(
        "04_sections",
        os.path.join(IMG, "sections", "section-12.webp"),
        "דבר תורה, חידות, קומיקס...",
        "מדורים תורניים ברמה גבוהה, כל שבוע",
        fit="contain",
    )
    make_icon_scene(
        "05_writers", "📰",
        (255, 154, 108), (224, 79, 59),
        "התלמידים כותבים בעצמם!",
        "צוות עלון - כתבים צעירים, בכל בית ספר",
        accent=(255, 244, 214),
    )
    make_icon_scene(
        "06_family", "🏠",
        (76, 191, 143), (36, 132, 120),
        "וגם המשפחה משחקת בבית",
        "מברכים, שרים, קוראים בעלון - ומסמנים יחד",
        accent=(255, 244, 214),
    )
    make_scene(
        "07_sharing",
        os.path.join(IMG, "sharing", "sharing-01.webp"),
        "כל מה שקורה בבית הספר...",
        "מגיע ישר הביתה",
        fit="cover",
    )
    make_scene(
        "08_bw",
        os.path.join(IMG, "covers", "color-and-bw-p1.webp"),
        "צבעוני + שחור-לבן להדפסה",
        "כל שבוע, שני הקבצים אצלכם",
        fit="contain",
    )
    make_scene(
        "09_levels",
        os.path.join(IMG, "covers", "age-older-p1.webp"),
        "ואפשר גם לפי שכבות גיל!",
        fit="contain",
    )

    make_closing_card(
        "99_cta", logo,
        "בואו תנסו חודש חינם",
        "בחרו את הכיוון שאתם אוהבים\nונחזור אליכם להתחיל",
    )

    print("DONE")
