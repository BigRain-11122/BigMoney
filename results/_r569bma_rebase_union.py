# -*- coding: utf-8 -*-
"""r569 rebase pick union: pool_core_samples.jsonl (second collision, r523 live-burn window).

Union = :2: (origin side incl. newer bm-b/bm-c ride lines) + my ride's new
lines (:3: minus :1: set-diff, cherry-pick 3-way base is my parent not a
common ancestor -- r569 v3 law). Append-log semantics, dedupe across sides.
"""
import subprocess

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
PATH = 'results/pool_core_samples.jsonl'

def stage(n):
    return subprocess.check_output(['git', '-C', REPO, 'show', f':{n}:{PATH}'])

ours_raw, theirs_raw, base_raw = stage(2), stage(3), stage(1)

def tolines(raw):
    return [l for l in raw.decode('utf-8').replace('\r\n', '\n').split('\n') if l]

ours, theirs, base = tolines(ours_raw), tolines(theirs_raw), tolines(base_raw)
bset = set(base)
my_new = [l for l in theirs if l not in bset]
print(f'origin-side: {len(ours)} | my new: {len(my_new)}')

hset = set(ours)
append = [l for l in my_new if l not in hset]
print(f'appending {len(append)} (deduped vs origin-side)')

eol = '\r\n' if ours_raw.count(b'\r\n') * 2 > ours_raw.count(b'\n') else '\n'
tail_nl = ours_raw.endswith(b'\n')
out = ours + append
data = eol.join(out) + (eol if tail_nl else '')
with open(REPO + '\\' + PATH.replace('/', '\\'), 'wb') as f:
    f.write(data.encode('utf-8'))
assert set(out) == (set(ours) | set(my_new)), 'zero-loss FAILED'
print('zero-loss PASS: result == origin-side | my-new')
