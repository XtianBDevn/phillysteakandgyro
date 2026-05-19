#!/usr/bin/env python3
"""
Mirror phillysteakgyros.com into ./mirror/ with all CSS, JS, fonts and images.

Approach:
  1. BFS from a seed list of page URLs.
  2. For each HTML page: fetch, parse, find asset refs (link, script, img, srcset,
     inline style url(...), preload).
  3. For each CSS file: fetch, find url(...) and @import refs.
  4. Save everything under mirror/, mapping remote hosts to subfolders.
  5. Rewrite HTML/CSS to use relative paths that work from file:// or a static server.

Limitations:
  - Wix is a heavy SPA; runtime data fetches (XHR/GraphQL) are not replayed.
    The rendered HTML the server returns is preserved, which is enough to get
    the visual layout + above-the-fold content. Dynamic widgets that fetch
    on load (e.g. the live menu app) will show their last-rendered snapshot.
  - Does not execute JS; data: URIs left alone; protocol-relative URLs normalised.
"""

from __future__ import annotations
import os
import re
import sys
import time
import subprocess
import urllib.parse as up
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "mirror"
SEED = [
    "https://www.phillysteakgyros.com/",
    "https://www.phillysteakgyros.com/menu-1",
    "https://www.phillysteakgyros.com/menu-1?menu=menu",
]
ALLOWED_PAGE_HOSTS = {"www.phillysteakgyros.com", "phillysteakgyros.com"}
ASSET_HOSTS_ALLOW = {
    "www.phillysteakgyros.com", "phillysteakgyros.com",
    "static.wixstatic.com", "static.parastorage.com",
    "siteassets.parastorage.com", "frog.wix.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")

# in-memory state
fetched: dict[str, bytes] = {}
local_path_by_url: dict[str, Path] = {}
asset_queue: list[tuple[str, str]] = []  # (url, kind)
page_queue: list[str] = []
seen_pages: set[str] = set()
seen_assets: set[str] = set()
errors: list[tuple[str, str]] = []


def http_get(url: str) -> bytes | None:
    """Fetch URL via curl (uses system CA store, no Python SSL pain)."""
    try:
        p = subprocess.run(
            ["curl", "-sSL", "-g", "--fail", "--max-time", "30",
             "-A", UA, "-H", "Accept: */*",
             "-H", "Referer: https://www.phillysteakgyros.com/",
             url],
            capture_output=True, timeout=45)
        if p.returncode != 0:
            errors.append((url, p.stderr.decode("utf-8", "replace")[:200]))
            return None
        return p.stdout
    except Exception as e:
        errors.append((url, repr(e)))
        return None


def normalise(url: str, base: str) -> str | None:
    """Resolve to absolute https URL. Returns None if not http(s)."""
    if not url:
        return None
    url = url.strip()
    if url.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
        return None
    if url.startswith("//"):
        url = "https:" + url
    abs_url = up.urljoin(base, url)
    parts = up.urlsplit(abs_url)
    if parts.scheme not in ("http", "https"):
        return None
    # strip fragment, keep query
    return up.urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def local_path_for(url: str) -> Path:
    """Map a remote URL to a local file path under mirror/."""
    parts = up.urlsplit(url)
    host = parts.netloc
    path = parts.path
    if path.endswith("/") or path == "":
        path = path + "index.html"
    # avoid traversal, collapse double slashes
    path = re.sub(r"/{2,}", "/", path)
    safe = path.lstrip("/")
    # encode the query as a suffix so duplicate-path-different-query files
    # don't clobber each other
    if parts.query:
        q = re.sub(r"[^A-Za-z0-9._-]", "_", parts.query)[:80]
        base, _, ext = safe.rpartition(".")
        if base:
            safe = f"{base}__{q}.{ext}"
        else:
            safe = f"{safe}__{q}"
    return ROOT / host / safe


def relpath(from_file: Path, to_file: Path) -> str:
    """POSIX-style relative path for use in HTML/CSS."""
    rel = os.path.relpath(to_file, start=from_file.parent)
    return rel.replace(os.sep, "/")


def enqueue_asset(url: str, kind: str) -> Path | None:
    """Register an asset for download, return its planned local path."""
    if not url:
        return None
    host = up.urlsplit(url).netloc
    if host and host not in ASSET_HOSTS_ALLOW:
        # 3rd-party tracker etc. — skip but still record so we know.
        return None
    if url in seen_assets:
        return local_path_by_url[url]
    seen_assets.add(url)
    p = local_path_for(url)
    local_path_by_url[url] = p
    asset_queue.append((url, kind))
    return p


def enqueue_page(url: str) -> None:
    host = up.urlsplit(url).netloc
    if host not in ALLOWED_PAGE_HOSTS:
        return
    if url in seen_pages:
        return
    seen_pages.add(url)
    page_queue.append(url)


# -------- HTML parsing --------

ATTRS_URL = {
    "href": {"link", "a"},
    "src": {"script", "img", "iframe", "source", "video", "audio"},
    "data-src": {"img"},
    "data-href": {"a"},
    "poster": {"video"},
    "content": {"meta"},  # og:image, twitter:image
}


class Linker(HTMLParser):
    def __init__(self, page_url: str):
        super().__init__(convert_charrefs=False)
        self.page_url = page_url
        self.page_path = local_path_by_url[page_url]
        self.out: list[str] = []
        # capture <style> blocks for CSS rewriting
        self._in_style = False
        self._style_buf: list[str] = []

    def _attr_str(self, attrs):
        parts = []
        for k, v in attrs:
            if v is None:
                parts.append(k)
            else:
                v_esc = v.replace('"', "&quot;")
                parts.append(f'{k}="{v_esc}"')
        return " ".join(parts)

    def _rewrite_attr(self, tag, attrs):
        new_attrs = []
        for k, v in attrs:
            if v is None or not v:
                new_attrs.append((k, v))
                continue
            kind = None
            if k == "srcset" and tag in ("img", "source"):
                # srcset candidates are separated by COMMA + WHITESPACE.
                # Plain commas can appear inside URL paths (e.g. Wix CDN's
                # /v1/fill/w_219,h_147,al_c,...). Split only on ",\s+".
                pieces = []
                for piece in re.split(r",\s+", v):
                    piece = piece.strip().rstrip(",")
                    if not piece:
                        continue
                    bits = piece.split(None, 1)
                    src = bits[0]
                    desc = bits[1] if len(bits) > 1 else ""
                    abs_u = normalise(src, self.page_url)
                    if abs_u:
                        local = enqueue_asset(abs_u, "img")
                        if local:
                            pieces.append((relpath(self.page_path, local) +
                                           ((" " + desc) if desc else "")))
                            continue
                    pieces.append(piece)
                v = ", ".join(pieces)
                new_attrs.append((k, v))
                continue

            if k == "style":
                v = self._rewrite_css_block(v)
                new_attrs.append((k, v))
                continue

            if k in ("href", "data-href") and tag == "link":
                rel = dict(attrs).get("rel", "").lower()
                if "stylesheet" in rel:
                    kind = "css"
                elif rel in ("icon", "shortcut icon", "apple-touch-icon",
                             "mask-icon", "manifest", "preload"):
                    # preload "as" can be style/script/fetch/image/font
                    as_attr = dict(attrs).get("as", "").lower()
                    kind = "css" if as_attr == "style" else "asset"
            elif k == "href" and tag == "a":
                abs_u = normalise(v, self.page_url)
                if abs_u and up.urlsplit(abs_u).netloc in ALLOWED_PAGE_HOSTS:
                    enqueue_page(abs_u)
                    if abs_u in local_path_by_url:
                        v = relpath(self.page_path, local_path_by_url[abs_u])
                new_attrs.append((k, v))
                continue
            elif k in ("src", "data-src") and tag == "script":
                kind = "js"
            elif k in ("src", "data-src", "poster") and tag in (
                    "img", "iframe", "source", "video", "audio"):
                kind = "asset"
            elif k == "content" and tag == "meta":
                # only rewrite og:image / twitter:image style meta
                attr_d = dict(attrs)
                name = (attr_d.get("property") or attr_d.get("name") or "").lower()
                if "image" in name and ("http" in v or v.startswith("//")):
                    kind = "asset"

            if kind:
                abs_u = normalise(v, self.page_url)
                if abs_u:
                    local = enqueue_asset(abs_u, kind)
                    if local:
                        v = relpath(self.page_path, local)
            new_attrs.append((k, v))
        return new_attrs

    def _rewrite_css_block(self, css_text: str) -> str:
        def repl(m):
            raw = m.group(1).strip().strip("'\"")
            abs_u = normalise(raw, self.page_url)
            if not abs_u:
                return m.group(0)
            local = enqueue_asset(abs_u, "asset")
            if not local:
                return m.group(0)
            return f"url('{relpath(self.page_path, local)}')"
        return re.sub(r"url\(\s*([^)]+?)\s*\)", repl, css_text)

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self._in_style = True
            self._style_buf = []
            self.out.append(self.get_starttag_text() or f"<{tag}>")
            return
        new_attrs = self._rewrite_attr(tag, attrs)
        attr_str = self._attr_str(new_attrs)
        self.out.append(f"<{tag}{(' ' + attr_str) if attr_str else ''}>")

    def handle_startendtag(self, tag, attrs):
        new_attrs = self._rewrite_attr(tag, attrs)
        attr_str = self._attr_str(new_attrs)
        self.out.append(f"<{tag}{(' ' + attr_str) if attr_str else ''} />")

    def handle_endtag(self, tag):
        if tag == "style" and self._in_style:
            css = "".join(self._style_buf)
            self.out.append(self._rewrite_css_block(css))
            self._in_style = False
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self._in_style:
            self._style_buf.append(data)
        else:
            self.out.append(data)

    def handle_entityref(self, name):
        self.out.append(f"&{name};")

    def handle_charref(self, name):
        self.out.append(f"&#{name};")

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.out.append(f"<!{decl}>")


def safe_write(p: Path, body: bytes | str, mode: str = "wb") -> Path:
    """Write `body` to `p`, handling Wix's file-vs-dir path collisions.

    static.wixstatic.com uses both /media/foo.png (raw image) AND
    /media/foo.png/v1/fill/... (derived resize). Same prefix is a file in
    one URL and a directory in another. We rename the file leaf to
    foo.png__raw.png when a sibling directory needs to live there.
    """
    # If any parent path component is currently a FILE (not a dir), rename it
    # so we can mkdir over it.
    parts = p.parts
    for i in range(len(parts) - 1, 0, -1):
        ancestor = Path(*parts[:i])
        if ancestor.exists() and not ancestor.is_dir():
            # rename the file leaf to free up the directory name
            stem = ancestor.name
            ext = ancestor.suffix or ".bin"
            new_name = ancestor.with_name(stem + "__raw" + ext) if ancestor.suffix \
                else ancestor.with_name(stem + "__raw")
            ancestor.rename(new_name)
            # update the URL → local mapping so HTML refs follow the rename
            for u, lp in list(local_path_by_url.items()):
                if lp == ancestor:
                    local_path_by_url[u] = new_name
    p.parent.mkdir(parents=True, exist_ok=True)
    # If our target itself already exists as a dir, write to a sibling.
    if p.exists() and p.is_dir():
        stem = p.name
        ext = p.suffix or ".bin"
        p = p.with_name(stem + "__raw" + ext) if p.suffix \
            else p.with_name(stem + "__raw")
    if mode == "wb":
        p.write_bytes(body)
    else:
        p.write_text(body, encoding="utf-8")
    return p


def process_page(url: str):
    print(f"[page] {url}")
    body = http_get(url)
    if body is None:
        return
    p = local_path_for(url)
    local_path_by_url[url] = p
    fetched[url] = body
    text = body.decode("utf-8", errors="replace")
    parser = Linker(url)
    parser.feed(text)
    parser.close()
    rewritten = "".join(parser.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rewritten, encoding="utf-8")


def process_css(url: str, body: bytes):
    p = local_path_by_url[url]
    text = body.decode("utf-8", errors="replace")

    def repl_url(m):
        raw = m.group(1).strip().strip("'\"")
        abs_u = normalise(raw, url)
        if not abs_u:
            return m.group(0)
        local = enqueue_asset(abs_u, "asset")
        if not local:
            return m.group(0)
        return f"url('{relpath(p, local)}')"

    def repl_import(m):
        raw = m.group(1).strip().strip("'\"")
        abs_u = normalise(raw, url)
        if not abs_u:
            return m.group(0)
        local = enqueue_asset(abs_u, "css")
        if not local:
            return m.group(0)
        return f"@import url('{relpath(p, local)}')"

    text = re.sub(r"url\(\s*([^)]+?)\s*\)", repl_url, text)
    text = re.sub(r"@import\s+(?:url\()?\s*(['\"][^'\"]+['\"])\s*\)?", repl_import, text)
    final = safe_write(p, text, mode="wt")
    local_path_by_url[url] = final


def process_binary(url: str, body: bytes):
    p = local_path_by_url[url]
    final = safe_write(p, body, mode="wb")
    local_path_by_url[url] = final


def process_js(url: str, body: bytes):
    p = local_path_by_url[url]
    final = safe_write(p, body, mode="wb")
    local_path_by_url[url] = final


def deep_scan_for_assets():
    """Wix inlines CSS/JS/font URLs inside <script> JSON config blobs and
    JS bundles. The HTML parser only sees <link>/<script>/<img> attributes;
    those config URLs slip through. Do a brute-force regex scan over every
    fetched HTML and JS file and queue anything that looks like an asset."""
    url_re = re.compile(
        r"https?://(?:static\.parastorage\.com|static\.wixstatic\.com|"
        r"siteassets\.parastorage\.com|fonts\.googleapis\.com|"
        r"fonts\.gstatic\.com)"
        r"/[^\s'\"<>()\\]+?\.(?:css|js|woff2?|ttf|otf|eot|png|jpe?g|webp|"
        r"avif|gif|svg|ico)(?:\?[^\s'\"<>()\\]*)?",
        re.IGNORECASE)
    new_urls = 0
    for url, body in list(fetched.items()):
        if not isinstance(body, (bytes, bytearray)):
            continue
        # only scan textual content
        ct_path = local_path_by_url.get(url)
        if not ct_path:
            continue
        suffix = ct_path.suffix.lower()
        if suffix not in (".html", ".js", ".json", ".css", ""):
            continue
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            continue
        for m in url_re.finditer(text):
            u = m.group(0)
            if u in seen_assets:
                continue
            ext = u.split("?")[0].rsplit(".", 1)[-1].lower()
            kind = "css" if ext == "css" else "js" if ext == "js" else "asset"
            if enqueue_asset(u, kind):
                new_urls += 1
    print(f"[deep-scan] queued {new_urls} additional assets")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for u in SEED:
        enqueue_page(u)

    # First pass: pages (rewrites HTML and queues assets)
    while page_queue:
        url = page_queue.pop(0)
        local_path_by_url.setdefault(url, local_path_for(url))
        process_page(url)
        time.sleep(0.15)

    def drain_assets():
        while asset_queue:
            url, kind = asset_queue.pop(0)
            if url in fetched:
                continue
            print(f"[{kind:>5}] {url[:120]}")
            body = http_get(url)
            if body is None:
                continue
            fetched[url] = body
            if kind == "css":
                process_css(url, body)
            elif kind == "js":
                process_js(url, body)
            else:
                process_binary(url, body)
            time.sleep(0.05)

    drain_assets()

    # Deep scan inside the fetched HTML/JS to catch dynamically referenced
    # CSS bundles that Wix loads via JS at runtime.
    deep_scan_for_assets()
    drain_assets()

    # Write a tiny index that links to the mirrored homepage
    idx = ROOT / "index.html"
    home = local_path_by_url.get("https://www.phillysteakgyros.com/")
    if home:
        rel = relpath(idx, home)
        idx.write_text(
            f'<!doctype html><meta charset=utf-8><title>Mirror</title>'
            f'<meta http-equiv="refresh" content="0; url={rel}">'
            f'<p>Loading <a href="{rel}">mirrored homepage</a>…</p>',
            encoding="utf-8")

    # Summary
    print("\n--- summary ---")
    print(f"pages:  {len([k for k in fetched if up.urlsplit(k).netloc in ALLOWED_PAGE_HOSTS])}")
    print(f"assets: {len(fetched) - len([k for k in fetched if up.urlsplit(k).netloc in ALLOWED_PAGE_HOSTS])}")
    print(f"errors: {len(errors)}")
    if errors:
        with open(ROOT / "_errors.log", "w") as f:
            for u, e in errors:
                f.write(f"{u}\t{e}\n")
        print(f"  -> see {ROOT / '_errors.log'}")


if __name__ == "__main__":
    main()
