#!/usr/bin/env python3
"""
Generates index.html from content.json + template.html.

You normally never run this by hand: editing content.json on github.com and
committing triggers the GitHub Action, which runs this script and publishes the
result. To rebuild locally (optional): `python3 build.py`.

Text fields in content.json accept a little Markdown:
  **bold**            -> <strong>bold</strong>
  *italic*            -> <em>italic</em>
  [label](https://…)  -> <a href="https://…">label</a>
"""

import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent


def strip_trailing_commas(text):
    """Remove commas that sit right before a closing ] or } (the most common
    hand-editing slip), while ignoring anything inside quoted strings."""
    out, in_string, escape = [], False, False
    for i, ch in enumerate(text):
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            continue
        if ch == ",":
            j = i + 1
            while j < len(text) and text[j] in " \t\r\n":
                j += 1
            if j < len(text) and text[j] in "]}":
                continue  # drop the trailing comma
        out.append(ch)
    return "".join(out)


def load_content(path):
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(strip_trailing_commas(raw))
    except json.JSONDecodeError as e:
        lines = raw.splitlines()
        bad = lines[e.lineno - 1].strip() if 0 <= e.lineno - 1 < len(lines) else ""
        print(
            f"\n  content.json couldn't be read: {e.msg} (line {e.lineno}).\n"
            f"    {bad}\n\n"
            "  Common causes: a missing comma between entries, a missing quotation\n"
            '  mark, or an unescaped " inside some text. Fix that line and re-run.\n',
            file=sys.stderr,
        )
        sys.exit(1)


CONTENT = load_content(HERE / "content.json")
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")


def attr(text):
    """Escape a plain string for use inside an HTML attribute or text node."""
    return html.escape(str(text), quote=True)


def inline(text):
    """Convert the small Markdown subset to HTML (escaping everything else)."""
    out = html.escape(str(text), quote=False)          # 1. neutralise & < >
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)  # 2. **bold**
    out = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", out)  # 3. *italic*
    # 4. [label](url) — the url is already &<>-escaped by step 1, so only
    #    quotes still need escaping for the attribute (avoids double-escaping).
    out = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2).replace(chr(34), "&quot;")}" target="_blank" rel="noopener">{m.group(1)}</a>',
        out,
    )
    return out


def slug(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(text).lower())).strip("-")


def render_section(sec):
    heading, kind = sec["heading"], sec.get("type", "publications")
    items = sec.get("items", [])
    if not items:                       # empty sections are left off the live page
        return ""
    sid = slug(heading) + "-heading"
    rows = []
    if kind == "projects":
        list_class = "project-list"
        for item in items:
            rows.append(f"        <li>{inline(item)}</li>")
    else:                               # publications-style list
        list_class = "pub-list"
        for item in items:
            body = inline(item["citation"])
            if item.get("pdf"):
                body += f' <a class="pdf" href="{attr(item["pdf"])}" target="_blank" rel="noopener">[pdf]</a>'
            rows.append(f"        <li>{body}</li>")
    parts = [
        f'    <section aria-labelledby="{sid}">',
        f'      <h2 id="{sid}">{inline(heading)}</h2>',
        f'      <ul class="{list_class}">',
        *rows,
        "      </ul>",
    ]
    note = sec.get("note")
    if note:
        parts.append(
            f'      <p class="more"><a href="{attr(note["url"])}" target="_blank" rel="noopener">{inline(note["text"])}</a></p>'
        )
    parts.append("    </section>")
    return "\n".join(parts)


def render_footer(footer):
    parts = [
        "    <footer>",
        "      <!-- Email is plain text on purpose, to avoid scraping. -->",
        f'      <span>{inline(footer["email"])}</span>',
    ]
    for link in footer.get("links", []):
        parts.append(f'      <a href="{attr(link["url"])}" target="_blank" rel="noopener">{inline(link["text"])}</a>')
    parts.append("    </footer>")
    return "\n".join(parts)


blocks = [
    f'    <h1>{inline(CONTENT["name"])}</h1>',
    f'    <p class="focus">{inline(CONTENT["focus"])}</p>',
    f'    <p class="roles">{inline(CONTENT["roles"])}</p>',
]
for section in CONTENT.get("sections", []):
    rendered = render_section(section)
    if rendered:
        blocks.append("")
        blocks.append(rendered)
blocks.append("")
blocks.append(render_footer(CONTENT["footer"]))
content_html = "\n".join(blocks)

page = (
    TEMPLATE
    .replace("{{NAME}}", attr(CONTENT["name"]))
    .replace("{{META_DESCRIPTION}}", attr(CONTENT["metaDescription"]))
    .replace("{{FOCUS}}", attr(CONTENT["focus"]))
    .replace("{{CONTENT}}", content_html)
)

banner = "<!-- GENERATED FILE — do not edit directly. Edit content.json; the site rebuilds automatically. -->\n"
page = page.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + banner, 1)

(HERE / "index.html").write_text(page, encoding="utf-8")
print("Wrote index.html")
