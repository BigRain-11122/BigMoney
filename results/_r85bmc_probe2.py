# -*- coding: utf-8 -*-
"""r85 supplementary probe: autofill_state full delta + CODELY.md 3-way line delta."""
import json, subprocess, difflib

def blob(n, path):
    return subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True).stdout

def lines(b):
    return b.decode('utf-8').split('\n')

# ---- autofill_state full ----
o = json.loads(blob('2', 'results/autofill_state.json'))
t = json.loads(blob('3', 'results/autofill_state.json'))
K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))
ok, tk = {K(r): r for r in o['launches']}, {K(r): r for r in t['launches']}
print('autofill: ours', len(o['launches']), 'theirs', len(t['launches']),
      'union', len(set(ok) | set(tk)), 'overlap', len(set(ok) & set(tk)))
for k in sorted(set(ok) & set(tk)):
    if ok[k] != tk[k]:
        d = {f for f in set(ok[k]) | set(tk[k]) if ok[k].get(f) != tk[k].get(f)}
        print('  SAME-KEY-DIVERGE', k[0], k[1], 'fields:', {f: (ok[k].get(f), tk[k].get(f)) for f in d})
only_o = sorted(set(ok) - set(tk)); only_t = sorted(set(tk) - set(ok))
print('  ours-only keys:', [(k[0], k[1], k[4], k[5]) for k in only_o])
print('  theirs-only keys:', [(k[0], k[1], k[4], k[5]) for k in only_t])
print('  ours last_tick:', {f: o['last_tick'].get(f) for f in ('ts', 'machine', 'action')})
print('  theirs last_tick:', {f: t['last_tick'].get(f) for f in ('ts', 'machine', 'action')})
b1 = blob('1', 'results/autofill_state.json')
print('  base: crlf=%d bytes=%d indent2=%r' % (
    b1.count(b'\r\n'), len(b1), lines(b1)[1][:6] if len(lines(b1)) > 1 else ''))
print('  ours: crlf=%d theirs: crlf=%d' % (
    blob('2', 'results/autofill_state.json').count(b'\r\n'),
    blob('3', 'results/autofill_state.json').count(b'\r\n')))

# ---- CODELY 3-way ----
b, ob, tb = lines(blob('1', 'CODELY.md')), lines(blob('2', 'CODELY.md')), lines(blob('3', 'CODELY.md'))
do = list(difflib.unified_diff(b, ob, lineterm='', n=0))
dt = list(difflib.unified_diff(b, tb, lineterm='', n=0))
print('\nCODELY: base %d lines, ours %d, theirs %d' % (len(b), len(ob), len(tb)))
print('--- base->ours delta (%d hunks) ---' % sum(1 for l in do if l.startswith('@@')))
for l in do:
    if l.startswith(('+', '-')) and not l.startswith(('+++', '---')):
        print(' O', l[:150])
print('--- base->theirs delta (%d hunks) ---' % sum(1 for l in dt if l.startswith('@@')))
for l in dt:
    if l.startswith(('+', '-')) and not l.startswith(('+++', '---')):
        print(' T', l[:150])
