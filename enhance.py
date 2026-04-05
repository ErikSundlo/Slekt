#!/usr/bin/env python3
"""
Enhances the already-reformatted HTML files:
  - Gives proper names to unnamed hist* documents
  - Promotes standalone <b> paragraphs to <h2> section headings
  - Removes <sdfield> LibreOffice artifacts
  - Adds anchor IDs to all headings
  - Generates a Table of Contents for documents with 3+ headings
  - Regenerates the root index.html with updated names
"""

import os
import re
from bs4 import BeautifulSoup, NavigableString

HTML_DIR = r"C:\Users\eriks\OneDrive\Konverter\HTML"
ROOT_DIR = r"C:\Users\eriks\OneDrive\Konverter"

# ----------------------------------------------------------------
# Proper names for all documents
# ----------------------------------------------------------------
ALL_DOCS = {
    # Formål
    "Formål.html": "Formål – innledning av Harald Sundlo",

    # Konrad Sundlo forteller
    "Russland & Byen med det gylne skinn 1.html": "Russland & Byen med det gylne skinn – del 1",
    "Byen med det gylne skinn 2.html":             "Russland & Byen med det gylne skinn – del 2",
    "Byen med det gylne skinn 3 og Nansen.html":   "Russland & Byen med det gylne skinn – del 3 og Nansen",
    "Byen med kanonen.html":                        "Narvik 1940 – Byen med kanonen",

    # Politikompaniet
    "1.Politi.html":  "1. Politikompani – Fenrik Bødtker forteller",
    "2 Politi.html":  "1. Politikompani – Fortellinger del 2",
    "3politi.html":   "1. Politikompani – Fortellinger del 3",

    # Regiment Nordland
    "5konordl.html":  "Med 5. kompani Regiment Nordland – Dagfinn Henriksen",
    "7konordl.html":  "Med 7. kompani Regiment Nordland – Erling Larsen",

    # Legioner og bataljoner
    "Legiogri.html":  "Den Norske Legion – organisasjon og grunnlag",
    "Legpans.html":   "Den Norske Legion – pansertropper",
    "Reggerm.html":   "Med Germania – Arnt Torp forteller",
    "Skibat.html":    "Skibataljonen",

    # Sundloslekten – person names
    "hist3.html":                              "Jørgen Pederssøn Schjelderup",
    "hist5.html":                              "Hans Nielsen Speilberg",
    "hist 9 Conrad Lassen.html":               "Conrad Lassen",
    "hist10 Konrad Bertram Holm Sundlo.html":  "Konrad Bertram Holm Sundlo",
    "hist 13 Johan Marius Sundlo.html":        "Johan Marius Sundlo",
    "hist15.html":                             "Halfdan Sundlo",
    "hist16.html":                             "John Kjelbergsen Sundlo",
    "hist17.html":                             "Grim Saxvik",
    "hist22.html":                             "Mortine Kjelbergsdatter Sundlo",
    "hist23 Kjelberg Johnsen Sundlo.html":     "Kjelberg Johnsen Sundlo",
    "hist37 Albertine Sundlo.html":            "Albertine Sundlo",
    "hist38 Othelie Sundlo.html":              "Othelie Sundlo",
    "hist119.html":                            "Anders Larsen Holm",
    "hist139  Peder Paulsen (Leth).html":      "Peder Paulsen (Leth)",
    "hist140.html":                            "Paul Jensen Tved",
    "hist142 Paul Pedersen Dons.html":         "Paul Pedersen Dons",
    "hist151 Lorentz Dons.html":               "Lorentz Dons",
    "hist154 Mathias Conrad Peterson.html":    "Mathias Conrad Peterson",
    "hist156 Johan Peter Muller.html":         "Johan Peter Muller",
    "Hist158 Karl Dons.html":                  "Karl Dons",
    "hist160.html":                            "Georg Burchard Baade",
    "hist163.html":                            "Gjørtleren på Jøråshaugen – Christian Andersen Holm",
    "hist205.html":                            "Frøystein Ringset",
    "hist208.html":                            "Michel Baade – Hanseatisk kjøpmann i Bergen",
    "hist209.html":                            "Hans Baade – Hanseatisk kjøpmann i Bergen",
    "hist210.html":                            "Daniel Baade – Grønlandsmisjonen",
    "hist212.html":                            "Peter Baade – Bergen",
    "hist213.html":                            "Steffen Baade – Bergen",
    "hist235.html":                            "Korrespondanse med Johannes Gundersen, Levanger",
    "hist254.html":                            "Peter Daniel Baade – Prest og jurist",
    "hist255.html":                            "Michael Baade – Misjonær i Porsanger",
    "hist274.html":                            "Harald Hårfagre",
    "hist282.html":                            "Halvdan Svarte",
    "hist310.html":                            "Fredrik Anton Olai Baade",
    "hist430.html":                            "Nils Edvard Olsen Ringset",
    "hist431 Marie Saxvik.html":               "Marie Saxvik",

    # Ringsetslekten
    "Marta Ringset-Minneoppgave.html": "Marta Ringset – Minneoppgave",
}

# ----------------------------------------------------------------
# Categories for the index page
# ----------------------------------------------------------------
CATEGORIES = [
    {
        "title": "Formål og bakgrunn",
        "description": "Innledning og bakgrunnen for dette arkivet",
        "icon": "📜",
        "docs": ["Formål.html"],
    },
    {
        "title": "Konrad Sundlo forteller",
        "description": "Erindringer fra Kaukasus og Russland, nedskrevet av Harald Sundlo",
        "icon": "📖",
        "docs": [
            "Russland & Byen med det gylne skinn 1.html",
            "Byen med det gylne skinn 2.html",
            "Byen med det gylne skinn 3 og Nansen.html",
            "Byen med kanonen.html",
        ],
    },
    {
        "title": "Politikompaniet",
        "description": "Historier fra 1. Politikompani – Den Norske Legion",
        "icon": "⚔️",
        "docs": ["1.Politi.html", "2 Politi.html", "3politi.html"],
    },
    {
        "title": "Regiment Nordland",
        "description": "Beretninger fra Regiment Nordland",
        "icon": "🎖️",
        "docs": ["5konordl.html", "7konordl.html"],
    },
    {
        "title": "Legioner og bataljoner",
        "description": "Historier fra Den Norske Legion og tilknyttede enheter",
        "icon": "🗂️",
        "docs": ["Legiogri.html", "Legpans.html", "Reggerm.html", "Skibat.html"],
    },
    {
        "title": "Sundloslekten",
        "description": "Slektshistorie – familien Sundlo og tilknyttede familier",
        "icon": "🌳",
        "docs": [
            "hist3.html", "hist5.html",
            "hist 9 Conrad Lassen.html",
            "hist10 Konrad Bertram Holm Sundlo.html",
            "hist 13 Johan Marius Sundlo.html",
            "hist15.html", "hist16.html", "hist17.html", "hist22.html",
            "hist23 Kjelberg Johnsen Sundlo.html",
            "hist37 Albertine Sundlo.html", "hist38 Othelie Sundlo.html",
            "hist119.html",
            "hist139  Peder Paulsen (Leth).html",
            "hist140.html",
            "hist142 Paul Pedersen Dons.html",
            "hist151 Lorentz Dons.html",
            "hist154 Mathias Conrad Peterson.html",
            "hist156 Johan Peter Muller.html",
            "Hist158 Karl Dons.html",
            "hist163.html",
            "hist235.html",
            "hist274.html", "hist282.html",
            "hist431 Marie Saxvik.html",
        ],
    },
    {
        "title": "Baade / Ringset-slekten",
        "description": "Slektshistorie – familiene Baade og Ringset",
        "icon": "🌿",
        "docs": [
            "hist160.html",
            "hist208.html", "hist209.html", "hist210.html",
            "hist212.html", "hist213.html",
            "hist254.html", "hist255.html",
            "hist310.html",
            "Marta Ringset-Minneoppgave.html",
            "hist205.html",
            "hist430.html",
        ],
    },
]

# ----------------------------------------------------------------
# ToC CSS to inject inside content pages
# ----------------------------------------------------------------
TOC_CSS = """
    .toc {
        background: var(--gold-light, #f5edda);
        border: 1px solid var(--border, #ddd5c8);
        border-left: 4px solid var(--gold, #9a6e1a);
        border-radius: 6px;
        padding: 18px 22px;
        margin-bottom: 2.5em;
        font-size: 0.92rem;
    }
    .toc-title {
        font-family: 'Lora', Georgia, serif;
        font-weight: 600;
        color: var(--navy, #1c3557);
        margin-bottom: 10px;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .toc ul {
        margin: 0;
        padding-left: 1.2em;
        list-style: none;
    }
    .toc ul li {
        margin-bottom: 4px;
        line-height: 1.5;
    }
    .toc ul li::before {
        content: '– ';
        color: var(--gold, #9a6e1a);
        font-weight: 600;
    }
    .toc a {
        color: var(--navy, #1c3557);
        text-decoration: none;
    }
    .toc a:hover {
        color: var(--gold, #9a6e1a);
        text-decoration: underline;
    }
    .content-wrapper h2 {
        scroll-margin-top: 60px;
    }
    .content-wrapper h3 {
        scroll-margin-top: 60px;
    }
    /* Style <ol> tables of contents within document body */
    .doc-toc {
        background: var(--gold-light, #f5edda);
        border: 1px solid var(--border, #ddd5c8);
        border-left: 4px solid var(--gold, #9a6e1a);
        border-radius: 6px;
        padding: 16px 20px;
        margin: 1.5em 0;
        font-size: 0.92rem;
    }
    .doc-toc li {
        margin-bottom: 3px;
    }
"""


def slugify(text):
    """Create a URL-safe anchor slug from text."""
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text[:60] or "section"


def is_standalone_bold_heading(tag):
    """Return the heading text if <p> is a candidate for heading promotion.

    Handles cases like <p>«<b>1. Title</b></p> where a stray quote precedes the bold.
    """
    if tag.name != 'p':
        return False
    children = [c for c in tag.children
                if not (isinstance(c, NavigableString) and not c.strip())]
    # Case 1: only a <b> child
    if len(children) == 1 and children[0].name == 'b':
        text = children[0].get_text(strip=True)
        if 3 < len(text) < 150:
            return text
    # Case 2: a leading punctuation/quote NavigableString + <b>
    if len(children) == 2:
        first, second = children
        stripped = first.strip() if isinstance(first, NavigableString) else ''
        # Allow short leading punctuation (quotes, dashes, etc.) of 1-3 chars
        is_punc = len(stripped) <= 3 and not any(c.isalnum() for c in stripped)
        if (isinstance(first, NavigableString)
                and is_punc
                and hasattr(second, 'name') and second.name == 'b'):
            text = second.get_text(strip=True)
            if 3 < len(text) < 150:
                return text
    return False


def clean_tabs(text):
    """Replace tabs with a space."""
    return re.sub(r'\t+', ' ', text).strip()


def enhance_content(html_content):
    """
    Process the content-wrapper HTML:
    1. Remove any previously-generated ToC divs (idempotent)
    2. Remove sdfield tags
    3. Promote standalone bold <p> to <h2>
    4. Promote single-item <ol> to <h2> section headings
    5. Style multi-item <ol> that follow an "Innhold" heading as doc-toc
    6. Add anchor IDs to headings
    7. Generate ToC if 3+ headings
    Returns enhanced HTML string.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Remove any previously-generated .toc divs so we don't duplicate
    for toc_div in soup.find_all('div', class_='toc'):
        toc_div.decompose()

    # 2. Remove <sdfield> tags entirely
    for sf in soup.find_all('sdfield'):
        sf.decompose()

    # Also remove any <p> that only contain whitespace/br after sdfield removal
    for p in soup.find_all('p'):
        if not p.get_text(strip=True) and not p.find(['img', 'table']):
            p.decompose()

    # 3. Promote standalone bold <p> to <h2>
    for p in list(soup.find_all('p')):
        bold_text = is_standalone_bold_heading(p)
        if bold_text:
            h2 = soup.new_tag('h2')
            h2.string = clean_tabs(bold_text)
            p.replace_with(h2)

    # 4. Promote single-item <ol> to <h2> section headings.
    #    These are used in LibreOffice docs as inline section titles.
    for ol in list(soup.find_all('ol')):
        lis = ol.find_all('li', recursive=False)
        if len(lis) == 1:
            text = clean_tabs(lis[0].get_text(strip=True))
            if 2 < len(text) < 120:
                h2 = soup.new_tag('h2')
                h2.string = text
                ol.replace_with(h2)

    # 5. Style multi-item <ol> that appear after an "Innhold" paragraph as doc-toc.
    #    This handles the structured ToC at the top of Narvik/similar docs.
    found_innhold = False
    doc_toc_done = False
    for tag in list(soup.children):
        if not hasattr(tag, 'name') or not tag.name:
            continue
        if tag.name == 'p' and tag.get_text(strip=True).lower() in ('innhold', 'innholdsfortegnelse'):
            found_innhold = True
            continue
        if found_innhold and not doc_toc_done and tag.name == 'ol':
            tag['class'] = tag.get('class', []) + ['doc-toc']
        elif found_innhold and tag.name not in ('ol', 'p'):
            doc_toc_done = True  # Stop after first non-ol/p after Innhold

    # 3. Clean heading text (remove embedded tabs/newlines) and add anchor IDs
    slug_counts = {}
    for h in soup.find_all(['h1', 'h2', 'h3']):
        # Flatten any whitespace inside the heading tag
        raw_text = h.get_text()
        clean_text = re.sub(r'[\t\n\r]+', ' ', raw_text)
        clean_text = re.sub(r' {2,}', ' ', clean_text).strip()
        # If the heading's direct string content is messy, rebuild it
        if h.string and (('\t' in h.string) or ('\n' in h.string)):
            h.string = clean_text
        elif not h.string:
            # Complex inner structure - keep as-is but log
            pass

        text = clean_text
        base_slug = slugify(text)
        if not base_slug:
            continue
        if base_slug in slug_counts:
            slug_counts[base_slug] += 1
            slug = f"{base_slug}-{slug_counts[base_slug]}"
        else:
            slug_counts[base_slug] = 0
            slug = base_slug
        h['id'] = slug

    # 4. Generate ToC
    # Collect headings for ToC (skip if heading text matches page title – h1 duplicates)
    toc_items = []
    headings = soup.find_all(['h1', 'h2', 'h3'])

    # We'll use h2 and h3 only for ToC (h1 is usually the doc title, duplicated in page-header)
    for h in headings:
        if h.name in ('h2', 'h3'):
            raw = h.get_text()
            text = re.sub(r'[\t\n\r]+', ' ', raw)
            text = re.sub(r' {2,}', ' ', text).strip()
            anchor = h.get('id', '')
            if text and anchor:
                toc_items.append((h.name, text, anchor))

    # Add ToC only if 3+ items
    toc_html = ""
    if len(toc_items) >= 3:
        items_html = ""
        for level, text, anchor in toc_items:
            indent = "  " if level == 'h3' else ""
            items_html += f'{indent}<li><a href="#{anchor}">{text}</a></li>\n'
        toc_html = (
            f'<div class="toc">'
            f'<div class="toc-title">Innhold</div>'
            f'<ul>{items_html}</ul>'
            f'</div>'
        )

    result = str(soup)
    if toc_html:
        # Insert ToC at the very start of the content
        result = toc_html + "\n" + result

    return result


def inject_toc_css(html_file_content):
    """Inject TOC CSS into an existing HTML file's <style> block (idempotent)."""
    if '.toc {' in html_file_content:
        return html_file_content  # Already injected
    return html_file_content.replace(
        '\n    </style>',
        TOC_CSS + '\n    </style>',
        1  # Only replace first occurrence (in <head>)
    )


def update_page_title(html_content, new_title):
    """Update the <title> and page-header <h1> with the proper name."""
    # Update <title>
    html_content = re.sub(
        r'<title>[^<]+</title>',
        f'<title>{new_title} – Historisk arkiv</title>',
        html_content
    )
    # Update page-header h1
    html_content = re.sub(
        r'(<header class="page-header">\s*<h1>)[^<]*(</h1>)',
        rf'\g<1>{new_title}\g<2>',
        html_content
    )
    return html_content


def process_file(file_path):
    """Enhance a single HTML file."""
    fname = os.path.basename(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Update title/header with proper name
    proper_name = ALL_DOCS.get(fname, "")
    if proper_name:
        raw = update_page_title(raw, proper_name)

    # Find content-wrapper
    match = re.search(
        r'(<main class="content-wrapper">)(.*?)(</main>)',
        raw, re.DOTALL
    )
    if not match:
        return False, "No content-wrapper found"

    content = match.group(2)
    enhanced = enhance_content(content)

    new_raw = raw[:match.start()] + match.group(1) + enhanced + match.group(3) + raw[match.end():]

    # Inject ToC CSS if we added a ToC
    if '<div class="toc">' in enhanced:
        new_raw = inject_toc_css(new_raw)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_raw)

    return True, "OK"


# ----------------------------------------------------------------
# Index page generation (copy from reformat.py with updated names)
# ----------------------------------------------------------------
def load_reformat_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "reformat", os.path.join(ROOT_DIR, "reformat.py")
    )
    mod = importlib.util.load_from_spec(spec)  # won't work easily, just regenerate inline


INDEX_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
        --navy: #1c3557;
        --navy-light: #2a4a7a;
        --gold: #9a6e1a;
        --gold-light: #f5edda;
        --cream: #faf7f2;
        --paper: #ffffff;
        --text: #2d2929;
        --text-muted: #7a726b;
        --border: #ddd5c8;
        --shadow: rgba(28, 53, 87, 0.12);
    }

    body {
        font-family: 'Source Sans 3', system-ui, sans-serif;
        background: var(--cream);
        color: var(--text);
        line-height: 1.85;
        font-size: 17px;
        min-height: 100vh;
    }

    a { color: var(--navy); text-decoration: none; }
    a:hover { color: var(--gold); text-decoration: underline; }

    .hero {
        background: linear-gradient(135deg, var(--navy) 0%, #263f6b 60%, #2a4a7a 100%);
        color: white;
        padding: 90px 30px 80px;
        text-align: center;
        border-bottom: 5px solid var(--gold);
    }
    .hero h1 {
        font-family: 'Lora', Georgia, serif;
        font-size: 3rem;
        font-weight: 600;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .hero .subtitle {
        font-size: 1.15rem;
        opacity: 0.82;
        max-width: 580px;
        margin: 0 auto;
        line-height: 1.6;
        font-weight: 300;
    }

    .intro-block {
        max-width: 720px;
        margin: 55px auto;
        padding: 0 30px;
    }
    .intro-card {
        background: var(--paper);
        border: 1px solid var(--border);
        border-left: 4px solid var(--gold);
        border-radius: 6px;
        padding: 28px 32px;
        box-shadow: 0 2px 12px var(--shadow);
    }
    .intro-card h2 {
        font-family: 'Lora', Georgia, serif;
        color: var(--navy);
        font-size: 1.1rem;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .intro-card p {
        margin-bottom: 0.8em;
        color: #4a4540;
        line-height: 1.75;
        font-size: 0.96rem;
    }
    .intro-card p:last-child { margin-bottom: 0; }

    .categories-section {
        max-width: 1060px;
        margin: 0 auto 70px;
        padding: 0 30px;
    }

    .category-block { margin-bottom: 50px; }

    .category-header {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--gold);
    }
    .category-header .icon { font-size: 1.3rem; }
    .category-header h2 {
        font-family: 'Lora', Georgia, serif;
        color: var(--navy);
        font-size: 1.4rem;
        font-weight: 600;
    }
    .category-header .desc {
        color: var(--text-muted);
        font-size: 0.88rem;
        margin-left: auto;
        font-style: italic;
    }

    .doc-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
        gap: 12px;
    }
    .doc-card {
        background: var(--paper);
        border: 1px solid var(--border);
        border-radius: 7px;
        padding: 14px 18px;
        transition: border-color 0.18s, box-shadow 0.18s, transform 0.12s;
    }
    .doc-card:hover {
        border-color: var(--gold);
        box-shadow: 0 3px 14px var(--shadow);
        transform: translateY(-1px);
    }
    .doc-card a {
        color: var(--navy);
        font-weight: 600;
        font-size: 0.95rem;
        display: block;
        line-height: 1.4;
    }
    .doc-card:hover a { color: var(--gold); text-decoration: none; }

    footer.site-footer {
        background: var(--navy);
        color: rgba(255,255,255,0.5);
        text-align: center;
        padding: 30px;
        font-size: 0.82rem;
        letter-spacing: 0.2px;
    }
"""


def extract_intro_text():
    """Extract intro paragraphs from Formål.html."""
    formal_path = os.path.join(HTML_DIR, "Formål.html")
    if not os.path.exists(formal_path):
        return ""
    with open(formal_path, encoding='utf-8') as f:
        raw = f.read()
    m = re.search(r'class="content-wrapper"[^>]*>(.*?)</main>', raw, re.DOTALL)
    if not m:
        return ""
    soup = BeautifulSoup(m.group(1), 'html.parser')
    paras = []
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 60:
            paras.append(f"<p>{text}</p>")
        if len(paras) >= 3:
            break
    return "\n".join(paras)


def make_index_page(intro_text=""):
    categories_html = ""
    for cat in CATEGORIES:
        docs_html = ""
        for fname in cat["docs"]:
            label = ALL_DOCS.get(fname, fname)
            docs_html += f"""
            <div class="doc-card">
                <a href="HTML/{fname}">{label}</a>
            </div>"""
        categories_html += f"""
        <div class="category-block">
            <div class="category-header">
                <span class="icon">{cat["icon"]}</span>
                <h2>{cat["title"]}</h2>
                <span class="desc">{cat["description"]}</span>
            </div>
            <div class="doc-grid">{docs_html}
            </div>
        </div>
"""

    intro_section = ""
    if intro_text:
        intro_section = f"""
    <div class="intro-block">
        <div class="intro-card">
            <h2>Om arkivet</h2>
            {intro_text}
        </div>
    </div>
"""

    return f"""<!DOCTYPE html>
<html lang="nb">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historisk arkiv – Sundlo og Ringset-slektene</title>
    <style>{INDEX_CSS}
    </style>
</head>
<body>
    <header class="hero">
        <h1>Historisk arkiv</h1>
        <p class="subtitle">Sundlo- og Ringset-slektenes historiearkiv –<br>
        norske frivillige i Russland og slektshistorie</p>
    </header>

{intro_section}
    <section class="categories-section">
{categories_html}
    </section>

    <footer class="site-footer">
        Historisk arkiv – Sundlo og Ringset-slektene &nbsp;·&nbsp;
        Nedskrevet av Harald Sundlo, Asker 1993/94
    </footer>
</body>
</html>
"""


def main():
    print("=" * 60)
    print("Historisk Arkiv – Enhancer (ToC + Names)")
    print("=" * 60)

    html_files = [f for f in os.listdir(HTML_DIR)
                  if f.endswith('.html') and f.lower() != 'index.html']

    ok = 0
    toc_added = 0
    errors = []

    print(f"\nProcessing {len(html_files)} files...")
    for fname in sorted(html_files):
        path = os.path.join(HTML_DIR, fname)
        success, msg = process_file(path)
        if success:
            # Check if ToC was added
            with open(path, encoding='utf-8') as f:
                content = f.read()
            has_toc = '<div class="toc">' in content
            status = "OK+ToC" if has_toc else "OK"
            if has_toc:
                toc_added += 1
            print(f"  {status}: {fname}")
            ok += 1
        else:
            print(f"  ERR: {fname}: {msg}")
            errors.append(fname)

    print(f"\nProcessed {ok}/{len(html_files)} files, {toc_added} with ToC")
    if errors:
        print(f"Errors: {errors}")

    print("\nRegenerating root index.html...")
    intro = extract_intro_text()
    index_html = make_index_page(intro)
    with open(os.path.join(ROOT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("OK: index.html")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
