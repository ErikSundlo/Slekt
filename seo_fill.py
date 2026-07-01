#!/usr/bin/env python3
"""Idempotently add SEO tags (canonical, hreflang, meta description, Open Graph
and Twitter Card) to pages that are missing them. Safe to re-run: only inserts
tags that are absent."""
import os
import re
import html

BASE = "https://www.sundlospeilberg.no/"
OG_IMAGE = BASE + "og-image.svg"
ROOT = os.path.dirname(os.path.abspath(__file__))

TITLE_RE = re.compile(r"(?im)^([ \t]*)<title>(.*?)</title>\s*$")
FIRST_P_RE = re.compile(r"(?is)<p\b[^>]*>(.*?)</p>")
DESC_RE = re.compile(r'(?i)name="description"\s+content="(.*?)"')
TAG_RE = re.compile(r"(?s)<[^>]+>")
WS_RE = re.compile(r"\s+")

# Title suffixes to strip when falling back to the title for a description.
SUFFIXES = [" – Historical Archive", " – Historisches Archiv",
            " – Historisk arkiv – Sundlo- og Ringsetslekten", " – Historisk arkiv"]

LOCALE = {"nb": "nb_NO", "en": "en_US", "de": "de_DE"}
SITE_NAME = {
    "nb": "Historisk arkiv – Sundlo og Ringset",
    "en": "Historical Archive – Sundlo and Ringset",
    "de": "Historisches Archiv – Sundlo und Ringset",
}


def url_for(relpath):
    return BASE + relpath.replace(os.sep, "/")


def esc(s):
    """Normalise then escape for an HTML attribute (avoids double-escaping)."""
    return html.escape(html.unescape(s), quote=True)


def get_description(text, title):
    """Reuse an existing meta description if present, else derive one."""
    m = DESC_RE.search(text)
    if m:
        return html.unescape(m.group(1)).strip()
    m = FIRST_P_RE.search(text)
    desc = ""
    if m:
        desc = WS_RE.sub(" ", html.unescape(TAG_RE.sub("", m.group(1)))).strip()
    if len(desc) < 40:  # too short / no paragraph -> fall back to the title
        t = title
        for s in SUFFIXES:
            if t.endswith(s):
                t = t[: -len(s)]
        desc = t.strip()
    if len(desc) > 155:
        cut = desc[:155].rsplit(" ", 1)[0]
        desc = cut.rstrip(".,;:") + "…"
    return desc


def hreflang_block(indent, nb, en, de):
    return (
        f'{indent}<link rel="alternate" hreflang="nb" href="{url_for(nb)}">\n'
        f'{indent}<link rel="alternate" hreflang="en" href="{url_for(en)}">\n'
        f'{indent}<link rel="alternate" hreflang="de" href="{url_for(de)}">\n'
    )


def og_block(indent, *, title, desc, self_url, lang, kind):
    t, d = esc(title), esc(desc)
    return (
        f'{indent}<meta property="og:title" content="{t}">\n'
        f'{indent}<meta property="og:description" content="{d}">\n'
        f'{indent}<meta property="og:type" content="{kind}">\n'
        f'{indent}<meta property="og:locale" content="{LOCALE[lang]}">\n'
        f'{indent}<meta property="og:site_name" content="{esc(SITE_NAME[lang])}">\n'
        f'{indent}<meta property="og:url" content="{self_url}">\n'
        f'{indent}<meta property="og:image" content="{OG_IMAGE}">\n'
        f'{indent}<meta property="og:image:type" content="image/svg+xml">\n'
        f'{indent}<meta name="twitter:card" content="summary_large_image">\n'
        f'{indent}<meta name="twitter:title" content="{t}">\n'
        f'{indent}<meta name="twitter:description" content="{d}">\n'
        f'{indent}<meta name="twitter:image" content="{OG_IMAGE}">\n'
    )


def process(relpath, *, self_url, description=True, hreflang=None, noindex=False,
            og=True, lang="nb", kind="website"):
    path = os.path.join(ROOT, relpath)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    m = TITLE_RE.search(text)
    if not m:
        print(f"  SKIP (no <title>): {relpath}")
        return
    indent, title = m.group(1), m.group(2).strip()

    additions = ""
    if noindex and "noindex" not in text:
        additions += f'{indent}<meta name="robots" content="noindex,follow">\n'
    if 'rel="canonical"' not in text:
        additions += f'{indent}<link rel="canonical" href="{self_url}">\n'
    if hreflang and "hreflang" not in text:
        additions += hreflang_block(indent, *hreflang)
    if description and 'name="description"' not in text:
        additions += f'{indent}<meta name="description" content="{esc(get_description(text, title))}">\n'
    if og and "og:title" not in text:
        additions += og_block(indent, title=title, desc=get_description(text, title),
                              self_url=self_url, lang=lang, kind=kind)

    if not additions:
        print(f"  ok (nothing to add): {relpath}")
        return

    insert_at = m.end()
    if text[insert_at:insert_at + 1] == "\n":
        insert_at += 1
    text = text[:insert_at] + additions + text[insert_at:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  updated: {relpath}")


def main():
    # --- Top-level Norwegian-only utility pages ---
    for name in ["tidslinje.html", "slektstre.html", "navneregister.html"]:
        process(name, self_url=url_for(name), lang="nb", kind="website")

    # --- about.html (already has hreflang) ---
    process("about.html", self_url=url_for("about.html"), lang="nb", kind="website")

    # --- homepage: already fully tagged; run keeps it idempotent ---
    process("index.html", self_url=BASE, lang="nb", kind="website")

    # --- redirect stub: noindex + canonical to homepage, no description/OG ---
    process(os.path.join("HTML", "index.html"),
            self_url=BASE, description=False, og=False, noindex=True)

    # --- translated homepage / about pages ---
    process(os.path.join("en", "index.html"), self_url=url_for("en/index.html"),
            hreflang=("index.html", "en/index.html", "de/index.html"), lang="en")
    process(os.path.join("de", "index.html"), self_url=url_for("de/index.html"),
            hreflang=("index.html", "en/index.html", "de/index.html"), lang="de")
    process(os.path.join("en", "about.html"), self_url=url_for("en/about.html"),
            hreflang=("about.html", "en/about.html", "de/about.html"), lang="en")
    process(os.path.join("de", "about.html"), self_url=url_for("de/about.html"),
            hreflang=("about.html", "en/about.html", "de/about.html"), lang="de")

    # --- content pages: Norwegian originals + en/de translations (kind=article) ---
    for lang, sub in [("nb", ""), ("en", "en"), ("de", "de")]:
        d = os.path.join("HTML", sub) if sub else "HTML"
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if not name.endswith(".html") or name == "index.html":
                continue
            rel = os.path.join(d, name)
            nb = os.path.join("HTML", name)
            en = os.path.join("HTML", "en", name)
            de = os.path.join("HTML", "de", name)
            process(rel, self_url=url_for(rel), hreflang=(nb, en, de),
                    lang=lang, kind="article")


if __name__ == "__main__":
    main()
