#!/usr/bin/env python3
"""
Enhances the already-reformatted HTML files:
  - Gives proper names to unnamed hist* documents
  - Promotes standalone <b> paragraphs to <h2> section headings
  - Removes <sdfield> LibreOffice artifacts
  - Adds anchor IDs to all headings
  - Generates a Table of Contents for documents with 3+ headings
  - Regenerates the root index.html with updated names
  - Extracts shared CSS to style.css
  - Adds search link to content page nav
  - Adds prev/next navigation between documents in same category
  - Adds reading time estimates
  - Adds cross-references between people
  - Adds print stylesheet
  - Generates person/place index page
  - Generates family tree page
  - Generates timeline page
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
    "formaal.html": "Formål – innledning av Harald Sundlo",

    # Konrad Sundlo forteller
    "russland-byen-gylne-skinn-1.html": "Russland & Byen med det gylne skinn – del 1",
    "byen-gylne-skinn-2.html":             "Russland & Byen med det gylne skinn – del 2",
    "byen-gylne-skinn-3-nansen.html":   "Russland & Byen med det gylne skinn – del 3 og Nansen",
    "byen-med-kanonen.html":                        "Narvik 1940 – Byen med kanonen",

    # Politikompaniet
    "1.Politi.html":  "1. Politikompani – Fenrik Bødtker forteller",
    "2-politi.html":  "1. Politikompani – Fortellinger del 2",
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
    "hist9-conrad-lassen.html":               "Conrad Lassen",
    "hist10-konrad-bertram-holm-sundlo.html":  "Konrad Bertram Holm Sundlo",
    "hist13-johan-marius-sundlo.html":        "Johan Marius Sundlo",
    "hist15.html":                             "Halfdan Sundlo",
    "hist16.html":                             "John Kjelbergsen Sundlo",
    "hist17.html":                             "Grim Saxvik",
    "hist22.html":                             "Mortine Kjelbergsdatter Sundlo",
    "hist23-kjelberg-johnsen-sundlo.html":     "Kjelberg Johnsen Sundlo",
    "hist37-albertine-sundlo.html":            "Albertine Sundlo",
    "hist38-othelie-sundlo.html":              "Othelie Sundlo",
    "hist119.html":                            "Anders Larsen Holm",
    "hist139-peder-paulsen-leth.html":      "Peder Paulsen (Leth)",
    "hist140.html":                            "Paul Jensen Tved",
    "hist142-paul-pedersen-dons.html":         "Paul Pedersen Dons",
    "hist151-lorentz-dons.html":               "Lorentz Dons",
    "hist154-mathias-conrad-peterson.html":    "Mathias Conrad Peterson",
    "hist156-johan-peter-muller.html":         "Johan Peter Muller",
    "hist158-karl-dons.html":                  "Karl Dons",
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
    "hist431-marie-saxvik.html":               "Marie Saxvik",

    # Ringsetslekten
    "marta-ringset-minneoppgave.html": "Marta Ringset – Minneoppgave",
}

# ----------------------------------------------------------------
# Categories for the index page
# ----------------------------------------------------------------
CATEGORIES = [
    {
        "title": "Formål og bakgrunn",
        "description": "Innledning og bakgrunnen for dette arkivet",
        "icon": "📜",
        "docs": ["formaal.html"],
    },
    {
        "title": "Konrad Sundlo forteller",
        "description": "Erindringer fra Kaukasus og Russland, nedskrevet av Harald Sundlo",
        "icon": "📖",
        "docs": [
            "russland-byen-gylne-skinn-1.html",
            "byen-gylne-skinn-2.html",
            "byen-gylne-skinn-3-nansen.html",
            "byen-med-kanonen.html",
        ],
    },
    {
        "title": "Politikompaniet",
        "description": "Historier fra 1. Politikompani – Den Norske Legion",
        "icon": "⚔️",
        "docs": ["1.Politi.html", "2-politi.html", "3politi.html"],
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
            "hist9-conrad-lassen.html",
            "hist10-konrad-bertram-holm-sundlo.html",
            "hist13-johan-marius-sundlo.html",
            "hist15.html", "hist16.html", "hist17.html", "hist22.html",
            "hist23-kjelberg-johnsen-sundlo.html",
            "hist37-albertine-sundlo.html", "hist38-othelie-sundlo.html",
            "hist119.html",
            "hist139-peder-paulsen-leth.html",
            "hist140.html",
            "hist142-paul-pedersen-dons.html",
            "hist151-lorentz-dons.html",
            "hist154-mathias-conrad-peterson.html",
            "hist156-johan-peter-muller.html",
            "hist158-karl-dons.html",
            "hist163.html",
            "hist235.html",
            "hist274.html", "hist282.html",
            "hist431-marie-saxvik.html",
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
            "marta-ringset-minneoppgave.html",
            "hist205.html",
            "hist430.html",
        ],
    },
]

# ----------------------------------------------------------------
# Build navigation maps
# ----------------------------------------------------------------
def build_nav_map():
    """Build prev/next navigation map from CATEGORIES."""
    nav = {}
    for cat in CATEGORIES:
        docs = cat["docs"]
        for i, fname in enumerate(docs):
            prev_doc = docs[i - 1] if i > 0 else None
            next_doc = docs[i + 1] if i < len(docs) - 1 else None
            nav[fname] = {
                "category": cat["title"],
                "prev": prev_doc,
                "next": next_doc,
            }
    return nav

NAV_MAP = build_nav_map()

# ----------------------------------------------------------------
# Person names for cross-referencing
# ----------------------------------------------------------------
def build_person_index():
    """Extract person names from document titles for cross-referencing."""
    persons = {}
    # Only cross-reference documents that are clearly about a person
    for fname, title in ALL_DOCS.items():
        # Skip non-person documents
        if fname.startswith(("formaal", "russland", "byen-", "1.Politi", "2-politi",
                           "3politi", "5konordl", "7konordl", "Legiogri", "Legpans",
                           "Reggerm", "Skibat", "hist235", "hist274", "hist282",
                           "marta-ringset")):
            continue
        # Clean title: remove prefixes like "Gjørtleren på Jøråshaugen – "
        name = title
        if " – " in name:
            parts = name.split(" – ")
            # Use the part that looks most like a person name
            for part in parts:
                if any(c.isupper() for c in part[1:]):
                    name = part.strip()
                    break
        # Skip very short names
        if len(name) < 6:
            continue
        persons[name] = fname
    return persons

PERSON_INDEX = build_person_index()

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

# ----------------------------------------------------------------
# Nav/footer CSS for prev/next, search link, reading time
# ----------------------------------------------------------------
EXTRA_CSS = """
    /* Reading time badge */
    .reading-time {
        display: inline-block;
        margin-top: 8px;
        padding: 4px 12px;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 999px;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.85);
        letter-spacing: 0.3px;
    }

    /* Search link in nav */
    .nav-search {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 5px;
        opacity: 0.75;
        font-size: 0.82rem;
    }
    .nav-search:hover { opacity: 1; }
    .nav-search svg {
        width: 14px;
        height: 14px;
        fill: currentColor;
    }

    /* Prev/Next navigation */
    .doc-nav {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-top: 3em;
        padding-top: 1.5em;
        border-top: 2px solid var(--border, #ddd5c8);
    }
    .doc-nav a {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 12px 16px;
        border: 1px solid var(--border, #ddd5c8);
        border-radius: 8px;
        max-width: 48%;
        transition: border-color 0.15s, box-shadow 0.15s;
        text-decoration: none;
    }
    .doc-nav a:hover {
        border-color: var(--gold, #9a6e1a);
        box-shadow: 0 2px 8px rgba(28,53,87,0.1);
        text-decoration: none;
    }
    .doc-nav .nav-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-muted, #7a726b);
    }
    .doc-nav .nav-title {
        font-family: 'Lora', Georgia, serif;
        font-weight: 600;
        font-size: 0.92rem;
        color: var(--navy, #1c3557);
    }
    .doc-nav a:hover .nav-title {
        color: var(--gold, #9a6e1a);
    }
    .doc-nav .next {
        margin-left: auto;
        text-align: right;
    }

    /* Cross-reference links */
    a.xref {
        color: var(--navy, #1c3557);
        border-bottom: 1px dashed var(--gold, #9a6e1a);
        text-decoration: none;
    }
    a.xref:hover {
        color: var(--gold, #9a6e1a);
        border-bottom-style: solid;
    }

    /* Print styles */
    @media print {
        nav.top-nav, footer.page-footer, .toc, .doc-nav, .reading-time { display: none; }
        .page-header { background: none !important; color: #000 !important; border-bottom: 2px solid #333; padding: 20px 0; }
        .page-header h1 { color: #000; font-size: 1.6rem; }
        .content-wrapper { box-shadow: none; padding: 20px 0; max-width: 100%; }
        body { background: #fff; font-size: 11pt; line-height: 1.5; }
        a { color: #000; text-decoration: none; }
        a.xref { border-bottom: none; }
        a.xref::after { content: ' [→ ' attr(title) ']'; font-size: 0.85em; color: #666; }
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
    """Return the heading text if <p> is a candidate for heading promotion."""
    if tag.name != 'p':
        return False
    children = [c for c in tag.children
                if not (isinstance(c, NavigableString) and not c.strip())]
    if len(children) == 1 and children[0].name == 'b':
        text = children[0].get_text(strip=True)
        if 3 < len(text) < 150:
            return text
    if len(children) == 2:
        first, second = children
        stripped = first.strip() if isinstance(first, NavigableString) else ''
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


def calculate_reading_time(text):
    """Estimate reading time in minutes from text content."""
    words = len(re.findall(r'\w+', text))
    minutes = max(1, round(words / 200))
    return minutes


def add_cross_references(soup, current_fname):
    """Add cross-reference links to person names found in the text."""
    for name, target_fname in PERSON_INDEX.items():
        if target_fname == current_fname:
            continue
        # Find text nodes containing this name
        for text_node in soup.find_all(string=re.compile(re.escape(name))):
            parent = text_node.parent
            # Don't link inside headings, existing links, or the ToC
            if parent.name in ('a', 'h1', 'h2', 'h3', 'h4', 'title'):
                continue
            if parent.find_parent('a') or parent.find_parent('div', class_='toc'):
                continue
            # Only replace first occurrence per text node
            if name in str(text_node):
                parts = str(text_node).split(name, 1)
                if len(parts) == 2:
                    new_content = BeautifulSoup(
                        f'{parts[0]}<a href="{target_fname}" class="xref" title="{ALL_DOCS.get(target_fname, name)}">{name}</a>{parts[1]}',
                        'html.parser'
                    )
                    text_node.replace_with(new_content)
                    break  # Only first occurrence per document


def enhance_content(html_content, current_fname=""):
    """Process the content-wrapper HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove any previously-generated .toc divs
    for toc_div in soup.find_all('div', class_='toc'):
        toc_div.decompose()

    # Remove previously-generated doc-nav
    for nav_div in soup.find_all('nav', class_='doc-nav'):
        nav_div.decompose()

    # Remove previously-generated reading-time spans
    for rt in soup.find_all('span', class_='reading-time'):
        rt.decompose()

    # Remove <sdfield> tags
    for sf in soup.find_all('sdfield'):
        sf.decompose()

    # Remove empty <p>
    for p in soup.find_all('p'):
        if not p.get_text(strip=True) and not p.find(['img', 'table']):
            p.decompose()

    # Promote standalone bold <p> to <h2>
    for p in list(soup.find_all('p')):
        bold_text = is_standalone_bold_heading(p)
        if bold_text:
            h2 = soup.new_tag('h2')
            h2.string = clean_tabs(bold_text)
            p.replace_with(h2)

    # Promote single-item <ol> to <h2>
    for ol in list(soup.find_all('ol')):
        lis = ol.find_all('li', recursive=False)
        if len(lis) == 1:
            text = clean_tabs(lis[0].get_text(strip=True))
            if 2 < len(text) < 120:
                h2 = soup.new_tag('h2')
                h2.string = text
                ol.replace_with(h2)

    # Style multi-item <ol> after "Innhold" as doc-toc
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
            doc_toc_done = True

    # Clean heading text and add anchor IDs
    slug_counts = {}
    for h in soup.find_all(['h1', 'h2', 'h3']):
        raw_text = h.get_text()
        clean_text = re.sub(r'[\t\n\r]+', ' ', raw_text)
        clean_text = re.sub(r' {2,}', ' ', clean_text).strip()
        if h.string and (('\t' in h.string) or ('\n' in h.string)):
            h.string = clean_text

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

    # Add cross-references
    if current_fname:
        add_cross_references(soup, current_fname)

    # Generate ToC
    toc_items = []
    headings = soup.find_all(['h1', 'h2', 'h3'])
    for h in headings:
        if h.name in ('h2', 'h3'):
            raw = h.get_text()
            text = re.sub(r'[\t\n\r]+', ' ', raw)
            text = re.sub(r' {2,}', ' ', text).strip()
            anchor = h.get('id', '')
            if text and anchor:
                toc_items.append((h.name, text, anchor))

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

    # Build prev/next nav
    nav_html = ""
    if current_fname and current_fname in NAV_MAP:
        nav_info = NAV_MAP[current_fname]
        prev_doc = nav_info["prev"]
        next_doc = nav_info["next"]
        if prev_doc or next_doc:
            nav_items = ""
            if prev_doc:
                prev_title = ALL_DOCS.get(prev_doc, prev_doc)
                nav_items += f'<a href="{prev_doc}" class="prev"><span class="nav-label">Forrige</span><span class="nav-title">{prev_title}</span></a>'
            if next_doc:
                next_title = ALL_DOCS.get(next_doc, next_doc)
                nav_items += f'<a href="{next_doc}" class="next"><span class="nav-label">Neste</span><span class="nav-title">{next_title}</span></a>'
            nav_html = f'<nav class="doc-nav" aria-label="Dokumentnavigasjon">{nav_items}</nav>'

    result = str(soup)
    if toc_html:
        result = toc_html + "\n" + result
    if nav_html:
        result = result + "\n" + nav_html

    return result


def inject_toc_css(html_file_content):
    """Inject TOC CSS into an existing HTML file's <style> block (idempotent)."""
    if '.toc {' in html_file_content:
        return html_file_content
    return html_file_content.replace(
        '\n    </style>',
        TOC_CSS + '\n    </style>',
        1
    )


def inject_extra_css(html_file_content):
    """Inject extra CSS for nav, reading time, cross-refs, print (idempotent)."""
    if '.doc-nav {' in html_file_content:
        return html_file_content
    return html_file_content.replace(
        '\n    </style>',
        EXTRA_CSS + '\n    </style>',
        1
    )


def update_page_title(html_content, new_title):
    """Update the <title> and page-header <h1> with the proper name."""
    html_content = re.sub(
        r'<title>[^<]+</title>',
        f'<title>{new_title} – Historisk arkiv</title>',
        html_content
    )
    html_content = re.sub(
        r'(<header class="page-header">\s*<h1>)[^<]*(</h1>)',
        rf'\g<1>{new_title}\g<2>',
        html_content
    )
    return html_content


def add_search_link(html_content):
    """Add search link to the nav bar (idempotent)."""
    if 'nav-search' in html_content:
        return html_content
    search_link = (
        '<a href="../index.html?q=" class="nav-search" title="Søk i arkivet">'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2.5"/>'
        '<line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>'
        ' Søk</a>'
    )
    # Insert before closing </div> of nav-inner
    html_content = html_content.replace(
        '<a href="../about.html" class="nav-about">Om arkivet</a>',
        f'{search_link}\n            <a href="../about.html" class="nav-about">Om arkivet</a>',
        1
    )
    return html_content


def add_reading_time(html_content, minutes):
    """Add reading time badge in the page header (idempotent)."""
    if 'reading-time' in html_content:
        return html_content
    badge = f'<span class="reading-time">~{minutes} min lesing</span>'
    html_content = html_content.replace(
        '</h1>\n    </header>',
        f'</h1>\n        {badge}\n    </header>',
        1
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

    # Calculate reading time before enhancement
    plain_text = BeautifulSoup(content, 'html.parser').get_text()
    reading_minutes = calculate_reading_time(plain_text)

    enhanced = enhance_content(content, current_fname=fname)

    new_raw = raw[:match.start()] + match.group(1) + enhanced + match.group(3) + raw[match.end():]

    # Inject CSS
    if '<div class="toc">' in enhanced:
        new_raw = inject_toc_css(new_raw)
    new_raw = inject_extra_css(new_raw)

    # Add search link and reading time
    new_raw = add_search_link(new_raw)
    new_raw = add_reading_time(new_raw, reading_minutes)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_raw)

    return True, f"OK ({reading_minutes} min)"


# ----------------------------------------------------------------
# Index page generation
# ----------------------------------------------------------------
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
    """Extract intro paragraphs from formaal.html."""
    formal_path = os.path.join(HTML_DIR, "formaal.html")
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


# ----------------------------------------------------------------
# Person/Place Index Page
# ----------------------------------------------------------------
def generate_person_index_page():
    """Generate an alphabetical index of all people documented."""
    entries = []
    for fname, title in sorted(ALL_DOCS.items(), key=lambda x: x[1]):
        entries.append((title, f"HTML/{fname}"))

    # Group by first letter
    groups = {}
    for title, href in entries:
        letter = title[0].upper()
        if letter.isdigit() or not letter.isalpha():
            letter = "#"
        groups.setdefault(letter, []).append((title, href))

    letter_nav = " ".join(
        f'<a href="#{letter}">{letter}</a>' for letter in sorted(groups.keys())
    )

    content = ""
    for letter in sorted(groups.keys()):
        content += f'<h2 id="{letter}">{letter}</h2>\n<ul>\n'
        for title, href in groups[letter]:
            content += f'  <li><a href="{href}">{title}</a></li>\n'
        content += '</ul>\n'

    return f"""<!DOCTYPE html>
<html lang="nb">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Navneregister – Historisk arkiv</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
    :root{{--navy:#1c3557;--navy-light:#2a4a7a;--gold:#9a6e1a;--gold-light:#f5edda;--cream:#faf7f2;--paper:#ffffff;--text:#2d2929;--text-muted:#7a726b;--border:#ddd5c8;--shadow:rgba(28,53,87,0.12);}}
    body{{font-family:'Source Sans 3',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.85;font-size:17px;min-height:100vh;}}
    a{{color:var(--navy);text-decoration:none;}} a:hover{{color:var(--gold);text-decoration:underline;}}
    nav.top-nav{{background:var(--navy);padding:12px 30px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.2);}}
    nav.top-nav a{{color:rgba(255,255,255,0.88);font-size:0.88rem;font-weight:600;letter-spacing:0.3px;}}
    nav.top-nav a:hover{{color:#fff;text-decoration:none;}}
    nav.top-nav .nav-inner{{max-width:860px;margin:0 auto;display:flex;align-items:center;gap:12px;}}
    .page-header{{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 100%);color:white;padding:55px 30px 50px;text-align:center;border-bottom:4px solid var(--gold);}}
    .page-header h1{{font-family:'Lora',Georgia,serif;font-size:2.1rem;font-weight:600;line-height:1.3;max-width:760px;margin:0 auto;}}
    .content-wrapper{{max-width:720px;margin:0 auto;padding:50px 30px 80px;background:var(--paper);box-shadow:0 0 40px var(--shadow);min-height:60vh;}}
    .letter-nav{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:2em;padding-bottom:1.5em;border-bottom:2px solid var(--border);}}
    .letter-nav a{{display:inline-block;width:2.2em;height:2.2em;line-height:2.2em;text-align:center;border:1px solid var(--border);border-radius:6px;font-weight:600;transition:0.15s;}}
    .letter-nav a:hover{{background:var(--gold-light);border-color:var(--gold);text-decoration:none;}}
    h2{{font-family:'Lora',Georgia,serif;color:var(--navy);font-size:1.35rem;font-weight:600;margin-top:2em;margin-bottom:0.7em;scroll-margin-top:60px;border-bottom:1px solid var(--border);padding-bottom:6px;}}
    h2:first-of-type{{margin-top:0;}}
    ul{{list-style:none;padding:0;}}
    li{{margin-bottom:0.5em;padding:6px 0;border-bottom:1px solid #f0ebe3;}}
    li a{{font-weight:600;}}
    footer.page-footer{{text-align:center;padding:28px 30px;background:var(--navy);color:rgba(255,255,255,0.55);font-size:0.82rem;}}
    footer.page-footer a{{color:rgba(255,255,255,0.7);}}
    @media print{{nav.top-nav,footer.page-footer,.letter-nav{{display:none;}}.page-header{{background:none!important;color:#000!important;border-bottom:2px solid #333;padding:20px 0;}}.page-header h1{{color:#000;}}.content-wrapper{{box-shadow:none;padding:20px 0;}}body{{background:#fff;}}a{{color:#000;}}}}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-inner">
            <a href="index.html">Historisk arkiv</a>
            <span style="color:rgba(255,255,255,0.35)">·</span>
            <a href="index.html">Tilbake til oversikten</a>
        </div>
    </nav>
    <header class="page-header">
        <h1>Navneregister</h1>
    </header>
    <main class="content-wrapper">
        <div class="letter-nav">{letter_nav}</div>
        {content}
    </main>
    <footer class="page-footer">
        Historisk arkiv – Sundlo og Ringset-slektene &nbsp;|&nbsp;
        <a href="index.html">Tilbake til oversikten</a>
    </footer>
</body>
</html>
"""


# ----------------------------------------------------------------
# Family Tree Page
# ----------------------------------------------------------------
def generate_family_tree_page():
    """Generate a simple family tree visualization."""
    return """<!DOCTYPE html>
<html lang="nb">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slektstre – Historisk arkiv</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{--navy:#1c3557;--navy-light:#2a4a7a;--gold:#9a6e1a;--gold-light:#f5edda;--cream:#faf7f2;--paper:#ffffff;--text:#2d2929;--text-muted:#7a726b;--border:#ddd5c8;--shadow:rgba(28,53,87,0.12);}
    body{font-family:'Source Sans 3',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.85;font-size:17px;min-height:100vh;}
    a{color:var(--navy);text-decoration:none;} a:hover{color:var(--gold);text-decoration:underline;}
    nav.top-nav{background:var(--navy);padding:12px 30px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.2);}
    nav.top-nav a{color:rgba(255,255,255,0.88);font-size:0.88rem;font-weight:600;letter-spacing:0.3px;}
    nav.top-nav a:hover{color:#fff;text-decoration:none;}
    nav.top-nav .nav-inner{max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:12px;}
    .page-header{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 100%);color:white;padding:55px 30px 50px;text-align:center;border-bottom:4px solid var(--gold);}
    .page-header h1{font-family:'Lora',Georgia,serif;font-size:2.1rem;font-weight:600;line-height:1.3;max-width:760px;margin:0 auto;}
    .page-header p{margin-top:10px;opacity:0.85;font-size:1rem;}
    .content-wrapper{max-width:1100px;margin:0 auto;padding:50px 30px 80px;background:var(--paper);box-shadow:0 0 40px var(--shadow);min-height:60vh;}

    .tree-section{margin-bottom:3em;}
    .tree-section h2{font-family:'Lora',Georgia,serif;color:var(--navy);font-size:1.4rem;font-weight:600;margin-bottom:1em;padding-bottom:8px;border-bottom:2px solid var(--gold);}

    .tree{display:flex;flex-direction:column;align-items:center;}
    .tree-row{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-bottom:8px;position:relative;}
    .tree-connector{width:2px;height:20px;background:var(--border);margin:0 auto;}
    .tree-branch{display:flex;justify-content:center;position:relative;margin-bottom:8px;}
    .tree-branch::before{content:'';position:absolute;top:0;left:25%;right:25%;height:2px;background:var(--border);}

    .person{display:inline-block;padding:10px 16px;border:2px solid var(--border);border-radius:8px;background:var(--paper);text-align:center;min-width:160px;transition:0.15s;}
    .person:hover{border-color:var(--gold);box-shadow:0 2px 10px var(--shadow);}
    .person a{display:block;}
    .person .name{font-family:'Lora',Georgia,serif;font-weight:600;font-size:0.95rem;color:var(--navy);}
    .person:hover .name{color:var(--gold);}
    .person .dates{font-size:0.82rem;color:var(--text-muted);margin-top:2px;}
    .person .role{font-size:0.78rem;color:var(--text-muted);font-style:italic;margin-top:2px;}
    .person.highlight{border-color:var(--gold);background:var(--gold-light);}
    .person.couple{border-style:double;border-width:3px;}
    .marriage{display:flex;align-items:center;gap:12px;margin-bottom:8px;justify-content:center;flex-wrap:wrap;}
    .marriage-symbol{font-size:1.2rem;color:var(--gold);}
    .children-row{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;padding-top:12px;border-top:2px solid var(--border);margin-top:8px;}

    .legend{display:flex;gap:20px;flex-wrap:wrap;margin-top:2em;padding:16px;background:var(--gold-light);border-radius:8px;font-size:0.88rem;}
    .legend-item{display:flex;align-items:center;gap:6px;}
    .legend-swatch{width:20px;height:20px;border-radius:4px;border:2px solid;}

    footer.page-footer{text-align:center;padding:28px 30px;background:var(--navy);color:rgba(255,255,255,0.55);font-size:0.82rem;}
    footer.page-footer a{color:rgba(255,255,255,0.7);}

    @media (max-width:700px){
        .person{min-width:120px;padding:8px 10px;}
        .person .name{font-size:0.85rem;}
        .marriage{flex-direction:column;gap:6px;}
    }
    @media print{nav.top-nav,footer.page-footer{display:none;}.page-header{background:none!important;color:#000!important;border-bottom:2px solid #333;padding:20px 0;}.page-header h1{color:#000;}.content-wrapper{box-shadow:none;padding:20px 0;max-width:100%;}body{background:#fff;}a{color:#000;}}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-inner">
            <a href="index.html">Historisk arkiv</a>
            <span style="color:rgba(255,255,255,0.35)">·</span>
            <a href="index.html">Tilbake til oversikten</a>
        </div>
    </nav>
    <header class="page-header">
        <h1>Slektstre</h1>
        <p>En forenklet oversikt over familielinjene Sundlo, Speilberg, Ringset og Baade</p>
    </header>
    <main class="content-wrapper">

        <div class="tree-section">
            <h2>Sundlo-linjen</h2>
            <div class="tree">
                <div class="tree-row">
                    <div class="person">
                        <a href="HTML/hist3.html">
                            <div class="name">Jørgen Pederssøn Schjelderup</div>
                            <div class="role">Tidlig stamfar</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row">
                    <div class="person">
                        <a href="HTML/hist16.html">
                            <div class="name">John Kjelbergsen Sundlo</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row">
                    <div class="person">
                        <a href="HTML/hist23-kjelberg-johnsen-sundlo.html">
                            <div class="name">Kjelberg Johnsen Sundlo</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row">
                    <div class="person">
                        <a href="HTML/hist13-johan-marius-sundlo.html">
                            <div class="name">Johan Marius Sundlo</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="marriage">
                    <div class="person highlight">
                        <a href="HTML/hist10-konrad-bertram-holm-sundlo.html">
                            <div class="name">Konrad Bertram Holm Sundlo</div>
                            <div class="dates">1881–1965</div>
                            <div class="role">Oberst, Hålogaland inf.reg.</div>
                        </a>
                    </div>
                    <span class="marriage-symbol">&#9829;</span>
                    <div class="person">
                        <div class="name">Katrine Speilberg</div>
                        <div class="role">f. Speilberg</div>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="marriage">
                    <div class="person highlight">
                        <div class="name">Harald Sundlo</div>
                        <div class="dates">1927–2019</div>
                        <div class="role">Samlet og nedskrev arkivet</div>
                    </div>
                    <span class="marriage-symbol">&#9829;</span>
                    <div class="person">
                        <div class="name">Borgny Ringset</div>
                        <div class="role">f. Ringset</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tree-section">
            <h2>Speilberg-linjen</h2>
            <div class="tree">
                <div class="tree-row">
                    <div class="person">
                        <a href="HTML/hist5.html">
                            <div class="name">Hans Nielsen Speilberg</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row">
                    <div class="person">
                        <a href="HTML/hist9-conrad-lassen.html">
                            <div class="name">Conrad Lassen</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row">
                    <div class="person">
                        <div class="name">Katrine Speilberg</div>
                        <div class="role">Gift med Konrad Sundlo</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tree-section">
            <h2>Baade / Ringset-linjen</h2>
            <div class="tree">
                <div class="tree-row" style="gap:40px;">
                    <div class="person">
                        <a href="HTML/hist208.html">
                            <div class="name">Michel Baade</div>
                            <div class="role">Hanseatisk kjøpmann, Bergen</div>
                        </a>
                    </div>
                    <div class="person">
                        <a href="HTML/hist205.html">
                            <div class="name">Frøystein Ringset</div>
                            <div class="role">Liabygda, Sunnmøre</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row" style="gap:40px;">
                    <div class="person">
                        <a href="HTML/hist209.html">
                            <div class="name">Hans Baade</div>
                        </a>
                    </div>
                    <div class="person">
                        <a href="HTML/hist430.html">
                            <div class="name">Nils Edvard Olsen Ringset</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row" style="gap:40px;">
                    <div class="person">
                        <a href="HTML/hist310.html">
                            <div class="name">Fredrik Anton Olai Baade</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="marriage">
                    <div class="person">
                        <div class="name">Marta Baade Ringset</div>
                        <div class="role">f. Baade</div>
                    </div>
                    <span class="marriage-symbol">&#9829;</span>
                    <div class="person">
                        <a href="HTML/hist430.html">
                            <div class="name">Nils Edvard Ringset</div>
                        </a>
                    </div>
                </div>
                <div class="tree-connector"></div>
                <div class="tree-row">
                    <div class="person">
                        <div class="name">Borgny Ringset</div>
                        <div class="role">Gift med Harald Sundlo</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tree-section">
            <h2>Andre familiemedlemmer i arkivet</h2>
            <div class="children-row" style="border-top:none;margin-top:0;">
                <div class="person"><a href="HTML/hist15.html"><div class="name">Halfdan Sundlo</div></a></div>
                <div class="person"><a href="HTML/hist22.html"><div class="name">Mortine Kjelbergsdatter Sundlo</div></a></div>
                <div class="person"><a href="HTML/hist37-albertine-sundlo.html"><div class="name">Albertine Sundlo</div></a></div>
                <div class="person"><a href="HTML/hist38-othelie-sundlo.html"><div class="name">Othelie Sundlo</div></a></div>
                <div class="person"><a href="HTML/hist17.html"><div class="name">Grim Saxvik</div></a></div>
                <div class="person"><a href="HTML/hist431-marie-saxvik.html"><div class="name">Marie Saxvik</div></a></div>
                <div class="person"><a href="HTML/hist119.html"><div class="name">Anders Larsen Holm</div></a></div>
                <div class="person"><a href="HTML/hist163.html"><div class="name">Christian Andersen Holm</div></a></div>
                <div class="person"><a href="HTML/hist160.html"><div class="name">Georg Burchard Baade</div></a></div>
                <div class="person"><a href="HTML/hist210.html"><div class="name">Daniel Baade</div></a></div>
                <div class="person"><a href="HTML/hist212.html"><div class="name">Peter Baade</div></a></div>
                <div class="person"><a href="HTML/hist213.html"><div class="name">Steffen Baade</div></a></div>
                <div class="person"><a href="HTML/hist254.html"><div class="name">Peter Daniel Baade</div></a></div>
                <div class="person"><a href="HTML/hist255.html"><div class="name">Michael Baade</div></a></div>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item"><div class="legend-swatch" style="border-color:var(--gold);background:var(--gold-light);"></div> Nøkkelpersoner</div>
            <div class="legend-item"><div class="legend-swatch" style="border-color:var(--border);background:var(--paper);"></div> Dokumenterte personer</div>
            <div class="legend-item"><span class="marriage-symbol">&#9829;</span> Ekteskap</div>
        </div>
    </main>
    <footer class="page-footer">
        Historisk arkiv – Sundlo og Ringset-slektene &nbsp;|&nbsp;
        <a href="index.html">Tilbake til oversikten</a>
    </footer>
</body>
</html>
"""


# ----------------------------------------------------------------
# Timeline Page
# ----------------------------------------------------------------
def generate_timeline_page():
    """Generate a chronological timeline of key events."""
    return """<!DOCTYPE html>
<html lang="nb">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tidslinje – Historisk arkiv</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{--navy:#1c3557;--navy-light:#2a4a7a;--gold:#9a6e1a;--gold-light:#f5edda;--cream:#faf7f2;--paper:#ffffff;--text:#2d2929;--text-muted:#7a726b;--border:#ddd5c8;--shadow:rgba(28,53,87,0.12);}
    body{font-family:'Source Sans 3',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.85;font-size:17px;min-height:100vh;}
    a{color:var(--navy);text-decoration:none;} a:hover{color:var(--gold);text-decoration:underline;}
    nav.top-nav{background:var(--navy);padding:12px 30px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.2);}
    nav.top-nav a{color:rgba(255,255,255,0.88);font-size:0.88rem;font-weight:600;letter-spacing:0.3px;}
    nav.top-nav a:hover{color:#fff;text-decoration:none;}
    nav.top-nav .nav-inner{max-width:860px;margin:0 auto;display:flex;align-items:center;gap:12px;}
    .page-header{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 100%);color:white;padding:55px 30px 50px;text-align:center;border-bottom:4px solid var(--gold);}
    .page-header h1{font-family:'Lora',Georgia,serif;font-size:2.1rem;font-weight:600;line-height:1.3;max-width:760px;margin:0 auto;}
    .page-header p{margin-top:10px;opacity:0.85;font-size:1rem;}
    .content-wrapper{max-width:800px;margin:0 auto;padding:50px 30px 80px;background:var(--paper);box-shadow:0 0 40px var(--shadow);min-height:60vh;}

    .timeline{position:relative;padding-left:40px;}
    .timeline::before{content:'';position:absolute;left:14px;top:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--gold),var(--navy));border-radius:2px;}
    .timeline-era{margin-bottom:2.5em;}
    .timeline-era h2{font-family:'Lora',Georgia,serif;color:var(--navy);font-size:1.25rem;font-weight:600;margin-bottom:1em;padding-bottom:6px;border-bottom:1px solid var(--border);}
    .tl-item{position:relative;margin-bottom:1.5em;padding-left:16px;}
    .tl-item::before{content:'';position:absolute;left:-32px;top:6px;width:12px;height:12px;background:var(--gold);border:3px solid var(--paper);border-radius:50%;box-shadow:0 0 0 2px var(--gold);}
    .tl-year{font-family:'Lora',Georgia,serif;font-weight:600;color:var(--gold);font-size:1rem;margin-bottom:2px;}
    .tl-text{font-size:0.95rem;color:var(--text);line-height:1.6;}
    .tl-text a{font-weight:600;}
    .tl-tag{display:inline-block;margin-top:4px;padding:2px 8px;background:var(--gold-light);border-radius:4px;font-size:0.78rem;color:#5b4d2f;}

    footer.page-footer{text-align:center;padding:28px 30px;background:var(--navy);color:rgba(255,255,255,0.55);font-size:0.82rem;}
    footer.page-footer a{color:rgba(255,255,255,0.7);}

    @media print{nav.top-nav,footer.page-footer{display:none;}.page-header{background:none!important;color:#000!important;border-bottom:2px solid #333;padding:20px 0;}.page-header h1{color:#000;}.content-wrapper{box-shadow:none;padding:20px 0;max-width:100%;}body{background:#fff;}.timeline::before{background:#333;}.tl-item::before{background:#333;box-shadow:none;border-color:#fff;}}
    </style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-inner">
            <a href="index.html">Historisk arkiv</a>
            <span style="color:rgba(255,255,255,0.35)">·</span>
            <a href="index.html">Tilbake til oversikten</a>
        </div>
    </nav>
    <header class="page-header">
        <h1>Tidslinje</h1>
        <p>Viktige hendelser i Sundlo- og Ringset-slektenes historie</p>
    </header>
    <main class="content-wrapper">
        <div class="timeline">

            <div class="timeline-era">
                <h2>Tidlige røtter</h2>
                <div class="tl-item">
                    <div class="tl-year">ca. 850</div>
                    <div class="tl-text"><a href="HTML/hist274.html">Harald Hårfagre</a> og <a href="HTML/hist282.html">Halvdan Svarte</a> – de eldste genealogiske tilknytningene i arkivet.</div>
                    <span class="tl-tag">Genealogi</span>
                </div>
            </div>

            <div class="timeline-era">
                <h2>1600–1700-tallet</h2>
                <div class="tl-item">
                    <div class="tl-year">1600-tallet</div>
                    <div class="tl-text"><a href="HTML/hist3.html">Jørgen Pederssøn Schjelderup</a> – tidlig stamfar i Sundlo-linjen.</div>
                    <span class="tl-tag">Sundlo-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">Tidlig 1700-tall</div>
                    <div class="tl-text"><a href="HTML/hist208.html">Michel Baade</a> ankommer Bergen som hanseatisk kjøpmann fra Mecklenburg.</div>
                    <span class="tl-tag">Baade-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1700-tallet</div>
                    <div class="tl-text"><a href="HTML/hist209.html">Hans Baade</a>, <a href="HTML/hist212.html">Peter Baade</a> og <a href="HTML/hist213.html">Steffen Baade</a> i Bergen.</div>
                    <span class="tl-tag">Baade-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1700-tallet</div>
                    <div class="tl-text"><a href="HTML/hist5.html">Hans Nielsen Speilberg</a> – prestefamilien Speilberg.</div>
                    <span class="tl-tag">Speilberg-slekten</span>
                </div>
            </div>

            <div class="timeline-era">
                <h2>1800-tallet</h2>
                <div class="tl-item">
                    <div class="tl-year">1800-tallet</div>
                    <div class="tl-text"><a href="HTML/hist9-conrad-lassen.html">Conrad Lassen</a>, <a href="HTML/hist139-peder-paulsen-leth.html">Peder Paulsen (Leth)</a>, <a href="HTML/hist142-paul-pedersen-dons.html">Paul Pedersen Dons</a> og andre i Sundlo/Speilberg-kretsen.</div>
                    <span class="tl-tag">Sundlo-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1881</div>
                    <div class="tl-text"><a href="HTML/hist10-konrad-bertram-holm-sundlo.html">Konrad Bertram Holm Sundlo</a> født.</div>
                    <span class="tl-tag">Sundlo-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1800-tallet</div>
                    <div class="tl-text"><a href="HTML/hist210.html">Daniel Baade</a> i Grønlandsmisjonen og <a href="HTML/hist255.html">Michael Baade</a> som misjonær i Porsanger.</div>
                    <span class="tl-tag">Baade-slekten</span>
                </div>
            </div>

            <div class="timeline-era">
                <h2>1900-tallet</h2>
                <div class="tl-item">
                    <div class="tl-year">1919</div>
                    <div class="tl-text">Konrad Sundlo i <a href="HTML/russland-byen-gylne-skinn-1.html">Kaukasus og Russland</a> – nedskrevet i «Byen med det gylne skinn».</div>
                    <span class="tl-tag">Konrad Sundlo forteller</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1927</div>
                    <div class="tl-text">Harald Sundlo født – sønn av Konrad og Katrine Sundlo.</div>
                    <span class="tl-tag">Sundlo-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">9. april 1940</div>
                    <div class="tl-text">Konrad Sundlo overgir <a href="HTML/byen-med-kanonen.html">Narvik</a> til tyske styrker – en av de mest omstridte hendelsene i norsk krigshistorie.</div>
                    <span class="tl-tag">Krigshistorie</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1941–1945</div>
                    <div class="tl-text">Norske frivillige i <a href="HTML/Legiogri.html">Den Norske Legion</a>, <a href="HTML/5konordl.html">Regiment Nordland</a> og <a href="HTML/Skibat.html">Skibataljonen</a> på Østfronten.</div>
                    <span class="tl-tag">Krigshistorie</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1965</div>
                    <div class="tl-text">Konrad Bertram Holm Sundlo dør.</div>
                    <span class="tl-tag">Sundlo-slekten</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">1992–1994</div>
                    <div class="tl-text">Harald Sundlo transkriberer farens notater og samler slektshistorisk materiale i Asker.</div>
                    <span class="tl-tag">Arkivets opprinnelse</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">2019</div>
                    <div class="tl-text">Harald Sundlo dør.</div>
                    <span class="tl-tag">Sundlo-slekten</span>
                </div>
            </div>

            <div class="timeline-era">
                <h2>2020-tallet</h2>
                <div class="tl-item">
                    <div class="tl-year">2025</div>
                    <div class="tl-text">Jan P. Pettersen utgir <em>Oberst Konrad Sundlo</em> – ny gjennomgang av rettsdokumentene.</div>
                    <span class="tl-tag">Litteratur</span>
                </div>
                <div class="tl-item">
                    <div class="tl-year">2025</div>
                    <div class="tl-text">Erik Sundlo digitaliserer og publiserer arkivet på nett.</div>
                    <span class="tl-tag">Arkivet</span>
                </div>
            </div>

        </div>
    </main>
    <footer class="page-footer">
        Historisk arkiv – Sundlo og Ringset-slektene &nbsp;|&nbsp;
        <a href="index.html">Tilbake til oversikten</a>
    </footer>
</body>
</html>
"""


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main():
    print("=" * 60)
    print("Historisk Arkiv – Enhancer (Full)")
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
            with open(path, encoding='utf-8') as f:
                content = f.read()
            has_toc = '<div class="toc">' in content
            status = "OK+ToC" if has_toc else "OK"
            if has_toc:
                toc_added += 1
            print(f"  {status}: {fname} ({msg})")
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

    print("\nGenerating person index page...")
    index_page = generate_person_index_page()
    with open(os.path.join(ROOT_DIR, "navneregister.html"), 'w', encoding='utf-8') as f:
        f.write(index_page)
    print("OK: navneregister.html")

    print("\nGenerating family tree page...")
    tree_page = generate_family_tree_page()
    with open(os.path.join(ROOT_DIR, "slektstre.html"), 'w', encoding='utf-8') as f:
        f.write(tree_page)
    print("OK: slektstre.html")

    print("\nGenerating timeline page...")
    timeline_page = generate_timeline_page()
    with open(os.path.join(ROOT_DIR, "tidslinje.html"), 'w', encoding='utf-8') as f:
        f.write(timeline_page)
    print("OK: tidslinje.html")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
