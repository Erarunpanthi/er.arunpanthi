#!/usr/bin/env python3
"""Generate an offline-friendly cave/district MCQ page from the supplied list."""
import html
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Psc-preparation/MCQ/caves-data.json'
OUTPUT = ROOT / 'Psc-preparation/MCQ/gufa/index.html'


def nepali(number):
    return str(number).translate(str.maketrans('0123456789', '०१२३४५६७८९'))


def build():
    rows = json.loads(DATA.read_text(encoding='utf-8'))
    districts = sorted({row['district'] for row in rows})
    locations = defaultdict(set)
    for row in rows:
        locations[row['cave']].add(row['district'])
    rng = random.Random(20261124)
    groups = []
    for start in range(0, len(rows), 10):
        cards = []
        for idx, row in enumerate(rows[start:start + 10], start + 1):
            cave, answer = row['cave'], row['district']
            distractors = [district for district in districts if district not in locations[cave]]
            options = rng.sample(distractors, 3) + [answer]
            rng.shuffle(options)
            labels = 'कखगघ'
            option_html = '\n'.join(
                f'            <li>{labels[i]}) {html.escape(value)}</li>'
                for i, value in enumerate(options)
            )
            cards.append(f'''        <article class="question">
          <h3>{nepali(idx)}. सूचीअनुसार {html.escape(cave)} तलका मध्ये कुन जिल्लामा उल्लेख छ?</h3>
          <ol class="options">
{option_html}
          </ol>
          <details class="solution"><summary>उत्तर हेर्नुहोस्</summary>
            <p><strong>सही उत्तर: {labels[options.index(answer)]}) {html.escape(answer)}</strong></p>
            <p>सम्झनुहोस्: {html.escape(cave)} — {html.escape(answer)}।</p>
          </details>
        </article>''')
        end = min(start + 10, len(rows))
        cards_html = '\n'.join(cards)
        groups.append(f'''      <details class="quiz-set"{' open' if start == 0 else ''}>
        <summary>प्रश्न {nepali(start + 1)}–{nepali(end)}</summary>
{cards_html}
      </details>''')
    group_html = '\n'.join(groups)
    return f'''<!DOCTYPE html>
<html lang="ne">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>नेपालका गुफा र जिल्ला — MCQ अभ्यास</title>
  <link rel="stylesheet" href="/css/styles.css?v=20260924">
  <style>
    .cave-quiz {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem 3rem; line-height: 1.7; }}
    .cave-quiz h1 {{ color: #14532d; }}
    .cave-quiz .intro {{ background: #f2f8f3; padding: 1rem 1.25rem; border-radius: 10px; }}
    .quiz-set {{ margin: 1rem 0; border: 1px solid #c9d9ce; border-radius: 10px; overflow: hidden; }}
    .quiz-set > summary {{ cursor: pointer; background: #e5f2e8; color: #14532d; padding: .8rem 1rem; font-weight: 700; }}
    .question {{ margin: 1rem; padding: 1rem; background: white; border: 1px solid #d9e4dc; border-radius: 8px; }}
    .question h3 {{ font-size: 1.05rem; margin: 0 0 .7rem; }}
    .options {{ list-style: none; padding: 0; margin: 0 0 .8rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .4rem; }}
    .solution summary {{ cursor: pointer; color: #176b36; font-weight: 700; }}
    .solution p {{ margin: .5rem 0 0; }}
    summary:focus-visible, a:focus-visible {{ outline: 3px solid #d97706; outline-offset: 3px; }}
  </style>
</head>
<body>
  <div id="navbar"></div>
  <main class="cave-quiz" id="main-content">
    <h1>नेपालका गुफा र जिल्ला: MCQ अभ्यास</h1>
    <div class="intro">
      <p>कुल {nepali(len(rows))} प्रश्न। पहिले विकल्प छान्नुहोस्, त्यसपछि उत्तर खोलेर गुफा र जिल्ला सँगै दोहोर्‍याउनुहोस्।</p>
      <p>यी जोडीहरू उपलब्ध गराइएको सूचीमा आधारित छन्; तथ्य स्वतन्त्र रूपमा प्रमाणित गरिएका छैनन्। उस्तै नामका गुफा फरक जिल्लामा हुन सक्छन्।</p>
      <a href="/Psc-preparation/MCQ/">← सबै MCQ विषय</a>
    </div>
{group_html}
    <p><a href="/Psc-preparation/MCQ/">← सबै MCQ विषय</a></p>
  </main>
  <div id="footer"></div>
  <script src="/js/layout.js?v=20261124" defer></script>
</body>
</html>
'''


def main():
    result = build()
    if '--check' in sys.argv:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != result:
            print('Cave quiz is out of date; run python3 tools/generate-cave-quiz.py')
            return 1
        print('Cave quiz is up to date')
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8')
    print('Generated cave quiz')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
