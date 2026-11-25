#!/usr/bin/env python3
"""Verify generated office MCQs and review cards."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Psc-preparation/MCQ/adda-data.json'
PAGE = ROOT / 'Psc-preparation/MCQ/adda/index.html'


class Quiz(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.questions = []
        self.kind = None
        self.capture = None
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and attrs.get('class') in {'office-card', 'question'}:
            self.kind = attrs['class']
            self.current = {'heading': '', 'options': [], 'answer': ''}
        elif self.current is not None and tag in {'h3', 'li', 'strong'}:
            self.capture = tag
            if tag == 'li':
                self.current['options'].append('')

    def handle_data(self, text):
        if self.current is None:
            return
        if self.capture == 'h3':
            self.current['heading'] += text
        elif self.capture == 'li':
            self.current['options'][-1] += text
        elif self.capture == 'strong':
            self.current['answer'] += text

    def handle_endtag(self, tag):
        if tag == 'article' and self.current is not None:
            (self.cards if self.kind == 'office-card' else self.questions).append(self.current)
            self.current = None
            self.kind = None
        if tag == self.capture:
            self.capture = None


class AddaQuizTest(unittest.TestCase):
    def test_questions_and_cards(self):
        rows = json.loads(DATA.read_text(encoding='utf-8'))
        parser = Quiz()
        parser.feed(PAGE.read_text(encoding='utf-8'))
        self.assertEqual(len(rows), 12)
        self.assertEqual([card['heading'] for card in parser.cards], [row['office'] for row in rows])
        expected = []
        for row in rows:
            if not row.get('uncertain'):
                expected.append((row['office'], row['ruler']))
            if row.get('work'):
                expected.append((row['office'], row['work']))
        self.assertEqual(len(parser.questions), len(expected))
        for question, (office, answer) in zip(parser.questions, expected):
            with self.subTest(office=office, answer=answer):
                self.assertIn(office, question['heading'])
                options = [value.split(') ', 1)[1] for value in question['options']]
                self.assertEqual(len(options), 4)
                self.assertEqual(len(set(options)), 4)
                self.assertEqual(Counter(options)[answer], 1)
                self.assertEqual(question['answer'], f"सही उत्तर: {'कखगघ'[options.index(answer)]}) {answer}")
        self.assertIn('पुष्टि बाँकी', PAGE.read_text(encoding='utf-8'))

    def test_generated_and_linked(self):
        subprocess.run([sys.executable, str(ROOT / 'tools/generate-adda-quiz.py'), '--check'], check=True)
        self.assertIn('href="adda/"', (ROOT / 'Psc-preparation/MCQ/index.html').read_text(encoding='utf-8'))
        self.assertIn('href="MCQ/adda/"', (ROOT / 'Psc-preparation/index.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
