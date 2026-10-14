# -*- coding: utf-8 -*-
"""Inspect W242 freeze editor: files touched, writes, wave-number dependent faces."""
import re
src = open('results/_w242bma_freeze_edits.py', encoding='utf-8').read()
lines = src.splitlines()
print('total lines=', len(lines))

print('--- FILE PATHS referenced ---')
for m in sorted(set(re.findall(r"[A-Za-z0-9_/.\\-]+\.(?:py|md|json)", src))):
    print(m)

print('--- WRITE CALLS ---')
for i, l in enumerate(lines):
    if re.search(r"open\(.{0,80}['\"](w|a)", l):
        print(i, l.strip()[:160])

print('--- band literal occurrences ---')
for i, l in enumerate(lines):
    if '549501' in l or '541204' in l:
        print(i, l.strip()[:170])
