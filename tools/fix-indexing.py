#!/usr/bin/env python3
"""Ensure every HTML file requests no indexing without adding SEO metadata.

Run with --check to report files that need updating instead of changing them.
This is a search-engine instruction, not access control.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r'<meta\b(?=[^>]*\bname\s*=\s*["\'](?:robots|googlebot)["\'])[^>]*>', re.I)
HEAD = re.compile(r'<head(?:\s[^>]*)?>', re.I)
DIRECTIVE = '<meta name="robots" content="noindex, nofollow">'


def main():
    check = '--check' in sys.argv
    changed = 0
    for path in sorted([*ROOT.rglob('*.html'), *ROOT.rglob('*.htm')]):
        if any(part.startswith('.') for part in path.relative_to(ROOT).parts):
            continue
        original = path.read_text(encoding='utf-8')
        tags = list(TAG.finditer(original))
        if len(tags) == 1 and tags[0].group() == DIRECTIVE:
            continue
        text = TAG.sub('', original)
        head = HEAD.search(text)
        if head:
            text = text[:head.end()] + '\n    ' + DIRECTIVE + text[head.end():]
        else:
            text = DIRECTIVE + '\n' + text
        changed += 1
        if check:
            print('Needs noindex:', path.relative_to(ROOT))
        else:
            path.write_text(text, encoding='utf-8')
    print(f'{changed} HTML file(s) would change' if check else f'Updated {changed} HTML file(s)')
    return int(check and changed > 0)


if __name__ == '__main__':
    sys.exit(main())
