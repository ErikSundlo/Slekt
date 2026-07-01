#!/usr/bin/env python3
"""Idempotently add canonical, hreflang and meta-description tags to pages
that are missing them. Safe to re-run: only inserts tags that are absent."""
import os
import re
import html

BASE = "https://www.sundlospeilberg.no/"
ROOT = os.path.dirname(os.path.abspath(__file__))

TITLE_RE = re.compile(r"(?im)^([ \t]*)<title>(.*?)</title>\s*$")
FIRST_P_RE = re.compile(r"(?is)<p\b[^>]*>(.*?)</p>")
TAG_RE = re.compile(r"(?s)<[^>]+>")
WS_RE = re.compile(r"\s+")

# Title suffixes to strip when falling back to the title for a description.
SUFFIXES = [" – Historical Archive", " – Historisches Archiv", " – Historisk arkiv",
            " – Historisk arkiv – Sundlo- og Ringsetslekten"]


def url_for(relpath):
    return BASE + relpath.replace(os.sep, "/")


def extract_description(text, title):
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


def process(relpath, *, self_url, description=True, hreflang=None, noindex=False):
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
        desc = html.escape(extract_description(text, title), quote=True)
        additions += f'{indent}<meta name="description" content="{desc}">\n'

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
    # --- Top-level Norwegian-only utility pages: canonical + description ---
    for name in ["tidslinje.html", "slektstre.html", "navneregister.html"]:
        process(name, self_url=url_for(name))

    # --- about.html (already has hreflang): canonical + description ---
    process("about.html", self_url=url_for("about.html"))

    # --- redirect stub: noindex + canonical to homepage, no description ---
    process(os.path.join("HTML", "index.html"),
            self_url=BASE, description=False, noindex=True)

    # --- translated homepage / about pages ---
    process(os.path.join("en", "index.html"), self_url=url_for("en/index.html"),
            hreflang=("index.html", "en/index.html", "de/index.html"))
    process(os.path.join("de", "index.html"), self_url=url_for("de/index.html"),
            hreflang=("index.html", "en/index.html", "de/index.html"))
    process(os.path.join("en", "about.html"), self_url=url_for("en/about.html"),
            hreflang=("about.html", "en/about.html", "de/about.html"))
    process(os.path.join("de", "about.html"), self_url=url_for("de/about.html"),
            hreflang=("about.html", "en/about.html", "de/about.html"))

    # --- translated content pages under HTML/en and HTML/de ---
    for lang in ["en", "de"]:
        d = os.path.join("HTML", lang)
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if not name.endswith(".html"):
                continue
            rel = os.path.join(d, name)
            nb = os.path.join("HTML", name)
            en = os.path.join("HTML", "en", name)
            de = os.path.join("HTML", "de", name)
            process(rel, self_url=url_for(rel), hreflang=(nb, en, de))


if __name__ == "__main__":
    main()
