#!/usr/bin/env python3
"""
Pull a source image down to web size and put it in this repo.

    python optimize.py <url-or-path> <folder>/<name> [--width 1400] [--png]

Source art is routinely 5 to 6 MB straight out of a generator or GHL's media
library. That is fine as a master and fatal on a landing page, where most of
the traffic is a phone on cellular. This resizes, strips metadata, and writes
a JPEG (or PNG when transparency actually matters).

    python optimize.py https://assets.cdn.filesafe.space/.../x.png giftcards/gift-card-hero

Then run build_manifest.py, commit and push.
"""

import argparse
import io as _io
import os
import sys
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET_KB = 300


def load(src):
    if src.startswith("http://") or src.startswith("https://"):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        return Image.open(_io.BytesIO(raw)), len(raw)
    with open(src, "rb") as fh:
        raw = fh.read()
    return Image.open(_io.BytesIO(raw)), len(raw)


def has_alpha(im):
    if im.mode in ("RGBA", "LA"):
        return im.getchannel("A").getextrema()[0] < 255
    return im.mode == "P" and "transparency" in im.info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dest", help="folder/name without extension, e.g. giftcards/gift-card-hero")
    ap.add_argument("--width", type=int, default=1400)
    ap.add_argument("--png", action="store_true", help="force PNG, for transparency")
    a = ap.parse_args()

    im, orig_bytes = load(a.src)
    ow, oh = im.size
    keep_alpha = a.png or has_alpha(im)

    if ow > a.width:
        im = im.resize((a.width, round(oh * a.width / ow)), Image.LANCZOS)

    folder, name = a.dest.rsplit("/", 1)
    outdir = os.path.join(ROOT, folder)
    os.makedirs(outdir, exist_ok=True)

    if keep_alpha:
        out = os.path.join(outdir, name + ".png")
        im.convert("RGBA").save(out, "PNG", optimize=True)
    else:
        out = os.path.join(outdir, name + ".jpg")
        im = im.convert("RGB")
        for q in (85, 80, 75, 70, 65):
            im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
            if os.path.getsize(out) <= TARGET_KB * 1024:
                break

    new_bytes = os.path.getsize(out)
    print(f"  {os.path.basename(a.src)}")
    print(f"    {ow}x{oh}  {orig_bytes/1024/1024:.1f} MB")
    print(f"    -> {im.size[0]}x{im.size[1]}  {new_bytes/1024:.0f} KB  "
          f"({orig_bytes/max(new_bytes,1):.0f}x smaller)")
    print(f"    {os.path.relpath(out, ROOT).replace(os.sep, '/')}")
    if new_bytes > TARGET_KB * 1024:
        print(f"    NOTE: still over {TARGET_KB} KB. Try a smaller --width.")


if __name__ == "__main__":
    main()
