#!/usr/bin/env python3
"""Inline every asset that target/site/serenity/index.html depends on so it
renders identically to the local file:// version as a single HTML file.

Strategy:
  - Parse index.html.
  - For each <link rel="stylesheet" href="...">: replace with <style> whose
    contents have all url(...) and @import references inlined as data: URIs
    (or recursively for further CSS).
  - For each <script src="...">: replace with <script>contents</script>.
  - For each <img src="...">, <link rel="icon" href="..."> etc.: replace
    with a data: URI.
  - Recurse for CSS @import / url(...) references inside the inlined CSS.
  - Skip anything that's already absolute (http://, https://, data:).

The resulting file is one HTML document with no external dependencies, so
double-clicking it after download renders the full Serenity dashboard with
working charts/tables. Drilldown to feature pages is still not possible
(those are separate sibling HTML files) — use the ZIP artifact for that.

Usage:
    python3 inline_serenity_index.py <serenity_report_dir> <output_html>
"""
from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

CSS_URL_RE = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<url>[^)'\"]+)(?P=quote)\s*\)")
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\()?\s*['\"]?(?P<url>[^'\");]+)['\"]?\s*\)?\s*;", re.IGNORECASE)

LINK_RE = re.compile(
    r"<link\b(?P<attrs>[^>]*?)\s*/?>",
    re.IGNORECASE,
)
SCRIPT_RE = re.compile(
    r"<script\b(?P<attrs>[^>]*?)\s*(?:/>|>(?P<body>.*?)</script>)",
    re.IGNORECASE | re.DOTALL,
)
IMG_RE = re.compile(r"<img\b(?P<attrs>[^>]*?)\s*/?>", re.IGNORECASE)

ATTR_RE = re.compile(r"""(?P<name>[\w:-]+)\s*=\s*(?P<quote>['"])(?P<value>.*?)(?P=quote)""")


def parse_attrs(attrs: str) -> dict[str, str]:
    return {m.group("name").lower(): m.group("value") for m in ATTR_RE.finditer(attrs)}


def render_attrs(attrs: dict[str, str], drop: tuple[str, ...] = ()) -> str:
    parts = []
    for k, v in attrs.items():
        if k in drop:
            continue
        parts.append(f'{k}="{v}"')
    return (" " + " ".join(parts)) if parts else ""


def is_external(url: str) -> bool:
    if not url:
        return True
    if url.startswith(("data:", "http://", "https://", "mailto:", "#", "javascript:")):
        return True
    return False


def resolve(report_dir: Path, current: Path, ref: str) -> Path | None:
    """Resolve a relative reference (possibly with ?query / #fragment) to a path."""
    if is_external(ref):
        return None
    ref = unquote(urlparse(ref).path)
    if not ref:
        return None
    base = current.parent if current.is_file() else current
    candidate = (base / ref).resolve()
    try:
        candidate.relative_to(report_dir.resolve())
    except ValueError:
        # Outside report dir
        return None
    return candidate if candidate.exists() else None


def to_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if mime is None:
        # Common fallbacks Serenity uses
        ext = path.suffix.lower()
        mime = {
            ".woff2": "font/woff2",
            ".woff": "font/woff",
            ".ttf": "font/ttf",
            ".eot": "application/vnd.ms-fontobject",
            ".otf": "font/otf",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
        }.get(ext, "application/octet-stream")
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def inline_css(css_text: str, report_dir: Path, css_path: Path) -> str:
    """Inline url(...) and @import inside a CSS string."""
    def replace_import(match: re.Match) -> str:
        target = resolve(report_dir, css_path, match.group("url"))
        if target is None:
            return ""
        try:
            return inline_css(target.read_text(encoding="utf-8", errors="replace"), report_dir, target)
        except Exception:
            return ""

    css_text = CSS_IMPORT_RE.sub(replace_import, css_text)

    def replace_url(match: re.Match) -> str:
        url = match.group("url")
        target = resolve(report_dir, css_path, url)
        if target is None:
            return match.group(0)  # leave absolute / fragment / missing
        if target.suffix.lower() == ".css":
            # Inline nested CSS as raw text into the parent? CSS doesn't allow
            # that inside url(), so just inline as data URI.
            mime = "text/css"
            data = inline_css(
                target.read_text(encoding="utf-8", errors="replace"), report_dir, target
            ).encode("utf-8")
            b64 = base64.b64encode(data).decode("ascii")
            return f"url(data:{mime};base64,{b64})"
        try:
            return f"url({to_data_uri(target)})"
        except Exception:
            return match.group(0)

    return CSS_URL_RE.sub(replace_url, css_text)


def inline_link(match: re.Match, report_dir: Path, html_path: Path) -> str:
    attrs = parse_attrs(match.group("attrs"))
    rel = (attrs.get("rel") or "").lower()
    href = attrs.get("href", "")

    if not href or is_external(href):
        return match.group(0)

    target = resolve(report_dir, html_path, href)
    if target is None:
        return match.group(0)

    if "stylesheet" in rel:
        try:
            css = target.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return match.group(0)
        media = attrs.get("media")
        media_attr = f' media="{media}"' if media else ""
        inlined = inline_css(css, report_dir, target)
        return f"<style{media_attr}>\n{inlined}\n</style>"

    if rel in {"icon", "shortcut icon", "apple-touch-icon"} or rel.startswith("apple-touch-icon"):
        try:
            attrs["href"] = to_data_uri(target)
        except Exception:
            return match.group(0)
        return f"<link{render_attrs(attrs)}>"

    # Other link types: try to inline as data URI; otherwise leave alone.
    try:
        attrs["href"] = to_data_uri(target)
        return f"<link{render_attrs(attrs)}>"
    except Exception:
        return match.group(0)


def inline_script(match: re.Match, report_dir: Path, html_path: Path) -> str:
    attrs = parse_attrs(match.group("attrs"))
    src = attrs.get("src", "")
    body = match.group("body") or ""

    if not src:
        # Already inline; leave it.
        return match.group(0)

    if is_external(src):
        return match.group(0)

    target = resolve(report_dir, html_path, src)
    if target is None:
        return match.group(0)

    try:
        js = target.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return match.group(0)

    # Escape any "</script>" inside JS so the wrapping tag isn't broken.
    js = js.replace("</script>", "<\\/script>")
    attrs_render = render_attrs(attrs, drop=("src",))
    return f"<script{attrs_render}>\n{js}\n</script>"


def inline_img(match: re.Match, report_dir: Path, html_path: Path) -> str:
    attrs = parse_attrs(match.group("attrs"))
    src = attrs.get("src", "")
    if not src or is_external(src):
        return match.group(0)
    target = resolve(report_dir, html_path, src)
    if target is None:
        return match.group(0)
    try:
        attrs["src"] = to_data_uri(target)
    except Exception:
        return match.group(0)
    return f"<img{render_attrs(attrs)}>"


def inline_html(html_text: str, report_dir: Path, html_path: Path) -> str:
    html_text = LINK_RE.sub(lambda m: inline_link(m, report_dir, html_path), html_text)
    html_text = SCRIPT_RE.sub(lambda m: inline_script(m, report_dir, html_path), html_text)
    html_text = IMG_RE.sub(lambda m: inline_img(m, report_dir, html_path), html_text)
    return html_text


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2

    report_dir = Path(sys.argv[1]).resolve()
    output_html = Path(sys.argv[2])
    index_path = report_dir / "index.html"

    if not index_path.is_file():
        print(f"❌ index.html not found in {report_dir}", file=sys.stderr)
        return 1

    html_text = index_path.read_text(encoding="utf-8", errors="replace")
    inlined = inline_html(html_text, report_dir, index_path)

    # Add a small banner at the very top of <body> warning that drilldown is unavailable.
    banner = (
        '<div style="background:#fef3c7;border-bottom:1px solid #fcd34d;'
        'padding:10px 16px;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;'
        'font-size:13px;color:#92400e;">'
        '⚠️ This is a standalone copy of the Serenity dashboard. '
        'Top-level charts and totals render here, but clicking through to '
        'feature or scenario detail pages will not work — see the email '
        'for the full report download link.'
        '</div>'
    )
    inlined = re.sub(r"(<body[^>]*>)", r"\1" + banner, inlined, count=1, flags=re.IGNORECASE)

    output_html.write_text(inlined, encoding="utf-8")
    size_kb = output_html.stat().st_size / 1024
    print(f"✅ Wrote {output_html} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
