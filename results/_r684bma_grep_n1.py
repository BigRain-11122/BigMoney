"""Locate finalize entry points in scripts/perpetual_faces_n1.py (read-only grep helper, r446 probe-to-file law)."""
import re

src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
pat = re.compile(r'def \w*finalize\w*|def cmd_\w+|finalize|--wave|argv|def main')
for i, line in enumerate(src.splitlines(), 1):
    if pat.search(line) and 'WAVE_CONFIGS' not in line and 'assert' not in line:
        print(i, line.rstrip()[:120])
