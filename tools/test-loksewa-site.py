#!/usr/bin/env python3
"""Check the Loksewa landing page, navigation, and retired sections."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = []
        self.refresh = None
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.refresh = attrs.get('content')


class LoksewaSite(unittest.TestCase):
    def test_root_opens_loksewa(self):
        root = Links(ROOT / 'index.html')
        self.assertEqual(root.refresh, '0; url=/Psc-preparation/')
        self.assertIn('/Psc-preparation/', root.links)
        self.assertTrue((ROOT / 'Psc-preparation/index.html').is_file())

    def test_retired_sections_are_removed(self):
        for route in ('Home', 'Resources', 'NEC-license-preparation'):
            with self.subTest(route=route):
                self.assertFalse((ROOT / route).exists())
        for page in ('Home.html', 'resources.html', 'license-preparation.html',
                     'notes.html', 'past-questions.html'):
            with self.subTest(page=page):
                self.assertFalse((ROOT / page).exists())

    def test_landing_and_navigation_links_exist(self):
        for page in ('Psc-preparation/index.html', 'partials/navbar.html'):
            for href in Links(ROOT / page).links:
                if href.startswith(('#', 'http:', 'https:', 'mailto:', 'tel:')):
                    continue
                with self.subTest(page=page, href=href):
                    target = urlsplit(href).path
                    path = ROOT / target.lstrip('/')
                    self.assertTrue(path.is_file() or (path / 'index.html').is_file()
                                    or Path(str(path) + '.html').is_file())


if __name__ == '__main__':
    unittest.main()
