#!/usr/bin/env python3
"""Check static links under both a custom domain and a GitHub project prefix."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.urls = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'a', 'link', 'script', 'img', 'iframe'}:
            for key in ('href', 'src', 'data-src', 'data-page'):
                if key in attrs:
                    self.urls.append(attrs[key])


class PagesDeployment(unittest.TestCase):
    def test_site_links_stay_within_deployment_and_exist(self):
        files = [ROOT / 'index.html', *ROOT.glob('Psc-preparation/**/*.html'),
                 *ROOT.glob('Psc-preparation/**/*.htm'), *ROOT.glob('Psc-video/**/*.html'),
                 *[ROOT / f for f in ('Timer.html', 'pomodoro.html', 'PrivacyPolicy.html',
                                       'TermsofService.html', 'tools/whatsapp-quiz.html')]]
        for prefix in ('/', '/er.arunpanthi/'):
            for file in files:
                rel = file.relative_to(ROOT)
                document = rel.parent.as_posix() + '/' if rel.name == 'index.html' else rel.as_posix()
                if rel.as_posix() == 'index.html':
                    document = ''
                base = 'https://example.test' + prefix + document
                for ref in References(file).urls:
                    if '$' in ref or ref.startswith(('#', 'data:', 'javascript:', 'mailto:', 'tel:', '//', 'http:', 'https:')):
                        continue
                    resolved = urlsplit(urljoin(base, ref)).path
                    with self.subTest(prefix=prefix, page=str(rel), ref=ref):
                        self.assertTrue(resolved.startswith(prefix), resolved)
                        target = ROOT / unquote(resolved[len(prefix):])
                        self.assertTrue(target.is_file() or (target / 'index.html').is_file(), resolved)

    def test_dynamically_generated_exam_paths(self):
        model = (ROOT / 'Psc-preparation/model-exam-sets/index.html').read_text()
        general = (ROOT / 'Psc-preparation/Mock-Test/General/index.html').read_text()
        hydrology = (ROOT / 'Psc-preparation/Mock-Test/Hydrology/index.html').read_text()
        current = (ROOT / 'Psc-preparation/Current-Affairs/current-affairs.js').read_text()
        self.assertIn('`Set/${i}.html`', model)
        self.assertIn('`Set/${i}.html`', general)
        self.assertIn('const SITE_TEST_PATH = "Test/"', hydrology)
        self.assertIn("var EXAM_URL = 'exam.html?date='", current)


if __name__ == '__main__':
    unittest.main()
