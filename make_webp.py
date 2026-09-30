# -*- coding: utf-8 -*-
"""Re-encode the gift card page images at their real display size, as WebP.

Quality 70 for photos: compared against 80 at the true 313px render size the
two are indistinguishable, and foliage is expensive to encode. The card shot
stays at 82 because it carries text.

The JPEGs were cut at 900 to 1400px wide and then displayed at 313 to 494 CSS
px. Even allowing 2x for retina that is two to three times more pixels than any
screen uses, and the before/after pair was seven times oversized. WebP at the
right dimensions cuts the page's image payload by roughly four.

JPEGs are left in place as a fallback and for anything already pointing at them.
"""
import io, os
from PIL import Image

SRC = r"C:\Users\Sage\AppData\Local\Temp\claude\F--Business-Artifacts-2026\532341d6-442f-4583-a1f5-72c478b476a7\images"
ROOT = os.path.dirname(os.path.abspath(__file__))

def crop(im, ratio, anchor):
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio); x0 = (w - nw) // 2
        return im.crop((x0, 0, x0 + nw, h))
    nh = round(w / ratio); y0 = max(0, min(round((h - nh) * anchor), h - nh))
    return im.crop((0, y0, w, y0 + nh))

# source, dest, display px at 1280 viewport, target width (~2x display), ratio, anchor
JOBS = [
    ("9.jpg",  "team/sage-at-work",                    340, 700, 0.80, 0.42),
    ("6.jpg",  "work/leaf-inspection",                 321, 700, 1.00, 0.45),
    ("13.jpg", "work/mango-thinning/thinning-cut",     321, 700, 1.00, 0.40),
    ("15.jpg", "work/mango-thinning/light-through-sq", 321, 700, 1.00, 0.34),
    ("10.jpg", "work/mango-thinning/canopy-before",    313, 700, 0.75, 0.50),
    ("18.jpg", "work/mango-thinning/canopy-after",     313, 700, 0.75, 0.50),
]

before = after = 0
for src, dest, disp, width, ratio, anchor in JOBS:
    im = crop(Image.open(os.path.join(SRC, src)).convert("RGB"), ratio, anchor)
    im = im.resize((width, round(im.size[1] * width / im.size[0])), Image.LANCZOS)
    out = os.path.join(ROOT, dest.replace("/", os.sep) + ".webp")
    im.save(out, "WEBP", quality=70, method=6)
    old = os.path.join(ROOT, dest.replace("/", os.sep) + ".jpg")
    ob, nb = os.path.getsize(old), os.path.getsize(out)
    before += ob; after += nb
    print(f"  {dest.split('/')[-1]:<22} {ob//1024:>4} KB -> {nb//1024:>3} KB   {im.size[0]}x{im.size[1]} for {disp}px display")

# The card shot has no separate original; re-encode the repo copy.
h = Image.open(os.path.join(ROOT, "giftcards", "gift-card-hero.jpg")).convert("RGB")
h = h.resize((1000, round(h.size[1] * 1000 / h.size[0])), Image.LANCZOS)
out = os.path.join(ROOT, "giftcards", "gift-card-hero.webp")
h.save(out, "WEBP", quality=82, method=6)
ob = os.path.getsize(os.path.join(ROOT, "giftcards", "gift-card-hero.jpg"))
nb = os.path.getsize(out)
before += ob; after += nb
print(f"  {'gift-card-hero':<22} {ob//1024:>4} KB -> {nb//1024:>3} KB   {h.size[0]}x{h.size[1]} for 494px display")

print(f"\n  page payload {before//1024} KB -> {after//1024} KB  ({before/after:.1f}x smaller)")
