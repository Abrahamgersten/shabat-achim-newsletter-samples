#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Asset pipeline: pull source examples from the parent folder, render PDFs,
optimize images, and drop clean-named web-ready assets into site/assets/."""
import os
import fitz
from PIL import Image

SRC = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים"
SITE = os.path.join(SRC, "site")
IMG = os.path.join(SITE, "assets", "images")
PDF_OUT = os.path.join(SITE, "assets", "pdfs")

def render_pdf(src_name, slug, pages=None, zoom=2.2, cover_zoom=1.6):
    """Copy the pdf with a clean name + render page covers as webp."""
    path = os.path.join(SRC, src_name)
    doc = fitz.open(path)
    doc.save(os.path.join(PDF_OUT, f"{slug}.pdf"))
    n = len(doc)
    idxs = pages if pages else range(n)
    covers = []
    for i in idxs:
        if i >= n:
            continue
        page = doc[i]
        rect = page.rect
        orientation = "landscape" if rect.width > rect.height else "portrait"
        pix = page.get_pixmap(matrix=fitz.Matrix(cover_zoom, cover_zoom))
        out_path = os.path.join(IMG, "covers", f"{slug}-p{i+1}.webp")
        Image.frombytes("RGB", (pix.width, pix.height), pix.samples).save(out_path, "WEBP", quality=82, method=6)
        covers.append((f"{slug}-p{i+1}.webp", orientation, pix.width, pix.height))
    doc.close()
    return covers

def optimize_image(src_name, dest_rel, max_w=1400, quality=82, subdir="misc"):
    path = os.path.join(SRC, src_name)
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        h = int(im.height * (max_w / im.width))
        im = im.resize((max_w, h), Image.LANCZOS)
    out_path = os.path.join(IMG, subdir, dest_rel)
    im.save(out_path, "WEBP", quality=quality, method=6)
    return im.size

if __name__ == "__main__":
    results = {}

    pdfs = [
        ("דוגמא אנכית 1.pdf", "vertical-1", None),
        ("דוגמא אנכית 2.pdf", "vertical-2", None),
        ("דוגמא אנכית 3.pdf", "vertical-3", None),
        ("דוגמא אנכית 4.pdf", "vertical-4", None),
        ("דוגמא אופקית 1.pdf", "horizontal-1", None),
        ("דוגמא אופקית 2.pdf", "horizontal-2", None),
        ("דוגמא אופקית 3.pdf", "horizontal-3", None),
        ("דוגמא אופקית 7.pdf", "horizontal-4", None),
        ("דוגמא אופקית 4 עם תכנים משותפים.pdf", "shared-content-1", None),
        ("דוגמא אופקית 5 עם תכנים משותפים.pdf", "shared-content-2", None),
        ("דוגמא אופקית 6 מדורג לפי רמות.pdf", "graduated-levels", None),
        ("דוגמא לשכבות הגיל הבוגרות.pdf", "age-older", None),
        ("דוגמא לשכבות הגיל הצעירות.pdf", "age-younger", None),
        ("דוגמא לעלון מותאם להדפסה שחור לבן.pdf", "color-and-bw", None),
        ("עלון נוה אברהם עריכה מלאה - ויחי.pdf", "full-example", None),
    ]
    for src, slug, pages in pdfs:
        try:
            covers = render_pdf(src, slug, pages)
            results[slug] = covers
            print(slug, "->", covers)
        except Exception as e:
            print("ERROR", src, e)

    # מדורים (section examples)
    sections = [
        "מדור דבר תורה.png", "מדור מה בפרשה.png", "מדור חידות בתמונות.png",
        "מדור חידות לפרשה.png", "מדור מסביב לשולחן - סיפור פיקנתי עם שאלות מסביב לשולחן השבת.png",
        "מדור זה קרה באמת.png", "מדור זה קרה באמת!.png", "מדור סיפור בהמשכים.png",
        "מדור סיפור בהמשכים 2.png", "מדור בריא לדעת.png", "מדור בריא לדעת 2.png",
        "מדור קומיקס.png", "מדור קומיקס 2.png", "מדור מצא את ההבדלים.png",
        "מלתא דבדיחותא.png", "מדור נפלאות הבריאה.png", "מדור תפזורת.png",
        "מדור יש לי מושג.png", "מדור יש לי מושג 2.png", "מדור ככה זה בחיים.png",
        "מדור אור בהשכלה.png", "מדור מה לעשות.png",
    ]
    for i, s in enumerate(sections, 1):
        try:
            size = optimize_image(os.path.join("מדורים", s), f"section-{i:02d}.webp", max_w=900, subdir="sections")
            print("section", i, s, "->", size)
        except Exception as e:
            print("ERROR", s, e)

    # שיתוף תכנים (personal content sharing)
    sharing = [
        "שיתוף תכנים 1.png", "שיתוף תכנים 2.png", "שיתוף תכנים 3.png",
        "שיתוף תכנים 4.jpeg", "שיתוף תכנים 5.jpeg", "שיתוף תכנים 7.jpeg",
        "שיתוף תכנים 8.png", "שיתוף תכנים 9.png",
    ]
    for i, s in enumerate(sharing, 1):
        try:
            size = optimize_image(s, f"sharing-{i:02d}.webp", max_w=1100, subdir="sharing")
            print("sharing", i, s, "->", size)
        except Exception as e:
            print("ERROR", s, e)

    # design style blank templates
    styles = ["אופציות עיצוביות חדשות 1.jpeg", "אופציות עיצוביות חדשות 2.jpeg", "אופציות עיצוביות חדשות 3.jpeg"]
    for i, s in enumerate(styles, 1):
        try:
            size = optimize_image(s, f"style-{i}.webp", max_w=1000, subdir="design-styles")
            print("style", i, s, "->", size)
        except Exception as e:
            print("ERROR", s, e)

    # logo + misc
    try:
        im = Image.open(os.path.join(SRC, "לוגו שבת אחים.png")).convert("RGBA")
        im.save(os.path.join(IMG, "misc", "logo.png"))
        print("logo saved", im.size)
    except Exception as e:
        print("ERROR logo", e)

    print("DONE")
