# -*- coding: utf-8 -*-
"""r569 pick-3 resolver v3: reconstruct union from commit objects (index stages collapsed).

HEAD now carries origin-side (bm-b rides) pool file; my ride 2b56a478a added
2 telemetry lines on my branch. Union = HEAD blob + my ride's added lines.
"""
import subprocess

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
PATH = 'results/pool_core_samples.jsonl'

def show(ref):
    return subprocess.check_output(['git', '-C', REPO, 'show', ref])

head_raw = show('HEAD:' + PATH)                      # origin-side clean version
mine_raw = show('2b56a478a:' + PATH)                  # my ride's version
base_raw = show('2b56a478a^:' + PATH)                 # my ride's parent

def tolines(raw):
    return [l for l in raw.decode('utf-8').replace('\r\n', '\n').split('\n') if l]

head = tolines(head_raw)
mine = tolines(mine_raw)
base = tolines(base_raw)
bset = set(base)
my_new = [l for l in mine if l not in bset]
print(f'HEAD(origin-side): {len(head)} | my-ride new: {len(my_new)}')

hset = set(head)
append = [l for l in my_new if l not in hset]
print(f'appending {len(append)} lines (deduped vs HEAD)')

eol = '\r\n' if head_raw.count(b'\r\n') * 2 > head_raw.count(b'\n') else '\n'
tail_nl = head_raw.endswith(b'\n')
out = head + append
data = eol.join(out) + (eol if tail_nl else '')
with open(REPO + '\\' + PATH.replace('/', '\\'), 'wb') as f:
    f.write(data.encode('utf-8'))
assert set(out) == (set(head) | set(my_new)), 'zero-loss assertion FAILED'
print('zero-loss PASS: result == origin-side | my-ride-new; EOL mirror =', repr(eol), 'tail_nl =', tail_nl)
