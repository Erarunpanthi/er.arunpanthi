#!/usr/bin/env python3
"""Check that pages keep the simplified metadata and omit the social section."""
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if attrs.get('id') == 'social-section':
            self.errors.append('social section placeholder')
        if self.in_head:
            name = attrs.get('name', '').lower()
            prop = attrs.get('property', '').lower()
            if tag == 'meta' and (name in {'description', 'keywords', 'author'} or name.startswith('twitter:') or prop.startswith('og:')):
                self.errors.append('extra metadata')
            if tag == 'link' and (attrs.get('rel', '').lower() == 'canonical' or
                                  (attrs.get('rel', '').lower() == 'alternate' and 'hreflang' in attrs)):
                self.errors.append('search link')
            if tag == 'script' and attrs.get('type', '').lower() == 'application/ld+json':
                self.errors.append('structured data')

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False


errors = []
for path in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in path.relative_to(ROOT).parts):
        continue
    page = Page()
    page.feed(path.read_text(encoding='utf-8'))
    errors.extend(f'{path.relative_to(ROOT)}: {error}' for error in page.errors)
if '"social-section"' in (ROOT / 'js/layout.js').read_text(encoding='utf-8'):
    errors.append('shared layout still loads the social section')
for error in errors:
    print('FAIL', error)
print(f'{len(errors)} problem(s)')
sys.exit(bool(errors))
