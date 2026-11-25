#!/usr/bin/env python3
"""Build historical office flashcards and MCQs from the office data."""
from collections import defaultdict
from pathlib import Path
import html
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Psc-preparation/MCQ/adda-data.json'
OUTPUT = ROOT / 'Psc-preparation/MCQ/adda/index.html'


def number(value):
    return str(value).translate(str.maketrans('0123456789', '०१२३४५६७८९'))


def build():
    rows = json.loads(DATA.read_text(encoding='utf-8'))
    people = sorted({row['ruler'] for row in rows})
    work = sorted({row['work'] for row in rows if row['work']})
    rng = random.Random(20261125)
    cards = []
    questions = []
    for row in rows:
        office = html.escape(row['office'])
        caveat = f'<p>{html.escape(row["note"])}</p>' if row.get('note') else ''
        source = (f'<a href="{html.escape(row["source"], quote=True)}">स्रोत</a>'
                  if row.get('source') else '')
        job = f'<p>{html.escape(row["work"])}</p>' if row.get('work') else ''
        qualifier = ' (पुष्टि बाँकी)' if row.get('uncertain') else ''
        cards.append(f'<article class="office-card"><h3>{office}</h3>{job}<p>{html.escape(row["ruler"])}{qualifier}</p>{caveat}{source}</article>')
        if not row.get('uncertain'):
            questions.append((f'{row["office"]} कसको पालामा स्थापना भएको हो?', row['ruler'], people))
        if row.get('work'):
            questions.append((f'{row["office"]} को काम के थियो?', row['work'], work))
    question_html = []
    for index, (text, correct, pool) in enumerate(questions, 1):
        options = rng.sample([choice for choice in pool if choice != correct], 3) + [correct]
        rng.shuffle(options)
        labels = 'कखगघ'
        choices = ''.join(f'<li>{labels[i]}) {html.escape(option)}</li>' for i, option in enumerate(options))
        question_html.append(f'''<article class="question">
        <h3>{number(index)}. {html.escape(text)}</h3>
        <ol class="options">{choices}</ol>
        <details><summary>उत्तर हेर्नुहोस्</summary><p><strong>सही उत्तर: {labels[options.index(correct)]}) {html.escape(correct)}</strong></p></details>
      </article>''')
    card_html = '\n        '.join(cards)
    quiz_html = '\n      '.join(question_html)
    return f'''<!DOCTYPE html>
<html lang="ne">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>ऐतिहासिक अड्डा — MCQ अभ्यास</title>
  <link rel="stylesheet" href="../../../css/styles.css?v=20260924">
  <style>
    .office-quiz {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem 3rem; line-height: 1.7; }}
    .office-quiz h1 {{ color: #14532d; }}
    .office-set {{ border: 1px solid #c9d9ce; border-radius: 10px; overflow: hidden; margin: 1rem 0; }}
    .office-set > summary {{ cursor: pointer; background: #e5f2e8; color: #14532d; padding: .8rem 1rem; font-weight: 700; }}
    .office-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 190px), 1fr)); gap: .75rem; padding: 1rem; }}
    .office-card, .question {{ border: 1px solid #d9e4dc; border-radius: 8px; background: white; padding: 1rem; }}
    .office-card h3, .question h3 {{ font-size: 1rem; margin: 0 0 .5rem; }}
    .office-card p {{ margin: .3rem 0; }}
    .question {{ margin: 1rem 0; }}
    .options {{ list-style: none; padding: 0; margin: 0 0 .8rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .4rem; }}
    .question summary {{ cursor: pointer; color: #176b36; font-weight: 700; }}
    summary:focus-visible, a:focus-visible {{ outline: 3px solid #d97706; outline-offset: 3px; }}
  </style>
</head>
<body>
  <div id="navbar"></div>
  <main class="office-quiz" id="main-content">
    <h1>ऐतिहासिक अड्डा र तिनका काम</h1>
    <p><a href="../">← सबै MCQ विषय</a></p>
    <details class="office-set">
      <summary>अड्डा र काम — कार्ड भ्यू</summary>
      <div class="office-grid">
        {card_html}
      </div>
    </details>
    <h2>MCQ अभ्यास</h2>
    <p>केही ऐतिहासिक विवरणहरू थप पुष्टि गर्न बाँकी छन्।</p>
    {quiz_html}
    <p><a href="../">← सबै MCQ विषय</a></p>
  </main>
  <div id="footer"></div>
  <script src="../../../js/layout.js?v=20261125" defer></script>
</body>
</html>
'''


def main():
    page = build()
    if '--check' in sys.argv:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != page:
            print('Office quiz is out of date')
            return 1
        print('Office quiz is up to date')
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding='utf-8')
    print('Generated office quiz')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
