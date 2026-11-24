#!/usr/bin/env python3
"""Check that published HTML asks search engines not to index it."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


class RobotsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.directives = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "meta" and attrs.get("name", "").lower() in {"robots", "googlebot"}:
            self.directives.append({part.strip().lower() for part in attrs.get("content", "").split(",")})


errors = []
pages = 0
for path in ROOT.rglob("*.html"):
    if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
        continue
    parser = RobotsParser()
    parser.feed(path.read_text(encoding="utf-8"))
    pages += 1
    if not parser.directives or any("noindex" not in directive or "index" in directive for directive in parser.directives):
        errors.append(f"{path.relative_to(ROOT)}: missing or conflicting noindex directive")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if re.search(r'^\s*(disallow|sitemap)\s*:\s*\S', robots, re.I | re.M):
    errors.append("robots.txt must not block crawlers or advertise a sitemap")
if (ROOT / "CNAME").read_text(encoding="utf-8").strip() != "panthiarun.com.np":
    errors.append("CNAME does not match the new domain")
for error in errors:
    print("FAIL", error)
print(f"Checked {pages} HTML files; {len(errors)} problem(s)")
sys.exit(bool(errors))
