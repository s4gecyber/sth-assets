#!/usr/bin/env python3
"""
Regenerate manifest.json and index.html for the Sweet Trees asset repo.

    python build_manifest.py

Walks the image folders, records what is there, and warns about anything that
will cause trouble later: files too big for a landing page, formats browsers
handle badly, and filenames that make ugly or broken URLs.

Pillow is optional. If it is installed you also get pixel dimensions, which is
how the script can tell you whether an og-image is actually 1200x630.
"""

import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://s4gecyber.github.io/sth-assets"

FOLDERS = ["brand", "og", "work", "work/before-after", "species", "giftcards"]
WEB_OK = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".avif"}
SIZE_WARN = 500 * 1024          # 500 KB
SIZE_HARD = 2 * 1024 * 1024     # 2 MB
GOOD_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n/1:.0f} {unit}"
        n /= 1024.0


def size_str(n):
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n/1024:.0f} KB"
    return f"{n/(1024*1024):.1f} MB"


def collect():
    items, warnings = [], []
    for folder in FOLDERS:
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            path = os.path.join(d, name)
            if not os.path.isfile(path) or name.startswith("."):
                continue
            ext = os.path.splitext(name)[1].lower()
            rel = f"{folder}/{name}"

            if ext not in WEB_OK:
                warnings.append(f"{rel}: '{ext}' is not a web image format, browsers may not show it")
                continue
            if not GOOD_NAME.match(name):
                warnings.append(f"{rel}: rename to lowercase with hyphens, no spaces")

            size = os.path.getsize(path)
            if size > SIZE_HARD:
                warnings.append(f"{rel}: {size_str(size)} is too big for a web page, resize it")
            elif size > SIZE_WARN:
                warnings.append(f"{rel}: {size_str(size)}, consider resizing under 500 KB")

            w = h = None
            if HAVE_PIL and ext != ".svg":
                try:
                    with Image.open(path) as im:
                        w, h = im.size
                except Exception:
                    pass

            if folder == "og" and w and (w, h) != (1200, 630):
                warnings.append(f"{rel}: og images should be 1200x630, this is {w}x{h}")

            items.append({
                "path": rel,
                "url": f"{BASE_URL}/{rel}",
                "folder": folder,
                "bytes": size,
                "size": size_str(size),
                "width": w,
                "height": h,
            })
    return items, warnings


GALLERY_CSS = """
:root{--forest:#1F3A28;--forest-deep:#142519;--moss:#5E8C61;--cream:#FAF7F0;
--cream-warm:#F4EDE0;--papaya:#D97706;--rule:#D7CFB8;--muted:#5C5C5C}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:#1A1A1A;
font:400 15px/1.6 'DM Sans',-apple-system,Segoe UI,sans-serif}
header{background:var(--forest-deep);color:var(--cream);padding:30px 28px;
border-bottom:5px solid var(--papaya)}
header h1{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;
font-size:30px;margin:0 0 6px}
header p{margin:0;color:#A4C29A;font-size:14px}
header code{background:rgba(255,255,255,.1);padding:2px 7px;border-radius:5px;font-size:13px}
main{max-width:1200px;margin:0 auto;padding:30px 24px 70px}
h2{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:23px;
color:var(--forest);margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--rule)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px}
.card{background:#fff;border:1px solid var(--rule);border-radius:12px;overflow:hidden;
display:flex;flex-direction:column}
.thumb{background:var(--cream-warm);height:160px;display:flex;align-items:center;
justify-content:center;overflow:hidden}
.thumb img{max-width:100%;max-height:100%;display:block}
.meta{padding:12px 14px}
.name{font-weight:700;font-size:13.5px;word-break:break-all;color:var(--forest)}
.dim{font-size:12px;color:var(--muted);margin-top:3px}
.copy{margin-top:10px;width:100%;background:var(--papaya);color:#fff;border:0;
border-radius:20px;padding:9px;font:700 12px 'DM Sans',sans-serif;cursor:pointer}
.copy:hover{background:#B45309}
.copy.done{background:var(--moss)}
.empty{color:var(--muted);font-style:italic;padding:8px 0}
.warn{background:#FCE9D2;border:1px solid var(--papaya);border-radius:10px;
padding:16px 18px;margin-bottom:26px}
.warn h3{margin:0 0 8px;font-size:14px;color:#B45309}
.warn ul{margin:0;padding-left:20px;font-size:13.5px;color:#7a5520}
"""


def write_gallery(items, warnings):
    by_folder = {}
    for it in items:
        by_folder.setdefault(it["folder"], []).append(it)

    warn_html = ""
    if warnings:
        lis = "".join(f"<li>{w}</li>" for w in warnings)
        warn_html = f'<div class="warn"><h3>{len(warnings)} thing(s) to look at</h3><ul>{lis}</ul></div>'

    body = []
    for folder in FOLDERS:
        entries = by_folder.get(folder, [])
        body.append(f"<h2>{folder} <span style='font-weight:400;font-size:14px;color:#5C5C5C'>"
                    f"({len(entries)})</span></h2>")
        if not entries:
            body.append('<p class="empty">Nothing here yet.</p>')
            continue
        cards = []
        for it in entries:
            dim = f"{it['width']}&times;{it['height']} &middot; " if it["width"] else ""
            cards.append(f"""<div class="card">
  <div class="thumb"><img src="{it['path']}" alt="{it['path']}" loading="lazy"></div>
  <div class="meta">
    <div class="name">{os.path.basename(it['path'])}</div>
    <div class="dim">{dim}{it['size']}</div>
    <button class="copy" data-url="{it['url']}">Copy URL</button>
  </div>
</div>""")
        body.append('<div class="grid">' + "".join(cards) + "</div>")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Sweet Trees asset library</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Cormorant+Garamond:wght@600&display=swap" rel="stylesheet">
<style>{GALLERY_CSS}</style></head>
<body>
<header>
  <h1>Sweet Trees asset library</h1>
  <p>{len(items)} file(s). Base URL <code>{BASE_URL}/</code> &middot; rebuilt {date.today().isoformat()}</p>
</header>
<main>
{warn_html}
{''.join(body)}
</main>
<script>
document.querySelectorAll('.copy').forEach(function (b) {{
  b.addEventListener('click', function () {{
    navigator.clipboard.writeText(b.dataset.url).then(function () {{
      var t = b.textContent; b.textContent = 'Copied'; b.classList.add('done');
      setTimeout(function () {{ b.textContent = t; b.classList.remove('done'); }}, 1400);
    }});
  }});
}});
</script>
</body></html>"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    items, warnings = collect()

    manifest = {
        "base_url": BASE_URL,
        "generated": date.today().isoformat(),
        "count": len(items),
        "images": items,
    }
    with open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    write_gallery(items, warnings)

    print(f"  {len(items)} image(s) indexed")
    for folder in FOLDERS:
        n = sum(1 for i in items if i["folder"] == folder)
        print(f"    {folder:22} {n}")
    if not HAVE_PIL:
        print("\n  (pip install pillow for dimensions and og-image size checks)")
    if warnings:
        print(f"\n  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"    - {w}")
    print("\n  wrote manifest.json and index.html")


if __name__ == "__main__":
    main()
