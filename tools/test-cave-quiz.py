#!/usr/bin/env python3
"""Verify cave questions against the supplied data, including repeated names."""
from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Psc-preparation/MCQ/caves-data.json'
PAGE = ROOT / 'Psc-preparation/MCQ/gufa/index.html'


class Questions(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.card = None
        self.capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and attrs.get('class') == 'question':
            self.card = {'question': '', 'options': [], 'answer': ''}
        elif self.card is not None and tag in ('h3', 'li', 'strong'):
            self.capture = tag
            if tag == 'li':
                self.card['options'].append('')

    def handle_endtag(self, tag):
        if tag == 'article' and self.card is not None:
            self.cards.append(self.card)
            self.card = None
        if tag == self.capture:
            self.capture = None

    def handle_data(self, data):
        if self.card is None:
            return
        if self.capture == 'h3':
            self.card['question'] += data
        elif self.capture == 'li':
            self.card['options'][-1] += data
        elif self.capture == 'strong':
            self.card['answer'] += data


class CaveCards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.card = None
        self.capture = None

    def handle_starttag(self, tag, attrs):
        if tag == 'article' and dict(attrs).get('class') == 'cave-card':
            self.card = {'cave': '', 'district': ''}
        elif self.card is not None and tag in ('h3', 'p'):
            self.capture = tag

    def handle_endtag(self, tag):
        if tag == 'article' and self.card is not None:
            self.cards.append(self.card)
            self.card = None
        if tag == self.capture:
            self.capture = None

    def handle_data(self, data):
        if self.card is not None and self.capture:
            key = 'cave' if self.capture == 'h3' else 'district'
            self.card[key] += data


class CaveQuizTest(unittest.TestCase):
    def test_card_view(self):
        rows = json.loads(DATA.read_text(encoding='utf-8'))
        page = PAGE.read_text(encoding='utf-8')
        parser = CaveCards()
        parser.feed(page)
        self.assertEqual(parser.cards, rows)
        self.assertNotIn('सूचीअनुसार', page)
        self.assertNotIn('सम्झनुहोस्:', page)

    def test_questions_and_answers(self):
        rows = json.loads(DATA.read_text(encoding='utf-8'))
        self.assertEqual(len(rows), 105)
        places = defaultdict(set)
        for row in rows:
            places[row['cave']].add(row['district'])
        parser = Questions()
        parser.feed(PAGE.read_text(encoding='utf-8'))
        self.assertEqual(len(parser.cards), len(rows))
        for row, card in zip(rows, parser.cards):
            with self.subTest(cave=row['cave'], district=row['district']):
                self.assertIn(row['cave'], card['question'])
                self.assertEqual(len(card['options']), 4)
                options = [s.split(') ', 1)[1] for s in card['options']]
                self.assertEqual(len(set(options)), 4)
                self.assertEqual(set(options) & places[row['cave']], {row['district']})
                label = 'कखगघ'[options.index(row['district'])]
                self.assertEqual(card['answer'], f"सही उत्तर: {label}) {row['district']}")

    def test_generated_page_and_links(self):
        subprocess.run([sys.executable, str(ROOT / 'tools/generate-cave-quiz.py'), '--check'], check=True)
        for page, link in (('Psc-preparation/index.html', 'MCQ/gufa/'),
                           ('Psc-preparation/MCQ/index.html', 'gufa/')):
            self.assertIn(f'href="{link}"', (ROOT / page).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
