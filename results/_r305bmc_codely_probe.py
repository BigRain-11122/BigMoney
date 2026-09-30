# -*- coding: utf-8 -*-
"""Inspect CODELY.md conflict regions (working tree markers) + stage line-diff."""
import subprocess, json, difflib, sys

wt = open('CODELY.md', 'rb').read().decode('utf-8')
lines = wt.splitlines()
regions = []
i = 0
while i < len(lines):
    if lines[i].startswith('<<<<<<<'):
        start = i
        base_i = ours_i = None
        for j in range(i, len(lines)):
            if lines[j].startswith('|||||||'): base_i = j
            if lines[j].startswith('======='): ours_i = j; break
        for j in range(ours_i + 1, len(lines)):
            if lines[j].startswith('>>>>>>>'):
                end = j; break
        regions.append((start, base_i, ours_i, end))
        i = end + 1
    else:
        i += 1
print(json.dumps({'marker_regions': len(regions),
  'eol_crlf': b'\r\n' in open('CODELY.md','rb').read()[:2000],
  'regions_meta': [(a, b, c, d) for a, b, c, d in regions]}))
for (a, b, c, d) in regions:
    print(f'--- region L{a+1}-{d+1} ---')
    print('OURS(HEAD):', '\n'.join(lines[a+1:(b if b else c)])[:600])
    print('THEIRS(r304):', '\n'.join(lines[c+1:d])[:600])
    print()

def blob(stage):
    return subprocess.check_output(['git', 'show', f':{stage}:CODELY.md']).decode('utf-8')
s1, s2, s3 = blob(1), blob(2), blob(3)
L1, L2, L3 = s1.splitlines(), s2.splitlines(), s3.splitlines()
sm = difflib.SequenceMatcher(None, L1, L2, autojunk=False)
only2 = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ('insert', 'replace'):
        only2.extend(L2[j1:j2])
sm2 = difflib.SequenceMatcher(None, L1, L3, autojunk=False)
only3 = []
for tag, i1, i2, j1, j2 in sm2.get_opcodes():
    if tag in ('insert', 'replace'):
        only3.extend(L3[j1:j2])
print(json.dumps({'base_lines': len(L1), 's2_lines': len(L2), 's3_lines': len(L3),
                  'only2_count': len(only2), 'only3_count': len(only3)}, ensure_ascii=False))
print('ONLY2 (origin-side new lines):')
for l in only2: print('  |', l[:160])
print('ONLY3 (r304-side new lines):')
for l in only3: print('  |', l[:160])
