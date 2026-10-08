# -*- coding: utf-8 -*-
"""r872 bm-a rebase UU resolver -- shared live faces, ts-newer-wins per face
(bigmoney-conflict-resolve canon: regeneration race, not semantic conflict).
Whole-file regeneration: ours = bm-a S6 (09:1x), theirs = bm-c r748 (09:1x)."""
import subprocess, json, re, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

UU = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'],
                    capture_output=True, text=True).stdout.strip().splitlines()
print('UU files:', len(UU))


def parse_sides(text):
    ours, theirs = [], []
    cur = ours
    for line in text.splitlines(keepends=True):
        if line.startswith('<<<<<<<'):
            cur = ours
            continue
        if line.startswith('======='):
            cur = theirs
            continue
        if line.startswith('>>>>>>>'):
            cur = None
            continue
        if cur is not None:
            cur.append(line)
    return ''.join(ours), ''.join(theirs)


def extract_ts(side):
    # JSON: ts / generated / timestamp fields
    try:
        d = json.loads(side)
        for k in ('ts', 'generated', 'timestamp', 'updated'):
            if k in d:
                return str(d[k])
        return None
    except Exception:
        pass
    # md/text: first ISO-like timestamp
    m = re.search(r'20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d', side)
    return m.group(0) if m else None


results = []
for f in UU:
    text = io.open(f, encoding='utf-8', errors='replace', newline='').read()
    ours, theirs = parse_sides(text)
    to, tt = extract_ts(ours), extract_ts(theirs)
    if to is None or tt is None:
        winner = 'ours' if to is not None else ('theirs' if tt is not None else 'ours')
        why = 'ts-missing-one-side'
    else:
        winner = 'ours' if to >= tt else 'theirs'
        why = f'ts {to} vs {tt}'
    content = ours if winner == 'ours' else theirs
    # normalize line endings: keep the file's original convention (LF for git)
    with io.open(f, 'w', encoding='utf-8', newline='') as fh:
        fh.write(content)
    subprocess.run(['git', 'add', f], capture_output=True)
    results.append((f, winner, why))
    print(f'{winner:7s} {f}  ({why})')

print('\nresolved:', len(results), 'files')
