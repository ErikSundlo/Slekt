#!/usr/bin/env python3
"""
Reformats all HTML files in Konverter/HTML to be uniform and professional.
Creates a beautiful start page at the root.
"""

import os
import re
from bs4 import BeautifulSoup, NavigableString

HTML_DIR = r"C:\Users\eriks\OneDrive\Konverter\HTML"
ROOT_DIR = r"C:\Users\eriks\OneDrive\Konverter"

# Document categories (from existing index.html structure)
CATEGORIES = [
    {
        "title": "Formål og bakgrunn",
        "description": "Innledning og bakgrunnen for dette arkivet",
        "icon": "📜",
        "docs": [
            ("Formål.html", "Formål – innledning av Harald Sundlo"),
        ]
    },
    {
        "title": "Konrad Sundlo forteller",
        "description": "Erindringer fra Kaukasus og Russland, nedskrevet av Harald Sundlo",
        "icon": "📖",
        "docs": [
            ("Russland & Byen med det gylne skinn 1.html", "Russland & Byen med det gylne skinn – del 1"),
            ("Byen med det gylne skinn 2.html", "Byen med det gylne skinn – del 2"),
            ("Byen med det gylne skinn 3 og Nansen.html", "Byen med det gylne skinn – del 3 og Nansen"),
            ("Byen med kanonen.html", "Byen med kanonen"),
        ]
    },
    {
        "title": "Politikompaniet",
        "description": "Historier fra 1. Politikompani – Den Norske Legion",
        "icon": "⚔️",
        "docs": [
            ("1.Politi.html", "Politikompani – del 1"),
            ("2 Politi.html", "Politikompani – del 2"),
            ("3politi.html", "Politikompani – del 3"),
        ]
    },
    {
        "title": "Regiment Nordland",
        "description": "Beretninger fra Regiment Nordland",
        "icon": "🎖️",
        "docs": [
            ("5konordl.html", "Konferanse Regiment Nordland – del 1"),
            ("7konordl.html", "Konferanse Regiment Nordland – del 2"),
        ]
    },
    {
        "title": "Legioner og bataljoner",
        "description": "Historier fra Den Norske Legion og tilknyttede enheter",
        "icon": "🗂️",
        "docs": [
            ("Legiogri.html", "Legionens organisasjon og grunnlag"),
            ("Legpans.html", "Legionens pansertropper"),
            ("Reggerm.html", "Regiment Germania"),
            ("Skibat.html", "Skibataljonen"),
        ]
    },
    {
        "title": "Sundloslekten",
        "description": "Slektshistorie – familien Sundlo",
        "icon": "🌳",
        "docs": [
            ("hist3.html", "Slektshistorie 3"),
            ("hist5.html", "Slektshistorie 5"),
            ("hist 9 Conrad Lassen.html", "Conrad Lassen"),
            ("hist10 Konrad Bertram Holm Sundlo.html", "Konrad Bertram Holm Sundlo"),
            ("hist 13 Johan Marius Sundlo.html", "Johan Marius Sundlo"),
            ("hist15.html", "Slektshistorie 15"),
            ("hist16.html", "Slektshistorie 16"),
            ("hist17.html", "Slektshistorie 17"),
            ("hist22.html", "Slektshistorie 22"),
            ("hist23 Kjelberg Johnsen Sundlo.html", "Kjelberg Johnsen Sundlo"),
            ("hist37 Albertine Sundlo.html", "Albertine Sundlo"),
            ("hist38 Othelie Sundlo.html", "Othelie Sundlo"),
            ("hist119.html", "Slektshistorie 119"),
            ("hist139  Peder Paulsen (Leth).html", "Peder Paulsen (Leth)"),
            ("hist140.html", "Slektshistorie 140"),
            ("hist142 Paul Pedersen Dons.html", "Paul Pedersen Dons"),
            ("hist151 Lorentz Dons.html", "Lorentz Dons"),
            ("hist154 Mathias Conrad Peterson.html", "Mathias Conrad Peterson"),
            ("hist156 Johan Peter Muller.html", "Johan Peter Muller"),
            ("Hist158 Karl Dons.html", "Karl Dons"),
            ("hist160.html", "Slektshistorie 160"),
            ("hist163.html", "Slektshistorie 163"),
            ("hist205.html", "Slektshistorie 205"),
            ("hist208.html", "Slektshistorie 208"),
            ("hist209.html", "Slektshistorie 209"),
            ("hist210.html", "Slektshistorie 210"),
            ("hist212.html", "Slektshistorie 212"),
            ("hist213.html", "Slektshistorie 213"),
            ("hist235.html", "Slektshistorie 235"),
            ("hist254.html", "Slektshistorie 254"),
            ("hist255.html", "Slektshistorie 255"),
            ("hist274.html", "Slektshistorie 274"),
            ("hist282.html", "Slektshistorie 282"),
            ("hist310.html", "Slektshistorie 310"),
            ("hist430.html", "Slektshistorie 430"),
            ("hist431 Marie Saxvik.html", "Marie Saxvik"),
        ]
    },
    {
        "title": "Ringsetslekten",
        "description": "Slektshistorie – familien Ringset",
        "icon": "🌿",
        "docs": [
            ("Marta Ringset-Minneoppgave.html", "Marta Ringset – Minneoppgave"),
        ]
    },
]

# All known files in a flat list for lookup
ALL_DOCS = {}
for cat in CATEGORIES:
    for fname, label in cat["docs"]:
        ALL_DOCS[fname] = label


SHARED_CSS = """
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
"""

CONTENT_CSS = SHARED_CSS + """
    nav.top-nav {
        background: var(--navy);
        padding: 12px 30px;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    nav.top-nav a {
        color: rgba(255,255,255,0.88);
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: color 0.15s;
    }
    nav.top-nav a:hover { color: #fff; text-decoration: none; }
    nav.top-nav .nav-inner {
        max-width: 860px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    nav.top-nav .nav-home { opacity: 0.7; font-size: 0.82rem; }
    nav.top-nav .nav-sep { color: rgba(255,255,255,0.35); }

    .page-header {
        background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
        color: white;
        padding: 55px 30px 50px;
        text-align: center;
        border-bottom: 4px solid var(--gold);
    }
    .page-header h1 {
        font-family: 'Lora', Georgia, serif;
        font-size: 2.1rem;
        font-weight: 600;
        line-height: 1.3;
        max-width: 760px;
        margin: 0 auto;
    }

    .content-wrapper {
        max-width: 800px;
        margin: 0 auto;
        padding: 50px 30px 80px;
        background: var(--paper);
        box-shadow: 0 0 40px var(--shadow);
        min-height: 60vh;
    }

    .content-wrapper p {
        margin-bottom: 1.15em;
        text-align: justify;
        hyphens: auto;
    }
    .content-wrapper p:last-child { margin-bottom: 0; }

    .content-wrapper h1,
    .content-wrapper h2,
    .content-wrapper h3 {
        font-family: 'Lora', Georgia, serif;
        color: var(--navy);
        margin-top: 2em;
        margin-bottom: 0.7em;
        line-height: 1.3;
    }
    .content-wrapper h1 { font-size: 1.65rem; font-weight: 600; }
    .content-wrapper h2 { font-size: 1.35rem; font-weight: 600; }
    .content-wrapper h3 { font-size: 1.1rem; font-weight: 600; }
    .content-wrapper h1:first-child,
    .content-wrapper h2:first-child { margin-top: 0; }

    .content-wrapper ol, .content-wrapper ul {
        padding-left: 1.8em;
        margin-bottom: 1.2em;
    }
    .content-wrapper li { margin-bottom: 0.4em; }

    .content-wrapper blockquote {
        border-left: 3px solid var(--gold);
        padding-left: 20px;
        margin: 1.5em 0;
        color: #555;
        font-style: italic;
    }

    footer.page-footer {
        text-align: center;
        padding: 28px 30px;
        background: var(--navy);
        color: rgba(255,255,255,0.55);
        font-size: 0.82rem;
        letter-spacing: 0.2px;
    }
    footer.page-footer a {
        color: rgba(255,255,255,0.7);
    }
    footer.page-footer a:hover { color: #fff; }
"""

INDEX_CSS = SHARED_CSS + """
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

    .category-block {
        margin-bottom: 50px;
    }

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
        cursor: pointer;
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


def extract_inner_body(file_path):
    """Extract the LibreOffice HTML body content from the wrapper file.

    The LibreOffice HTML is identified by its <style type="text/css"> block,
    which distinguishes it from the outer wrapper's plain <style> tag.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # The inner LibreOffice HTML has <style type="text/css"> (outer wrapper CSS does not).
    # Find: LibreOffice style block -> </head> -> <body> -> CONTENT -> </body>
    match = re.search(
        r'<style\s+type=["\']text/css["\']>.*?</style>.*?</head>\s*<body[^>]*>(.*?)</body\s*>',
        raw, re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    # Fallback: try to find content inside a content-wrapper main tag
    content_match = re.search(
        r'class="content-wrapper"[^>]*>(.*?)</main>', raw, re.DOTALL
    )
    if content_match:
        return content_match.group(1).strip()

    return ""


def clean_content(html_str):
    """Clean up LibreOffice HTML markup into clean, semantic HTML."""
    soup = BeautifulSoup(html_str, 'html.parser')

    # Unwrap <font> tags (preserve children)
    for tag in soup.find_all('font'):
        tag.unwrap()

    # Unwrap <span> tags
    for tag in soup.find_all('span'):
        tag.unwrap()

    # Remove all style/class/lang/dir attributes
    REMOVE_ATTRS = {'style', 'class', 'lang', 'dir', 'align', 'valign',
                    'link', 'vlink', 'text', 'start'}
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            if attr in REMOVE_ATTRS:
                del tag[attr]

    # Remove empty paragraphs (only whitespace or <br/>)
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        # If only <br/> tags and no real text, remove
        children_text = ''.join(c for c in p.strings)
        if not children_text.strip():
            p.decompose()

    # Convert <ol start="X"> back (just remove start if it was already cleaned)
    # Already handled above

    result = str(soup)

    # Clean up multiple blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def get_doc_label(filename):
    """Get the human-readable label for a document filename."""
    return ALL_DOCS.get(filename, os.path.splitext(filename)[0])


def make_content_page(file_path, title, content_html, back_label="Tilbake til oversikten"):
    """Generate a clean, professional HTML content page."""
    fname = os.path.basename(file_path)
    doc_label = get_doc_label(fname)

    return f"""<!DOCTYPE html>
<html lang="nb">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_label} – Historisk arkiv</title>
    <style>{CONTENT_CSS}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-inner">
            <a href="../index.html" class="nav-home">Historisk arkiv</a>
            <span class="nav-sep">›</span>
            <a href="../index.html">{back_label}</a>
        </div>
    </nav>

    <header class="page-header">
        <h1>{doc_label}</h1>
    </header>

    <main class="content-wrapper">
        {content_html}
    </main>

    <footer class="page-footer">
        Historisk arkiv – Sundlo og Ringset-slektene &nbsp;|&nbsp;
        <a href="../index.html">Tilbake til oversikten</a>
    </footer>
</body>
</html>
"""


def make_index_page(intro_text=""):
    """Generate the beautiful root start page."""
    categories_html = ""
    for cat in CATEGORIES:
        docs_html = ""
        for fname, label in cat["docs"]:
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


def extract_intro_text():
    """Extract a short intro paragraph from Formål.html."""
    formal_path = os.path.join(HTML_DIR, "Formål.html")
    if not os.path.exists(formal_path):
        return ""

    inner_html = extract_inner_body(formal_path)
    if not inner_html:
        return ""

    cleaned = clean_content(inner_html)
    soup = BeautifulSoup(cleaned, 'html.parser')

    # Get the meaningful paragraphs (skip very short ones)
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 60:
            paragraphs.append(str(p))
        if len(paragraphs) >= 3:
            break

    return "\n".join(paragraphs)


def process_all_files():
    """Process all HTML content files and create clean versions."""
    processed = 0
    errors = []

    # Get all HTML files in HTML_DIR (excluding index.html)
    html_files = [f for f in os.listdir(HTML_DIR)
                  if f.endswith('.html') and f.lower() != 'index.html']

    print(f"Processing {len(html_files)} HTML files...")

    for filename in html_files:
        file_path = os.path.join(HTML_DIR, filename)
        try:
            # Extract inner body content
            inner_body = extract_inner_body(file_path)

            if not inner_body.strip():
                print(f"  WARNING: No inner body found in {filename}")
                errors.append(filename)
                continue

            # Clean the content
            cleaned = clean_content(inner_body)

            if not cleaned.strip():
                print(f"  WARNING: Empty cleaned content for {filename}")
                errors.append(filename)
                continue

            # Get document title/label
            doc_label = get_doc_label(filename)

            # Generate new page
            new_html = make_content_page(file_path, doc_label, cleaned)

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_html)

            processed += 1
            print(f"  OK: {filename}")

        except Exception as e:
            print(f"  ERR: {filename}: {e}")
            errors.append(filename)

    print(f"\nProcessed {processed}/{len(html_files)} files")
    if errors:
        print(f"Errors/warnings: {errors}")

    return errors


def create_html_index():
    """Create a clean index in the HTML folder (for direct browsing)."""
    categories_html = ""
    for cat in CATEGORIES:
        links_html = ""
        for fname, label in cat["docs"]:
            links_html += f'<li><a href="{fname}">{label}</a></li>\n'
        categories_html += f"""
        <section>
            <h2>{cat["title"]}</h2>
            <ul>{links_html}</ul>
        </section>"""

    html = f"""<!DOCTYPE html>
<html lang="nb">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dokumentoversikt – Historisk arkiv</title>
    <meta http-equiv="refresh" content="0; url=../index.html">
</head>
<body>
    <p>Videresender til <a href="../index.html">forsiden</a>...</p>
</body>
</html>
"""
    index_path = os.path.join(HTML_DIR, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("OK: HTML/index.html (redirect)")


def create_root_index():
    """Create the beautiful root start page."""
    intro_text = extract_intro_text()
    index_html = make_index_page(intro_text)

    root_index = os.path.join(ROOT_DIR, "index.html")
    with open(root_index, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("OK: Root index.html (start page)")


def main():
    print("=" * 60)
    print("Historisk Arkiv – HTML Reformatter")
    print("=" * 60)

    print("\n[1] Processing content files...")
    errors = process_all_files()

    print("\n[2] Creating HTML folder index (redirect)...")
    create_html_index()

    print("\n[3] Creating root start page...")
    create_root_index()

    print("\n" + "=" * 60)
    print("Done! Open index.html in the Konverter folder to view.")
    print("=" * 60)


if __name__ == "__main__":
    main()
