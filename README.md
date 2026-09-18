# sth-assets

Image hosting for Sweet Trees Hawaii websites. Every photo, logo, and social card that a page or an
embed needs to link to lives here.

**Live at:** `https://s4gecyber.github.io/sth-assets/`

## Why this exists

Carrd sites are built from HTML embeds, and an embed needs a real URL for every image. Carrd's own
uploads are fine for native Carrd image elements, but their asset URLs can change when a site
republishes, and a broken image inside an embed fails silently. GitHub Pages URLs do not move.

That matters more than it sounds for the gift card promo, where the page URL and its images end up
inside card PDFs that never expire.

## The URL pattern

```
https://s4gecyber.github.io/sth-assets/<folder>/<filename>
```

So `brand/sth-logo.png` is served at:

```
https://s4gecyber.github.io/sth-assets/brand/sth-logo.png
```

Drop that straight into any embed:

```html
<img src="https://s4gecyber.github.io/sth-assets/brand/sth-logo.png" alt="Sweet Trees Hawaii">
```

## Folders

| Folder | What goes in it |
|---|---|
| `brand/` | Logos, wordmarks, banners, anything that is the identity itself |
| `og/` | Social preview cards, 1200×630, one per site. Name them for the site: `og-deals.jpg` |
| `work/` | Real job photos. Pruning, care visits, finished trees |
| `work/before-after/` | Paired shots. The most persuasive thing on any page |
| `species/` | Tree and fruit photos organised by species, for the care guides |
| `giftcards/` | Card artwork and gift card promo images |

Organised by what an image *is*, not by which site uses it, because the same photo ends up on several
sites.

## Adding an image

1. Drop the file into the right folder.
2. Run `python build_manifest.py`
3. Commit and push.

The script regenerates `manifest.json` and `index.html`, and warns about anything likely to cause
trouble: files over 500 KB, formats browsers handle badly, and names with spaces or capitals that
make URLs awkward.

## Naming

Lowercase, hyphens, no spaces. A space becomes `%20` in the URL and gets mangled by half the tools
that touch it.

```
good:  mango-pruning-before-mililani.jpg
bad:   Mango Pruning BEFORE (Mililani).JPG
```

## Browsing what is here

`index.html` is a generated gallery of everything in the repo with its URL next to it. Open it
locally, or once Pages is live, at the URL above.

## Size

Keep photos under about 500 KB. GitHub Pages will serve anything, but a 4 MB phone photo on a
landing page costs conversions on mobile, which is where most of the traffic is.

Resize to the largest size a page actually displays. A full-width hero rarely needs more than
2000 px wide. A proof photo in a card rarely needs more than 1200 px.

## A note on what goes public

This repository is public, because GitHub Pages needs it to be in order to serve the files. Anything
committed here is world-readable and can be indexed by search engines.

That is fine for brand assets and marketing photos. Do not put customer documents, anything with an
address or a phone number visible in the frame, or a photo a customer has not agreed to have used in
marketing.
